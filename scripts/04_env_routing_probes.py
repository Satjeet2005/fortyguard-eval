import os, time, json, requests

from dotenv import load_dotenv
load_dotenv()
KEY = os.environ["FORTYGUARD_KEY"]  # never hardcode; see .env.example
BASE = "https://api.fortyguard.com"
H = {"api-key": KEY, "Content-Type": "application/json"}


def credits():
    r = requests.post(
        f"{BASE}/v1/system/fetch-api-key-usage", headers=H, json={"api_key": KEY}
    )
    return r.json()["credit_summary"]["total_remaining_credits"]


def call(label, method, path, body=None, headers=H):
    start = credits()
    t = time.time()
    r = requests.request(method, BASE + path, headers=headers, json=body, timeout=60)
    dt = round(time.time() - t, 2)
    keep = {
        k: v
        for k, v in r.headers.items()
        if k.lower().startswith(("x-", "content-type", "retry"))
    }
    with open("log3.jsonl", "a") as f:
        f.write(
            json.dumps(
                {
                    "label": label,
                    "status": r.status_code,
                    "seconds": dt,
                    "headers": keep,
                    "body": r.text[:1500],
                }
            )
            + "\n"
        )
    print(f"[{label}] {r.status_code} {keep.get('content-type')}\n{r.text[:240]}\n")
    end = credits()
    if end < start:
        print(f"!!! credits dropped {start - end} after '{label}'. Stopping.")
        raise SystemExit


# env_params: does the same date_time bug exist here?
base_env = {"latitude": 39.765, "longitude": -86.195, "temperature": 35.0}
call(
    "env_type1_no_start_time",
    "POST",
    "/v1/env_params",
    {**base_env, "date_time": {"start_date": "2024-07-15", "filter_type": 1}},
)
call(
    "env_bad_date_format",
    "POST",
    "/v1/env_params",
    {**base_env, "date_time": {"start_date": "15/07/2024", "filter_type": 3}},
)
call(
    "env_bad_analysis",
    "POST",
    "/v1/env_params",
    {
        **base_env,
        "date_time": {"start_date": "2024-07-15", "filter_type": 3},
        "analysis": ["foo"],
    },
)
call(
    "env_bad_latitude",
    "POST",
    "/v1/env_params",
    {
        **base_env,
        "latitude": 95,
        "date_time": {"start_date": "2024-07-15", "filter_type": 3},
    },
)

# routing: documented limits
call(
    "route_bad_lat",
    "POST",
    "/v1/routing",
    {
        "origin": {"lat": 95, "lon": -86.2},
        "destination": {"lat": 39.8, "lon": -86.1},
        "departure_time": "2024-07-15T14:00:00Z",
    },
)
call(
    "route_over_200km",
    "POST",
    "/v1/routing",
    {
        "origin": {"lat": 39.76, "lon": -86.16},
        "destination": {"lat": 41.88, "lon": -87.63},
        "departure_time": "2024-07-15T14:00:00Z",
    },
)
call(
    "route_bad_time",
    "POST",
    "/v1/routing",
    {
        "origin": {"lat": 39.76, "lon": -86.16},
        "destination": {"lat": 39.8, "lon": -86.1},
        "departure_time": "tomorrow",
    },
)

# status endpoint
call("status_random_id", "GET", "/v1/status/00000000-0000-0000-0000-000000000000")
call("status_malformed_id", "GET", "/v1/status/not-an-id")
call(
    "status_no_key",
    "GET",
    "/v1/status/00000000-0000-0000-0000-000000000000",
    headers={"Content-Type": "application/json"},
)
