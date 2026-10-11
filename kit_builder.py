import math
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from arcade_client import call, wait_for_job

PATTERN_W = PATTERN_H = 1024   # size of the patterns Arcade makes

# To add a product later, add one line here.
# Quantity rules: "per_guest", "per_table", or "fixed".
# "set_size" = how many pieces come in one unit (from the product titles).
KIT = [
    {"label": "Napkins",    "category": "Napkins",     "size": "20x20", "per_guest": 1, "set_size": 4},
    {"label": "Tablecloth", "category": "Tablecloths", "size": "60x60", "fixed": 1,     "set_size": 1},
    {"label": "Tea Towels", "category": "Tea Towels",  "size": None,    "fixed": 4,     "set_size": 2},
    # Later, if the crop problem gets solved:
    # ...
]

DEFAULT_STYLE = "elegant, romantic, refined, soft and timeless"


def make_fit(size):
    """Crop for non-square sizes (None for square). Same math that worked for your tea towel."""
    w, h = [float(x) for x in size.split("x")]
    if w == h:
        return None
    scale = min(PATTERN_W / w, PATTERN_H / h)
    cw, ch = int(w * scale), int(h * scale)
    return {
        "mode": "crop",
        "zoomLevel": 1,
        "crop": {
            "left": (PATTERN_W - cw) // 2,
            "top": (PATTERN_H - ch) // 2,
            "width": cw,
            "height": ch,
        },
    }


def make_pattern(theme, style=DEFAULT_STYLE):
    prompt = f"{theme}, {style}, seamless repeating pattern"
    job = call("patterns/create", {"requestId": str(uuid.uuid4()), "prompt": prompt})
    pattern_id = wait_for_job(job["jobId"])["patternId"]
    pattern = call("patterns/get", {"patternId": pattern_id})
    return pattern_id, pattern["imageUrl"]


def make_product(pattern_id, item, categories):
    """Build one product. Returns a dict, with an 'error' key if it failed."""
    try:
        cat = next(c for c in categories if c["name"] == item["category"])
        requested = {"size": item["size"]} if item["size"] else {}
        info = call("categories/get", {
            "categoryId": cat["categoryId"],
            "selections": requested,
        })
        if not info["canManufacture"]:
            return {"item": item, "error": "These options can't be made together."}

        body = {
            "requestId": str(uuid.uuid4()),
            "patternId": pattern_id,
            "categoryId": cat["categoryId"],
            "selections": info["selections"],
        }
        fit = make_fit(info["selections"]["size"])
        if fit:
            body["fit"] = fit

        job = call("products/create", body)
        product_id = wait_for_job(job["jobId"])["productId"]
        product = call("products/get", {"productId": product_id})
        return {
            "item": item,
            "productId": product_id,
            "title": product["title"],
            "options": product["selectionLabel"],
            "imageUrl": product["imageUrl"],
            "unitPrice": float(product["unitPrice"]["amount"]),
        }
    except Exception as e:
        return {"item": item, "error": str(e)}


def quantity_for(item, guests, tables):
    if "per_guest" in item:
        needed = math.ceil(guests * item["per_guest"])
    elif "per_table" in item:
        needed = math.ceil(tables * item["per_table"])
    else:
        needed = item.get("fixed", 1)
    return max(1, math.ceil(needed / item.get("set_size", 1)))


def build_kit(theme, guests, guests_per_table=8, style=DEFAULT_STYLE, on_progress=print):
    start = time.time()
    tables = math.ceil(guests / guests_per_table)

    on_progress("Painting your pattern...")
    pattern_id, pattern_image = make_pattern(theme, style)

    on_progress("Making your napkins, tablecloth and tea towels...")
    categories = call("categories/list", {})["items"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda it: make_product(pattern_id, it, categories), KIT))

    items, lines, total = [], [], 0.0
    for r in results:
        if "error" in r:
            items.append(r)
            continue
        qty = quantity_for(r["item"], guests, tables)
        r["quantity"] = qty
        r["lineTotal"] = round(r["unitPrice"] * qty, 2)
        total += r["lineTotal"]
        lines.append({"productId": r["productId"], "quantity": qty})
        items.append(r)

    on_progress("Building your checkout...")
    checkout_url = None
    if lines:
        checkout = call("checkouts/create", {
            "requestId": str(uuid.uuid4()),
            "lines": lines,
            "dropShip": True,
        })
        checkout_url = checkout["checkoutUrl"]

    return {
        "patternId": pattern_id,
        "patternImage": pattern_image,
        "tables": tables,
        "items": items,
        "total": round(total, 2),
        "checkoutUrl": checkout_url,
        "seconds": round(time.time() - start),
    }

if __name__ == "__main__":
    kit = build_kit("Italian garden, lemons and olive branches", guests=80)
    print("\nPattern:", kit["patternImage"])
    print(f"Tables: {kit['tables']}   Time: {kit['seconds']}s\n")
    for it in kit["items"]:
        if "error" in it:
            print(f"{it['item']['label']}: FAILED - {it['error']}")
        else:
            print(f"{it['title']} | {it['options']} | "
                  f"{it['quantity']} x ${it['unitPrice']} = ${it['lineTotal']}")
            print("   ", it["imageUrl"])
    print(f"\nEstimated total: ${kit['total']}")
    print("Checkout:", kit["checkoutUrl"])