import json, os, time, urllib.request
import urllib.error

BASE = "https://platform.arcade.ai/v1"

def call(path, body):
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
            return json.load(r)
    except urllib.error.HTTPError as e:
        print("HTTP error:", e.code)
        print("Body:", e.read().decode())
        raise

def wait_for_job(job_id):
    while True:
        job = call("jobs/get", {"jobId": job_id})
        print("  job status:", job["status"])
        if job["status"] == "succeeded":
            return job["result"]
        if job["status"] == "failed":
            raise RuntimeError(job["error"]["message"])
        time.sleep(5)