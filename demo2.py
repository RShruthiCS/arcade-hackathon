from arcade_client import call

response = call("categories/list", {})

for item in response["items"]:
    print(item["name"], "|", item["world"], "|", item["categoryId"])