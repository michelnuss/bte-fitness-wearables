/**
 * cart.js — Cart page: display items, quantity controls, totals,
 *           shipping calculator, proceed to checkout
 */

(function () {
  var cartData = null;

  document.addEventListener("DOMContentLoaded", loadCart);

  async function loadCart() {
    var cart = getCart();
    var container = document.getElementById("cart-container");

    if (!cart.length) {
      container.innerHTML =
        '<div class="cart-empty">' +
          '<h2>Your cart is empty</h2>' +
          '<p>Browse our products and add some items!</p>' +
          '<a href="/" class="btn btn-primary" style="margin-top:1rem;">Shop Now</a>' +
        '</div>';
      return;
    }

    try {
      cartData = await apiPost("/api/cart", { items: cart });
      renderCart(cartData);
    } catch (err) {
      container.innerHTML = '<p class="alert alert-error">Failed to load cart.</p>';
    }
  }

  function renderCart(data) {
    var container = document.getElementById("cart-container");

    var rows = data.items.map(function (item) {
      return (
        '<tr>' +
          '<td><span class="cart-item-name">' + item.name + '</span></td>' +
          '<td>' + fmtPrice(item.price) + '</td>' +
          '<td>' +
            '<div class="qty-control">' +
              '<button data-id="' + item.product_id + '" data-delta="-1" class="qty-btn">&minus;</button>' +
              '<input type="number" value="' + item.quantity + '" min="1" max="20" data-id="' + item.product_id + '" class="qty-field">' +
              '<button data-id="' + item.product_id + '" data-delta="1" class="qty-btn">+</button>' +
            '</div>' +
          '</td>' +
          '<td>' + fmtPrice(item.line_total) + '</td>' +
          '<td><button class="btn btn-danger btn-sm remove-btn" data-id="' + item.product_id + '">Remove</button></td>' +
        '</tr>'
      );
    }).join("");

    container.innerHTML =
      '<table class="cart-table">' +
        '<thead><tr>' +
          '<th>Product</th><th>Price</th><th>Qty</th><th>Total</th><th></th>' +
        '</tr></thead>' +
        '<tbody>' + rows + '</tbody>' +
      '</table>' +
      '<div class="cart-summary">' +
        '<h3>Cart Total</h3>' +
        '<div class="cart-summary-row"><span>Subtotal</span><span>' + fmtPrice(data.subtotal) + '</span></div>' +
        '<div class="cart-summary-row"><span>Weight</span><span>' + data.total_weight_oz + ' oz</span></div>' +
        '<div class="cart-summary-row total"><span>Subtotal</span><span>' + fmtPrice(data.subtotal) + '</span></div>' +
        '<div style="margin-top:1rem;">' +
          '<h3 style="font-size:1rem;margin-bottom:.5rem;">Estimate Shipping</h3>' +
          '<div style="display:flex;gap:.5rem;">' +
            '<input type="text" id="cart-ship-zip" placeholder="Zip code" maxlength="5" style="flex:1;padding:.5rem .75rem;border:1.5px solid var(--clr-border);border-radius:6px;font-size:.9rem;">' +
            '<button class="btn btn-outline btn-sm" id="cart-calc-ship">Calculate</button>' +
          '</div>' +
          '<div id="cart-shipping-result" style="margin-top:.75rem;"></div>' +
        '</div>' +
        '<a href="/checkout.html" class="btn btn-accent btn-lg" style="width:100%;margin-top:1rem;text-align:center;">Proceed to Checkout</a>' +
      '</div>';

    // Shipping calculator
    container.querySelector("#cart-calc-ship").addEventListener("click", calcShipping);

    // Quantity +/- buttons
    container.querySelectorAll(".qty-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var id = parseInt(btn.dataset.id, 10);
        var delta = parseInt(btn.dataset.delta, 10);
        var cart = getCart();
        var item = cart.find(function (i) { return i.product_id === id; });
        if (item) {
          var newQty = item.quantity + delta;
          if (newQty < 1) newQty = 1;
          if (newQty > 20) newQty = 20;
          updateCartQty(id, newQty);
          loadCart();
        }
      });
    });

    // Direct quantity input
    container.querySelectorAll(".qty-field").forEach(function (input) {
      input.addEventListener("change", function () {
        var id = parseInt(input.dataset.id, 10);
        var qty = parseInt(input.value, 10);
        if (isNaN(qty) || qty < 1) qty = 1;
        if (qty > 20) qty = 20;
        updateCartQty(id, qty);
        loadCart();
      });
    });

    // Remove buttons
    container.querySelectorAll(".remove-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        removeFromCart(parseInt(btn.dataset.id, 10));
        showToast("Item removed from cart");
        loadCart();
      });
    });
  }

  async function calcShipping() {
    var zip = document.getElementById("cart-ship-zip").value.trim();
    if (!zip || zip.length < 5) {
      showToast("Enter a valid 5-digit zip code");
      return;
    }

    var resultDiv = document.getElementById("cart-shipping-result");
    resultDiv.innerHTML = '<span class="spinner"></span>';

    try {
      var ship = await apiPost("/api/shipping", {
        zip_code: zip,
        weight_oz: cartData.total_weight_oz,
      });

      resultDiv.innerHTML =
        '<div class="alert alert-info" style="margin-bottom:0;">' +
          '<strong>' + ship.zone + ' zone</strong><br>' +
          'Shipping: ' + fmtPrice(ship.shipping_cost) + '<br>' +
          'Delivery: ' + ship.delivery_window +
        '</div>';
    } catch (err) {
      resultDiv.innerHTML = '<p class="alert alert-error" style="margin-bottom:0;">' + err.message + '</p>';
    }
  }
})();
