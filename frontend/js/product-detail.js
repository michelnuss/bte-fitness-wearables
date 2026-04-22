/**
 * product-detail.js — Fetch single product, render detail view, add-to-cart
 */

(function () {
  document.addEventListener("DOMContentLoaded", async function () {
    var params = new URLSearchParams(window.location.search);
    var id = parseInt(params.get("id"), 10);

    if (!id) {
      document.getElementById("product-container").innerHTML =
        '<p class="alert alert-error">No product ID specified.</p>';
      return;
    }

    try {
      var p = await apiGet("/api/products/" + id);
      document.title = p.name + " — StrikeFitness";
      render(p);
    } catch (err) {
      document.getElementById("product-container").innerHTML =
        '<p class="alert alert-error">Product not found.</p>';
    }
  });

  function render(p) {
    var featuresHtml = (p.features || []).map(function (f) {
      return "<li>" + f + "</li>";
    }).join("");

    document.getElementById("product-container").innerHTML =
      '<div class="product-detail" style="grid-template-columns:1fr;">' +
        '<div class="product-detail-info">' +
          (p.flagship ? '<span class="flagship-badge" style="position:static;display:inline-block;margin-bottom:.75rem;">Flagship Product</span>' : '') +
          '<h1>' + p.name + '</h1>' +
          '<div class="product-detail-category">' + p.category + ' &middot; ' + p.weight_oz + ' oz</div>' +
          '<div class="product-detail-price">' + fmtPrice(p.price) + '</div>' +
          '<p class="product-detail-description">' + p.long_description + '</p>' +
          '<ul class="product-features">' + featuresHtml + '</ul>' +
          '<div class="add-to-cart-row">' +
            '<div class="qty-control">' +
              '<button id="qty-minus" type="button">&minus;</button>' +
              '<input type="number" id="qty-input" value="1" min="1" max="20">' +
              '<button id="qty-plus" type="button">+</button>' +
            '</div>' +
            '<button class="btn btn-accent" id="add-to-cart-btn">Add to Cart</button>' +
          '</div>' +
        '</div>' +
      '</div>';

    var qtyInput = document.getElementById("qty-input");
    document.getElementById("qty-minus").addEventListener("click", function () {
      var v = parseInt(qtyInput.value, 10);
      if (v > 1) qtyInput.value = v - 1;
    });
    document.getElementById("qty-plus").addEventListener("click", function () {
      var v = parseInt(qtyInput.value, 10);
      if (v < 20) qtyInput.value = v + 1;
    });

    document.getElementById("add-to-cart-btn").addEventListener("click", function () {
      var qty = parseInt(qtyInput.value, 10) || 1;
      addToCart(p.id, qty);
      showToast(p.name + " added to cart!");
    });
  }
})();
