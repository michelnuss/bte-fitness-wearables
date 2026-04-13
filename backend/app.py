"""
BTE Fitness Wearables — FastAPI Backend

Serves the product catalog API and the frontend static files.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Load .env file (local dev). On Azure, use App Service environment variables.
load_dotenv(Path(__file__).parent / ".env")

# ---------------------------------------------------------------------------
# Load product catalog once at startup
# ---------------------------------------------------------------------------
PRODUCTS_PATH = Path(__file__).parent / "products.json"
with open(PRODUCTS_PATH, "r") as f:
    PRODUCTS: list[dict] = json.load(f)

PRODUCTS_BY_ID: dict[int, dict] = {p["id"]: p for p in PRODUCTS}

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="BTE Fitness Wearables API")

# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------


@app.get("/api/products")
def list_products():
    """Return every product (summary fields only)."""
    summary_fields = ["id", "name", "price", "short_description", "category", "flagship"]
    return [
        {**{k: p[k] for k in summary_fields}, "image_url": p.get("image_url", "")}
        for p in PRODUCTS
    ]


@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    """Return full details for a single product."""
    product = PRODUCTS_BY_ID.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/api/cart")
async def update_cart(request: Request):
    """
    Accept a cart payload and return it validated with computed totals.
    Payload: { "items": [{"product_id": int, "quantity": int}, ...] }
    """
    body = await request.json()
    items = body.get("items", [])
    validated = []
    subtotal = 0.0
    total_weight = 0.0

    for item in items:
        product = PRODUCTS_BY_ID.get(item.get("product_id"))
        if not product:
            continue
        qty = max(1, int(item.get("quantity", 1)))
        line_total = round(product["price"] * qty, 2)
        subtotal += line_total
        total_weight += product["weight_oz"] * qty
        validated.append({
            "product_id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": qty,
            "line_total": line_total,
        })

    return {
        "items": validated,
        "subtotal": round(subtotal, 2),
        "total_weight_oz": round(total_weight, 2),
    }


@app.post("/api/shipping")
async def estimate_shipping(request: Request):
    """
    Estimate shipping cost and delivery window.
    Payload: { "zip_code": str, "weight_oz": float }
    """
    body = await request.json()
    zip_code = str(body.get("zip_code", "")).strip()
    weight_oz = float(body.get("weight_oz", 0))

    if not zip_code or len(zip_code) < 5:
        raise HTTPException(status_code=400, detail="Valid 5-digit zip code required")

    # Zone mapping based on first digit of zip code
    first_digit = int(zip_code[0])
    # Zones: 0-1 = Northeast, 2-3 = Southeast, 4-5 = Midwest, 6-7 = Central, 8-9 = West
    zone_names = {
        0: "Northeast", 1: "Northeast",
        2: "Southeast", 3: "Southeast",
        4: "Midwest",   5: "Midwest",
        6: "Central",   7: "Central",
        8: "West",      9: "West",
    }
    zone = zone_names[first_digit]

    # Base rate by zone (simulated distance from East-coast warehouse)
    zone_base = {
        "Northeast": 4.99,
        "Southeast": 5.99,
        "Midwest": 6.99,
        "Central": 7.99,
        "West": 8.99,
    }
    base = zone_base[zone]

    # Weight surcharge: $1.50 per additional pound beyond the first pound
    weight_lbs = weight_oz / 16.0
    weight_surcharge = max(0, (weight_lbs - 1)) * 1.50

    shipping_cost = round(base + weight_surcharge, 2)

    # Delivery window by zone
    zone_days = {
        "Northeast": (2, 4),
        "Southeast": (3, 5),
        "Midwest": (4, 6),
        "Central": (5, 7),
        "West": (5, 8),
    }
    min_days, max_days = zone_days[zone]

    return {
        "zip_code": zip_code,
        "zone": zone,
        "weight_oz": weight_oz,
        "shipping_cost": shipping_cost,
        "delivery_window": f"{min_days}–{max_days} business days",
    }


@app.post("/api/price-estimate")
async def price_estimate(request: Request):
    """
    Apply discount rules and tax to a cart.
    Payload: { "subtotal": float, "zip_code": str }
    """
    body = await request.json()
    subtotal = float(body.get("subtotal", 0))
    zip_code = str(body.get("zip_code", "")).strip()

    # Discount tiers
    if subtotal >= 500:
        discount_pct = 15
    elif subtotal >= 250:
        discount_pct = 10
    elif subtotal >= 100:
        discount_pct = 5
    else:
        discount_pct = 0

    discount_amount = round(subtotal * discount_pct / 100, 2)
    after_discount = round(subtotal - discount_amount, 2)

    # Simulated state tax rates by first digit of zip
    tax_rates = {
        0: 6.25, 1: 6.35, 2: 6.00, 3: 7.00,
        4: 6.50, 5: 6.75, 6: 8.25, 7: 6.25,
        8: 5.60, 9: 7.25,
    }
    first_digit = int(zip_code[0]) if zip_code and zip_code[0].isdigit() else 0
    tax_rate = tax_rates.get(first_digit, 6.00)
    tax_amount = round(after_discount * tax_rate / 100, 2)

    total = round(after_discount + tax_amount, 2)

    return {
        "subtotal": subtotal,
        "discount_pct": discount_pct,
        "discount_amount": discount_amount,
        "after_discount": after_discount,
        "tax_rate": tax_rate,
        "tax_amount": tax_amount,
        "total": total,
    }


@app.post("/api/checkout")
async def checkout(request: Request):
    """
    Process a checkout (simulated — no real payment).
    Payload: {
        "items": [{"product_id": int, "quantity": int}, ...],
        "shipping": {"zip_code": str},
        "customer": {"name": str, "email": str}
    }
    """
    body = await request.json()
    items = body.get("items", [])
    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    customer = body.get("customer", {})
    if not customer.get("name") or not customer.get("email"):
        raise HTTPException(status_code=400, detail="Customer name and email required")

    # Build order summary
    order_items = []
    subtotal = 0.0
    for item in items:
        product = PRODUCTS_BY_ID.get(item.get("product_id"))
        if not product:
            continue
        qty = max(1, int(item.get("quantity", 1)))
        line_total = round(product["price"] * qty, 2)
        subtotal += line_total
        order_items.append({
            "product_id": product["id"],
            "name": product["name"],
            "quantity": qty,
            "line_total": line_total,
        })

    import uuid
    order_id = str(uuid.uuid4())[:8].upper()

    return {
        "order_id": order_id,
        "status": "confirmed",
        "message": f"Thank you, {customer['name']}! Your order {order_id} has been placed.",
        "items": order_items,
        "subtotal": round(subtotal, 2),
    }


# ---------------------------------------------------------------------------
# AI Chat endpoint — Azure AI Foundry Agent with Entra ID auth
# ---------------------------------------------------------------------------

import re
import time

import requests as http_client
from azure.identity import DefaultAzureCredential

_credential = DefaultAzureCredential()
_AI_SCOPE = "https://ai.azure.com/.default"
_API_VERSION = "2025-05-15-preview"


def _get_bearer_token() -> str:
    return _credential.get_token(_AI_SCOPE).token


@app.post("/api/chat")
async def chat(request: Request):
    """
    Proxy chat messages to the Azure AI Foundry Agent.
    Uses Azure Entra ID auth (az login locally, managed identity in prod).
    Payload: { "message": str, "thread_id": str (optional) }
    """
    body = await request.json()
    user_message = body.get("message", "").strip()
    thread_id = body.get("thread_id", None)

    if not user_message:
        raise HTTPException(status_code=400, detail="Message is required")

    endpoint = os.getenv("AZURE_AI_ENDPOINT", "").rstrip("/")
    agent_id = os.getenv("AZURE_AGENT_ID", "")

    if not endpoint or not agent_id:
        raise HTTPException(status_code=500, detail="AI agent not configured")

    token = _get_bearer_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    def do_request(method, path, data=None):
        url = f"{endpoint}{path}?api-version={_API_VERSION}"
        resp = http_client.request(method, url, headers=headers, json=data, timeout=60)
        if not resp.ok:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Azure API error ({resp.status_code}): {resp.text}",
            )
        return resp.json()

    try:
        # Create or reuse thread
        if not thread_id:
            t = do_request("POST", "/threads", {})
            thread_id = t["id"]

        # Add user message
        do_request("POST", f"/threads/{thread_id}/messages", {
            "role": "user",
            "content": user_message,
        })

        # Run the agent
        run = do_request("POST", f"/threads/{thread_id}/runs", {
            "assistant_id": agent_id,
        })
        run_id = run["id"]

        # Poll until complete
        run_status = {}
        for _ in range(30):
            time.sleep(2)
            run_status = do_request("GET", f"/threads/{thread_id}/runs/{run_id}")
            if run_status["status"] in ("completed", "failed", "cancelled", "expired"):
                break

        if run_status.get("status") != "completed":
            raise HTTPException(
                status_code=500,
                detail=f"Run status: {run_status.get('status', 'unknown')}",
            )

        # Get latest assistant message
        msgs = do_request("GET", f"/threads/{thread_id}/messages")
        reply = ""
        for msg in msgs.get("data", []):
            if msg["role"] == "assistant":
                for block in msg.get("content", []):
                    if block.get("type") == "text":
                        reply = block["text"]["value"]
                break

        reply = re.sub(r'【.*?】', '', reply).strip()

        return {"reply": reply, "thread_id": thread_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Serve frontend static files (must be mounted LAST so API routes take
# priority over the catch-all static file handler)
# ---------------------------------------------------------------------------
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

# Mount CSS and JS subdirectories
app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")
app.mount("/images", StaticFiles(directory=FRONTEND_DIR / "images"), name="images")


@app.get("/")
def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/{page}.html")
def serve_page(page: str):
    file_path = FRONTEND_DIR / f"{page}.html"
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Page not found")
    return FileResponse(file_path)
