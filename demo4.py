import json
import uuid
from arcade_client import call, wait_for_job

PATTERN_ID="cmv465zlj003pk410f3f18ct8"
CATEGORY_ID="d6f27ba1-a68e-41be-909e-c93b24a479d7"   # Tea Towels

# Your pattern's size in pixels (find this in step 1 below)
PATTERN_W = 1024
PATTERN_H = 1024

# Tea towel shape: 18" x 20" (width : height)
SIZE_W, SIZE_H = 18, 20

options = call("categories/get", {
    "categoryId": CATEGORY_ID,
    "selections": {},
})
if not options["canManufacture"]:
    raise SystemExit("These options can't be made together.")
print("Using selections:", options["selections"])

# Largest crop with the product's shape that fits inside the pattern, centered
scale = min(PATTERN_W / SIZE_W, PATTERN_H / SIZE_H)
crop_w = int(SIZE_W * scale)
crop_h = int(SIZE_H * scale)
left = (PATTERN_W - crop_w) // 2
top = (PATTERN_H - crop_h) // 2

job = call("products/create", {
    "requestId": str(uuid.uuid4()),
    "patternId": PATTERN_ID,
    "categoryId": CATEGORY_ID,
    "selections": options["selections"],
    "fit": {
        "mode": "crop",
        "zoomLevel": 1,
        "crop": {"left": left, "top": top, "width": crop_w, "height": crop_h},
    },
})
print("Response:", job)

result = wait_for_job(job["jobId"])
print(json.dumps(result, indent=2))
print("Product ID:", result["productId"])