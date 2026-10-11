import json
import uuid
from arcade_client import call

PRODUCT_ID = "a835027b-0c79-4037-8b65-4c293a95dd93"

checkout = call("checkouts/create", {
    "requestId": str(uuid.uuid4()),
    "lines": [{"productId": PRODUCT_ID, "quantity": 1}],
    "dropShip": True,
})
print(json.dumps(checkout, indent=2))