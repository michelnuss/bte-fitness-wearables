"""
Generate a knowledge base text file from products.json.

This file is uploaded to Dialogflow CX or Vertex AI Agent Builder
so the AI agent can answer customer questions about the product catalog.

Usage:
    python generate_knowledge_base.py

Output:
    knowledge_base.txt (in the same directory)
"""

import json
from pathlib import Path

PRODUCTS_PATH = Path(__file__).parent / "products.json"
OUTPUT_PATH = Path(__file__).parent / "knowledge_base.txt"


def generate():
    with open(PRODUCTS_PATH, "r") as f:
        products = json.load(f)

    lines = []
    lines.append("=" * 60)
    lines.append("BTE FITNESS WEARABLES — PRODUCT CATALOG")
    lines.append("=" * 60)
    lines.append("")
    lines.append(
        "BTE Fitness Wearables is an online store selling 18 fitness "
        "wearable products. Our flagship product is the AnkleTrack Pro, "
        "an ankle-worn fitness monitor. We also sell smartwatches, wrist "
        "bands, smart rings, chest straps, clip-on pedometers, smart "
        "insoles, headbands, swim goggles, and more."
    )
    lines.append("")
    lines.append("SHIPPING INFORMATION:")
    lines.append("- Northeast (zip codes starting with 0–1): $4.99 base, 2–4 business days")
    lines.append("- Southeast (zip codes starting with 2–3): $5.99 base, 3–5 business days")
    lines.append("- Midwest (zip codes starting with 4–5): $6.99 base, 4–6 business days")
    lines.append("- Central (zip codes starting with 6–7): $7.99 base, 5–7 business days")
    lines.append("- West (zip codes starting with 8–9): $8.99 base, 5–8 business days")
    lines.append("- A weight surcharge of $1.50 per pound (beyond the first pound) is added.")
    lines.append("")
    lines.append("DISCOUNT TIERS:")
    lines.append("- Orders $100–$249: 5% off")
    lines.append("- Orders $250–$499: 10% off")
    lines.append("- Orders $500+: 15% off")
    lines.append("")
    lines.append("-" * 60)
    lines.append("")

    for p in products:
        lines.append(f"PRODUCT: {p['name']}")
        if p.get("flagship"):
            lines.append("*** FLAGSHIP PRODUCT ***")
        lines.append(f"Category: {p['category']}")
        lines.append(f"Price: ${p['price']:.2f}")
        lines.append(f"Weight: {p['weight_oz']} oz")
        lines.append(f"Summary: {p['short_description']}")
        lines.append(f"Details: {p['long_description']}")
        lines.append("Features: " + ", ".join(p.get("features", [])))
        lines.append("")
        lines.append("-" * 60)
        lines.append("")

    text = "\n".join(lines)

    with open(OUTPUT_PATH, "w") as f:
        f.write(text)

    print(f"Knowledge base generated: {OUTPUT_PATH}")
    print(f"  {len(products)} products, {len(text)} characters")


if __name__ == "__main__":
    generate()
