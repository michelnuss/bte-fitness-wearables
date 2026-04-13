/**
 * app.js — Shared utilities for BTE Fitness Wearables
 *
 * Cart is stored in localStorage as an array of {product_id, quantity}.
 */

const API = "";  // same origin — leave blank

// ---------------------------------------------------------------------------
// Cart helpers (localStorage)
// ---------------------------------------------------------------------------

function getCart() {
  try {
    return JSON.parse(localStorage.getItem("bte_cart")) || [];
  } catch {
    return [];
  }
}

function saveCart(cart) {
  localStorage.setItem("bte_cart", JSON.stringify(cart));
  updateCartBadge();
}

function addToCart(productId, qty) {
  const cart = getCart();
  const existing = cart.find(i => i.product_id === productId);
  if (existing) {
    existing.quantity += qty;
  } else {
    cart.push({ product_id: productId, quantity: qty });
  }
  saveCart(cart);
}

function updateCartQty(productId, qty) {
  let cart = getCart();
  if (qty <= 0) {
    cart = cart.filter(i => i.product_id !== productId);
  } else {
    const item = cart.find(i => i.product_id === productId);
    if (item) item.quantity = qty;
  }
  saveCart(cart);
}

function removeFromCart(productId) {
  saveCart(getCart().filter(i => i.product_id !== productId));
}

function clearCart() {
  localStorage.removeItem("bte_cart");
  updateCartBadge();
}

function cartTotalItems() {
  return getCart().reduce((sum, i) => sum + i.quantity, 0);
}

function updateCartBadge() {
  const badge = document.getElementById("cart-count");
  if (badge) badge.textContent = cartTotalItems();
}

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------

async function apiFetch(path, options) {
  const res = await fetch(API + path, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

function apiGet(path) {
  return apiFetch(path);
}

function apiPost(path, body) {
  return apiFetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

// ---------------------------------------------------------------------------
// Toast notification
// ---------------------------------------------------------------------------

function showToast(message, durationMs) {
  durationMs = durationMs || 2500;
  const el = document.getElementById("toast");
  if (!el) return;
  el.textContent = message;
  el.classList.add("visible");
  setTimeout(function () { el.classList.remove("visible"); }, durationMs);
}

// ---------------------------------------------------------------------------
// Formatting
// ---------------------------------------------------------------------------

function fmtPrice(n) {
  return "$" + Number(n).toFixed(2);
}

// ---------------------------------------------------------------------------
// Init badge on every page
// ---------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", updateCartBadge);
