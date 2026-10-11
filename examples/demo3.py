import json
from arcade_client import call

CATEGORY_ID = "d6f27ba1-a68e-41be-909e-c93b24a479d7"

response = call("categories/get", {
    "categoryId": CATEGORY_ID,
    "selections": {},
})

print(json.dumps(response, indent=2))