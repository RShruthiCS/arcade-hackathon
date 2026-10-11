import json
from arcade_client import call

PRODUCT_ID = "a835027b-0c79-4037-8b65-4c293a95dd93"

product = call("products/get", {"productId": PRODUCT_ID})
print(json.dumps(product, indent=2))