import json, os, time, urllib.request
import urllib.error
import random

BASE = "https://platform.arcade.ai/v1"

def call(path, body, retries=5):
    for attempt in range(retries):
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
            text = e.read().decode()
            if e.code == 429 and attempt < retries - 1:
                wait = float(e.headers.get("Retry-After", 10)) + random.uniform(0, 3)
                print(f"Rate limited, waiting {wait:.0f}s and retrying...")
                time.sleep(wait)
                continue
            print("HTTP error:", e.code)
            print("Body:", text)
            raise

def wait_for_job(job_id):
    while True:
        job = call("jobs/get", {"jobId": job_id})
        print("  job status:", job["status"])
        if job["status"] == "succeeded":
            return job["result"]
        if job["status"] == "failed":
            raise RuntimeError(job["error"]["message"])
        time.sleep(8)
