import uuid
from arcade_client import call, wait_for_job

print("Creating pattern...")
job = call("patterns/create", {
    "requestId": str(uuid.uuid4()),
    "prompt": "Small blue and white block-print florals on natural linen",
})
print("Response:", job)

result = wait_for_job(job["jobId"])
print("Pattern ID:", result["patternId"])