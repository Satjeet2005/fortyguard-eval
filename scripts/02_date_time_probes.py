import os, time, json, requests
from rich import print

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


def call(label, body):
    start = credits()
    t = time.time()
    r = requests.post(f"{BASE}/v1/heatmap", headers=H, json=body, timeout=60)
    dt = round(time.time() - t, 2)
    keep = {
        k: v
        for k, v in r.headers.items()
        if k.lower().startswith(("x-", "content-type", "server", "retry"))
    }
    with open("log2.jsonl", "a") as f:
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
    print(f"[{label}] {r.status_code} {dt}s\n{r.text[:260]}\n")
    end = credits()
    if end < start:
        print(f"!!! credits dropped {start - end} after '{label}'. Stopping.")
        raise SystemExit
    return r


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
dt = lambda **k: {"start_date": "2024-07-15", **k}

# The hypothesis: conditionally-required fields cause a 500
call("type1_no_start_time", {"polygon_aoi": poly, "date_time": dt(filter_type=1)})
call(
    "type2_no_end_time",
    {"polygon_aoi": poly, "date_time": dt(filter_type=2, start_time="10:00")},
)
call("type4_no_end_date", {"polygon_aoi": poly, "date_time": dt(filter_type=4)})
call(
    "end_before_start",
    {"polygon_aoi": poly, "date_time": dt(filter_type=4, end_date="2024-07-01")},
)
call(
    "range_over_1_month",
    {"polygon_aoi": poly, "date_time": dt(filter_type=4, end_date="2024-09-30")},
)
call(
    "bad_date_format",
    {"polygon_aoi": poly, "date_time": {"start_date": "15/07/2024", "filter_type": 3}},
)
call(
    "bad_time_format",
    {"polygon_aoi": poly, "date_time": dt(filter_type=1, start_time="2pm")},
)
call(
    "bad_granularity",
    {"polygon_aoi": poly, "date_time": dt(filter_type=3), "granularity": 50},
)
call(
    "bad_analytic",
    {"polygon_aoi": poly, "date_time": dt(filter_type=3), "analytic_type": "foo"},
)
call(
    "bad_direction",
    {
        "polygon_aoi": poly,
        "date_time": dt(filter_type=3),
        "analytic_type": "exceedance",
        "direction": "sideways",
    },
)
call(
    "bad_threshold",
    {
        "polygon_aoi": poly,
        "date_time": dt(filter_type=3),
        "analytic_type": "exceedance",
        "threshold": "hot",
    },
)
call(
    "point_geometry",
    {
        "polygon_aoi": {"type": "Point", "coordinates": [-86.2, 39.76]},
        "date_time": dt(filter_type=3),
    },
)
call(
    "unclosed_ring",
    {
        "polygon_aoi": {
            "type": "Polygon",
            "coordinates": [
                [[-86.20, 39.76], [-86.19, 39.76], [-86.19, 39.77], [-86.20, 39.77]]
            ],
        },
        "date_time": dt(filter_type=3),
    },
)
