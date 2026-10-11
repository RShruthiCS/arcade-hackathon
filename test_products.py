from math import gcd
import json
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from arcade_client import call, wait_for_job

# This pattern already worked for your tea towel
PATTERN_ID = "cmv465zlj003pk410f3f18ct8"
PATTERN_W = PATTERN_H = 1024

# (category name, size to request; None = default)
TESTS = [
    ("Napkins", None),
    ("Tablecloths", "60x60"),
    ("Tablecloths", "70x108"),
    #("Table Runners", None),
    #("Placemats", None),
    ("Tea Towels", None),]

cats = call("categories/list", {})["items"]



def make_fit(size):
    """Return a fit dict with an exact-ratio crop, or None for square sizes."""
    # x10 so sizes like 17.5x30 become whole numbers
    w, h = [round(float(x) * 10) for x in size.split("x")]
    if w == h:
        return None
    g = gcd(w, h)
    a, b = w // g, h // g                      # reduced ratio, e.g. 3:20
    k = min(PATTERN_W // a, PATTERN_H // b)    # biggest multiple that fits
    cw, ch = a * k, b * k
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

def make_one(test):
    name, size = test
    start = time.time()
    try:
        cat = next(c for c in cats if c["name"] == name)
        requested = {"size": size} if size else {}
        info = call("categories/get", {
            "categoryId": cat["categoryId"],
            "selections": requested,
        })
        if not info["canManufacture"]:
            return test, "CANNOT MANUFACTURE", None

        body = {
            "requestId": str(uuid.uuid4()),
            "patternId": PATTERN_ID,
            "categoryId": cat["categoryId"],
            "selections": info["selections"],
        }
        fit = make_fit(info["selections"]["size"])
        print(name, info["selections"]["size"], "fit:", fit)
        if fit:
            body["fit"] = fit

        job = call("products/create", body)
        product_id = wait_for_job(job["jobId"])["productId"]
        product = call("products/get", {"productId": product_id})
        return test, product, round(time.time() - start)
    except Exception as e:
        return test, f"ERROR: {e}", None


with ThreadPoolExecutor(max_workers=5) as pool:
    results = list(pool.map(make_one, TESTS))

print("\n" + "=" * 50)
for test, product, seconds in results:
    print(test)
    if isinstance(product, str):
        print("  ", product)
    else:
        print("   title:", product["title"])
        print("   options:", product["selectionLabel"])
        print("   price:", product["unitPrice"]["amount"], product["unitPrice"]["currency"])
        print("   image:", product["imageUrl"])
        print("   seconds:", seconds)