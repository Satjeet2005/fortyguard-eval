import os, time, json, requests

from dotenv import load_dotenv
load_dotenv()
KEY = os.environ["FORTYGUARD_KEY"]  # never hardcode; see .env.example
BASE = "https://api.fortyguard.com"
H = {"api-key": KEY, "Content-Type": "application/json"}

def credits():
    r = requests.post(f"{BASE}/v1/system/fetch-api-key-usage", headers=H, json={"api_key": KEY})
    return r.json()["credit_summary"]["total_remaining_credits"]

poly = {"type": "Polygon", "coordinates": [[[-86.20, 39.76], [-86.19, 39.76],
        [-86.19, 39.77], [-86.20, 39.77], [-86.20, 39.76]]]}
body = {"polygon_aoi": poly,
        "date_time": {"start_date": "2024-07-15", "start_time": "14:00", "filter_type": 1},
        "granularity": 100}

before = credits()
t0 = time.time()
r = requests.post(f"{BASE}/v1/heatmap", headers=H, json=body, timeout=60)
print("submit:", r.status_code, round(time.time() - t0, 2), "s")
print(r.text[:500])

if r.status_code == 200:
    aid = r.json()["data"]["activity_id"]
    polls = 0
    while True:
        time.sleep(4)
        polls += 1
        s = requests.get(f"{BASE}/v1/status/{aid}", headers=H, timeout=60)
        status = s.json().get("data", {}).get("status")
        print(f"poll {polls} ({round(time.time() - t0)}s): {s.status_code} {status}")
        if status in ("Completed", "Failed") or polls > 60:
            break
    with open("baseline_result.json", "w") as f:
        f.write(s.text)
    print("response size (bytes):", len(s.text))
    print("top-level keys:", list(s.json().keys()))
    print("data keys:", list(s.json().get("data", {}).keys()))
    print("credits:", before, "->", credits())