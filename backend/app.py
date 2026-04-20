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
# AI Chat — Google Gemini via google-genai (API key in env; knowledge_base.txt)
# ---------------------------------------------------------------------------

import re
import time
import uuid
from collections import OrderedDict

from google import genai
from google.genai import types

_BACKEND_ROOT = Path(__file__).parent
_KNOWLEDGE_PATH = _BACKEND_ROOT / "knowledge_base.txt"
_RAG_STRUCTURED = _BACKEND_ROOT / "rag_data" / "structured"
_RAG_UNSTRUCTURED = _BACKEND_ROOT / "rag_data" / "unstructured"
_RAG_WEBSITE = _BACKEND_ROOT / "rag_data" / "website"

try:
    with open(_KNOWLEDGE_PATH, encoding="utf-8") as _kf:
        _KNOWLEDGE_TEXT = _kf.read()
except OSError:
    _KNOWLEDGE_TEXT = ""

_MAX_SESSIONS = 200
_gemini_client: genai.Client | None = None
_CHATS: OrderedDict[str, object] = OrderedDict()


def _load_structured_rag() -> str:
    """JSON / tabular store facts: contact, location, services."""
    chunks: list[str] = []
    if not _RAG_STRUCTURED.is_dir():
        return ""
    for path in sorted(_RAG_STRUCTURED.glob("*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)
            chunks.append(f"=== STRUCTURED ({path.name}) ===\n{json.dumps(raw, indent=2)}")
        except (OSError, json.JSONDecodeError):
            continue
    return "\n\n".join(chunks)


def _load_text_dir(label: str, directory: Path, patterns: tuple[str, ...]) -> str:
    """Load all matching text files from a directory (unstructured or website snapshots)."""
    if not directory.is_dir():
        return ""
    parts: list[str] = []
    for pattern in patterns:
        for path in sorted(directory.glob(pattern)):
            try:
                text = path.read_text(encoding="utf-8")
                parts.append(f"=== {label}: {path.name} ===\n{text.strip()}")
            except OSError:
                continue
    return "\n\n".join(parts)


def _build_system_instruction() -> str:
    intro = (
        "You are a customer assistant for BTE Fitness Wearables. "
        "Answer only using the retrieved knowledge sections below (catalog, structured store data, "
        "unstructured policies/FAQ, and website snapshots). "
        "Rules: (1) For product names, prices, 'most expensive', 'cheapest', and catalog counts, "
        "trust the section 'PRODUCT CATALOG & PRICING' first — especially the PRICING NOTE line "
        "and each PRODUCT block's Price: field. (2) For contact, HQ, shipping zones, hours, and "
        "returns, combine catalog shipping/discount text with STRUCTURED DATA and UNSTRUCTURED FAQ. "
        "(3) Do not invent SKUs, prices, or policies. "
        "If something is not in the knowledge, say you do not have that information. "
        "If the user asks about topics unrelated to BTE Fitness, say: "
        "'I can only help with questions about BTE Fitness Wearables.'\n\n"
    )

    catalog = _KNOWLEDGE_TEXT or "(No catalog loaded.)"
    structured = _load_structured_rag() or "(No structured JSON files.)"
    unstructured = _load_text_dir("UNSTRUCTURED", _RAG_UNSTRUCTURED, ("*.txt", "*.md"))
    website = _load_text_dir("WEBSITE", _RAG_WEBSITE, ("*.md", "*.txt", "*.html"))

    if not unstructured:
        unstructured = "(No unstructured files in rag_data/unstructured/.)"
    if not website:
        website = "(No website snapshots in rag_data/website/.)"

    return (
        f"{intro}"
        f"=== PRODUCT CATALOG & PRICING (generated knowledge_base) ===\n{catalog}\n\n"
        f"=== STRUCTURED DATA (contact, location, services) ===\n{structured}\n\n"
        f"=== UNSTRUCTURED DATA (policies, FAQ, long-form text) ===\n{unstructured}\n\n"
        f"=== WEBSITE DATA (mirrored / exported pages) ===\n{website}"
    )


def _get_gemini_client() -> genai.Client:
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client

    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_API_KEY not configured. See GOOGLE_CLOUD_SETUP.md",
        )

    # Must set vertexai=False when using an AI Studio API key. On Cloud Run / GCP,
    # the default client can pick Application Default Credentials (OAuth) and call
    # generativelanguage with the wrong credential type → 401 ACCESS_TOKEN_TYPE_UNSUPPORTED.
    _gemini_client = genai.Client(api_key=api_key, vertexai=False)
    return _gemini_client


def _chat_config() -> types.GenerateContentConfig:
    return types.GenerateContentConfig(system_instruction=_build_system_instruction())


def _model_chain() -> list[str]:
    primary = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    fallbacks = ["gemini-2.5-flash-lite", "gemini-1.5-flash"]
    chain = [primary] + [m for m in fallbacks if m != primary]
    return chain


def _new_chat(model_name: str):
    return _get_gemini_client().chats.create(model=model_name, config=_chat_config())


def _get_or_create_session(thread_id: str | None):
    if thread_id and thread_id in _CHATS:
        _CHATS.move_to_end(thread_id)
        return _CHATS[thread_id], thread_id

    new_id = str(uuid.uuid4())
    chat = _new_chat(_model_chain()[0])
    _CHATS[new_id] = chat
    while len(_CHATS) > _MAX_SESSIONS:
        _CHATS.popitem(last=False)
    return chat, new_id


@app.post("/api/chat")
async def chat(request: Request):
    """
    Chat with Gemini using server-side API key and knowledge_base.txt.
    Payload: { "message": str, "thread_id": str (optional) }
    """
    body = await request.json()
    user_message = body.get("message", "").strip()
    thread_id = body.get("thread_id", None)

    if not user_message:
        raise HTTPException(status_code=400, detail="Message is required")

    try:
        session, tid = _get_or_create_session(thread_id)

        response = None
        last_err: Exception | None = None
        models = _model_chain()

        for model_idx, model_name in enumerate(models):
            if model_idx > 0:
                session = _new_chat(model_name)
                _CHATS[tid] = session

            for attempt in range(2):
                try:
                    response = session.send_message(user_message)
                    break
                except Exception as e:
                    last_err = e
                    msg = str(e).lower()
                    transient = (
                        "503" in msg
                        or "unavailable" in msg
                        or "overloaded" in msg
                        or "resource_exhausted" in msg
                        or "429" in msg
                    )
                    if transient and attempt == 0:
                        time.sleep(1.5)
                        continue
                    break

            if response is not None:
                break

        if response is None and last_err is not None:
            raise last_err

        reply = ""
        try:
            reply = (getattr(response, "text", None) or "").strip()
        except ValueError:
            reply = "I could not generate a safe reply. Please rephrase your question."

        reply = re.sub(r"【.*?】", "", reply).strip()

        return {"reply": reply, "thread_id": tid}

    except HTTPException:
        raise
    except Exception as e:
        msg = str(e).lower()
        if "503" in msg or "unavailable" in msg or "overloaded" in msg:
            raise HTTPException(
                status_code=503,
                detail="The assistant is temporarily busy. Please try again in a few seconds.",
            )
        if "429" in msg or "resource_exhausted" in msg or "quota" in msg:
            raise HTTPException(
                status_code=429,
                detail="Too many requests right now. Please wait a moment and try again.",
            )
        raise HTTPException(status_code=500, detail="Assistant error. Please try again.")


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
