from arcade_client import call

NAMES = ["Napkins", "Tablecloths", "Table Runners", "Placemats"]

cats = call("categories/list", {})["items"]

for name in NAMES:
    match = [c for c in cats if c["name"] == name]
    if not match:
        print("=" * 40)
        print(f"{name}: NOT FOUND in categories/list")
        continue

    cat = match[0]
    info = call("categories/get", {
        "categoryId": cat["categoryId"],
        "selections": {},
    })

    print("=" * 40)
    print(name)
    print("Category ID:", cat["categoryId"])
    print("Default selections:", info["selections"])
    print("Can manufacture:", info["canManufacture"])

    for opt in info["options"]:
        values = []
        for v in opt["values"]:
            tag = ""
            if v["isDefault"]:
                tag += " (default)"
            if not v["available"]:
                tag += " [unavailable]"
            values.append(f"{v['value']}{tag}")
        print(f"  {opt['label']} ({opt['key']}): {', '.join(values)}")