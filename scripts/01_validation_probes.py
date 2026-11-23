import os, time, json, requests
from rich import print

from dotenv import load_dotenv
load_dotenv()
KEY = os.environ["FORTYGUARD_KEY"]  # never hardcode; see .env.example
BASE = "https://api.fortyguard.com"
H = {"api-key": KEY, "Content-Type": "application/json"}


def call(label, path, body, headers=H, method="POST"):
    t = time.time()
    r = requests.request(method, BASE + path, headers=headers, json=body, timeout=60)
    dt = round(time.time() - t, 2)
    keep = {
        k: v
        for k, v in r.headers.items()
        if k.lower().startswith(("x-", "retry", "content-type", "server", "www-"))
    }
    rec = {
        "label": label,
        "status": r.status_code,
        "seconds": dt,
        "headers": keep,
        "body": r.text[:1500],
    }
    with open("log.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(
        f"[{label}] {r.status_code} {dt}s {keep.get('content-type')}\n{r.text[:300]}\n"
    )


def credits():
    r = requests.post(
        f"{BASE}/v1/system/fetch-api-key-usage", headers=H, json={"api_key": KEY}
    )
    return r.json()["credit_summary"]["total_remaining_credits"]


poly = {
    "type": "Polygon",
    "coordinates": [
        [
            [-86.20, 39.76],
            [-86.19, 39.76],
            [-86.19, 39.77],
            [-86.20, 39.77],
            [-86.20, 39.76],
        ]
    ],
}
dt_ok = {"start_date": "2024-07-15", "start_time": "14:00", "filter_type": 1}

print("credits before:", credits())

# Does the key check work? (free)
call(
    "bad_key",
    "/v1/heatmap",
    {"polygon_aoi": poly, "date_time": dt_ok},
    headers={"api-key": "wrong", "Content-Type": "application/json"},
)
call(
    "no_key",
    "/v1/heatmap",
    {"polygon_aoi": poly, "date_time": dt_ok},
    headers={"Content-Type": "application/json"},
)

# Reproduce the 500, three times
for i in range(3):
    call(f"no_polygon_{i}", "/v1/heatmap", {"date_time": dt_ok})

# Other malformed inputs
call("empty_body", "/v1/heatmap", {})
call("no_date_time", "/v1/heatmap", {"polygon_aoi": poly})
call(
    "bad_filter_type",
    "/v1/heatmap",
    {"polygon_aoi": poly, "date_time": {**dt_ok, "filter_type": 9}},
)
call("wrong_type", "/v1/heatmap", {"polygon_aoi": "hello", "date_time": dt_ok})

print("credits after:", credits())
