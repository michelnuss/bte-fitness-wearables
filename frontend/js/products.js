/**
 * products.js — Homepage: fetch products, render grid, category filter
 */

(function () {
  var allProducts = [];

  document.addEventListener("DOMContentLoaded", async function () {
    try {
      allProducts = await apiGet("/api/products");
      renderFlagship(allProducts);
      buildFilterBar(allProducts);
      renderGrid(allProducts);
    } catch (err) {
      document.getElementById("product-grid").innerHTML =
        '<p class="alert alert-error">Failed to load products. Is the server running?</p>';
    }
  });

  function renderFlagship(products) {
    var flagship = products.find(function (p) { return p.flagship && p.image_url; });
    if (!flagship) return;

    var container = document.getElementById("flagship-hero");
    if (!container) return;

    container.innerHTML =
      '<a href="/product.html?id=' + flagship.id + '" style="text-decoration:none;color:inherit;">' +
        '<div class="flagship-hero-inner">' +
          '<div class="flagship-hero-img">' +
            '<img src="' + flagship.image_url + '" alt="' + flagship.name + '">' +
          '</div>' +
          '<div class="flagship-hero-info">' +
            '<span class="flagship-badge" style="position:static;display:inline-block;margin-bottom:.75rem;">Flagship Product</span>' +
            '<h2>' + flagship.name + '</h2>' +
            '<p>' + flagship.short_description + '</p>' +
            '<div style="margin-top:1.25rem;display:flex;align-items:center;gap:1rem;">' +
              '<span style="font-size:1.6rem;font-weight:700;color:var(--clr-primary);">' + fmtPrice(flagship.price) + '</span>' +
              '<span class="btn btn-accent">Shop Now</span>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</a>';
  }

  function buildFilterBar(products) {
    var categories = [];
    products.forEach(function (p) {
      if (categories.indexOf(p.category) === -1) categories.push(p.category);
    });
    var bar = document.getElementById("filter-bar");
    categories.forEach(function (cat) {
      var btn = document.createElement("button");
      btn.className = "btn btn-sm btn-outline filter-btn";
      btn.dataset.category = cat;
      btn.textContent = cat;
      bar.appendChild(btn);
    });

    document.querySelectorAll(".filter-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        document.querySelectorAll(".filter-btn").forEach(function (b) {
          b.classList.remove("btn-primary");
          b.classList.add("btn-outline");
        });
        btn.classList.remove("btn-outline");
        btn.classList.add("btn-primary");

        var cat = btn.dataset.category;
        if (cat === "all") {
          renderGrid(allProducts);
        } else {
          renderGrid(allProducts.filter(function (p) { return p.category === cat; }));
        }
      });
    });
  }

  function renderGrid(products) {
    var grid = document.getElementById("product-grid");
    if (!products.length) {
      grid.innerHTML = '<p style="color:var(--clr-text-light);">No products found.</p>';
      return;
    }
    grid.innerHTML = products.map(function (p) {
      return (
        '<div class="product-card' + (p.flagship ? " flagship" : "") + '">' +
          '<a href="/product.html?id=' + p.id + '" style="text-decoration:none;color:inherit;">' +
            (p.image_url ? '<div class="product-card-img"><img src="' + p.image_url + '" alt="' + p.name + '"></div>' : "") +
            '<div class="product-card-body">' +
              (p.flagship ? '<span class="flagship-badge" style="position:static;display:inline-block;margin-bottom:.5rem;">Flagship</span>' : "") +
              '<div class="product-card-category">' + p.category + '</div>' +
              '<div class="product-card-name">' + p.name + '</div>' +
              '<div class="product-card-desc">' + p.short_description + '</div>' +
              '<div class="product-card-footer">' +
                '<span class="product-card-price">' + fmtPrice(p.price) + '</span>' +
                '<span class="btn btn-sm btn-primary">View Details</span>' +
              '</div>' +
            '</div>' +
          '</a>' +
        '</div>'
      );
    }).join("");
  }
})();
