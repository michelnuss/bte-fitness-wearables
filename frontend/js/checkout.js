/**
 * checkout.js — Checkout page: order summary, shipping calculator,
 *               price estimate with discounts/tax, place order
 */

(function () {
  var cartData = null;
  var shippingCost = 0;
  var priceEstimate = null;

  document.addEventListener("DOMContentLoaded", init);

  async function init() {
    var cart = getCart();
    if (!cart.length) {
      document.getElementById("checkout-container").innerHTML =
        '<div class="cart-empty"><h2>Nothing to check out</h2>' +
        '<p>Your cart is empty.</p>' +
        '<a href="/" class="btn btn-primary" style="margin-top:1rem;">Shop Now</a></div>';
      return;
    }

    try {
      cartData = await apiPost("/api/cart", { items: cart });
      renderOrderItems();
      renderTotals();
    } catch (err) {
      document.getElementById("order-items").innerHTML =
        '<p class="alert alert-error">Failed to load cart data.</p>';
    }

    document.getElementById("calc-shipping-btn").addEventListener("click", calcShipping);
    document.getElementById("place-order-btn").addEventListener("click", placeOrder);
  }

  function renderOrderItems() {
    var html = cartData.items.map(function (item) {
      return (
        '<div class="order-summary-item">' +
          '<span class="item-name">' + item.name + ' &times; ' + item.quantity + '</span>' +
          '<span>' + fmtPrice(item.line_total) + '</span>' +
        '</div>'
      );
    }).join("");
    document.getElementById("order-items").innerHTML = html;
  }

  function renderTotals() {
    var lines = '';
    lines += '<div class="order-line"><span>Subtotal</span><span>' + fmtPrice(cartData.subtotal) + '</span></div>';

    if (priceEstimate) {
      if (priceEstimate.discount_pct > 0) {
        lines += '<div class="order-line discount"><span>Discount (' + priceEstimate.discount_pct + '%)</span><span>-' + fmtPrice(priceEstimate.discount_amount) + '</span></div>';
      }
      lines += '<div class="order-line"><span>Tax (' + priceEstimate.tax_rate + '%)</span><span>' + fmtPrice(priceEstimate.tax_amount) + '</span></div>';
    }

    if (shippingCost > 0) {
      lines += '<div class="order-line"><span>Shipping</span><span>' + fmtPrice(shippingCost) + '</span></div>';
    }

    var grandTotal = priceEstimate ? priceEstimate.total + shippingCost : cartData.subtotal + shippingCost;
    lines += '<div class="order-line total"><span>Total</span><span>' + fmtPrice(grandTotal) + '</span></div>';

    document.getElementById("order-totals").innerHTML = lines;
  }

  async function calcShipping() {
    var zip = document.getElementById("ship-zip").value.trim();
    if (!zip || zip.length < 5) {
      showToast("Enter a valid 5-digit zip code");
      return;
    }

    var resultDiv = document.getElementById("shipping-result");
    resultDiv.innerHTML = '<span class="spinner"></span>';

    try {
      var ship = await apiPost("/api/shipping", {
        zip_code: zip,
        weight_oz: cartData.total_weight_oz,
      });

      shippingCost = ship.shipping_cost;

      resultDiv.innerHTML =
        '<div class="alert alert-info">' +
          '<strong>Shipping to ' + ship.zone + ' (zip ' + ship.zip_code + ')</strong><br>' +
          'Cost: ' + fmtPrice(ship.shipping_cost) + '<br>' +
          'Estimated delivery: ' + ship.delivery_window +
        '</div>';

      // Also fetch price estimate with discount/tax
      priceEstimate = await apiPost("/api/price-estimate", {
        subtotal: cartData.subtotal,
        zip_code: zip,
      });

      renderTotals();
    } catch (err) {
      resultDiv.innerHTML = '<p class="alert alert-error">' + err.message + '</p>';
    }
  }

  async function placeOrder() {
    var name = document.getElementById("cust-name").value.trim();
    var email = document.getElementById("cust-email").value.trim();

    if (!name || !email) {
      showToast("Please enter your name and email");
      return;
    }

    var zip = document.getElementById("ship-zip").value.trim();

    var btn = document.getElementById("place-order-btn");
    btn.disabled = true;
    btn.textContent = "Placing order...";

    try {
      var result = await apiPost("/api/checkout", {
        items: getCart(),
        shipping: { zip_code: zip },
        customer: { name: name, email: email },
      });

      clearCart();

      // Hide form, show confirmation
      document.getElementById("checkout-container").style.display = "none";
      var conf = document.getElementById("order-confirmation");
      conf.style.display = "block";
      conf.innerHTML =
        '<div class="order-confirmation">' +
          '<h2>Order Confirmed!</h2>' +
          '<p class="order-id">Order #' + result.order_id + '</p>' +
          '<p>' + result.message + '</p>' +
          '<a href="/" class="btn btn-primary" style="margin-top:1.5rem;">Continue Shopping</a>' +
        '</div>';
    } catch (err) {
      showToast("Checkout failed: " + err.message);
      btn.disabled = false;
      btn.textContent = "Place Order";
    }
  }
})();
