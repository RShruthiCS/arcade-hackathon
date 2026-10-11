import json, os, urllib.request, urllib.error, uuid

BASE = "https://platform.arcade.ai/v1"
PATTERN_ID = "cmv465zlj003pk410f3f18ct8"

def raw_call(path, body):
    req = urllib.request.Request(
        f"{BASE}/{path}",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {os.environ['ARCADE_API_KEY']}",
            "Content-Type": "application/json",
            "User-Agent": "hackathon-demo/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

def sweep(name, category_id, selections, label_w, label_h):
    label_ratio = label_w / label_h          # both our products are taller than wide
    ch = 1000
    top = (1024 - ch) // 2
    print(f"--- {name} (label ratio {label_ratio:.4f}) ---")
    for pct in range(70, 131):
        cw = round(ch * label_ratio * pct / 100)
        left = (1024 - cw) // 2
        status, resp = raw_call("products/create", {
            "requestId": str(uuid.uuid4()),
            "patternId": PATTERN_ID,
            "categoryId": category_id,
            "selections": selections,
            "fit": {"mode": "crop", "zoomLevel": 1,
                    "crop": {"left": left, "top": top, "width": cw, "height": ch}},
        })
        if status == 200:
            print(f"ACCEPTED at {pct}% -> crop {cw} x {ch} (ratio {cw/ch:.4f})")
            return
        if "ratio" not in str(resp):
            print("Different error:", resp)
            return
    print("No ratio accepted in the range")

sweep("Table Runners", "9aeeb74f-f11a-40c6-afd7-4001f0178d3b",
      {"fabric": "canvas", "size": "18x120"}, 18, 120)
sweep("Placemats", "4504ea0b-93d6-4280-9368-894a6ef4c783",
      {"fabric": "canvas", "size": "14x19", "embellishment": "none"}, 14, 19)