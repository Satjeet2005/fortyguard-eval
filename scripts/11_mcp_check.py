import os, json, requests
from dotenv import load_dotenv

load_dotenv()

BASE = "https://api.fortyguard.com"
KEY = os.getenv("FORTYGUARD_KEY")
H = {"api-key": KEY, "Content-Type": "application/json"}


def credits():
    r = requests.post(
        f"{BASE}/v1/system/fetch-api-key-usage",
        headers=H,
        json={"api_key": KEY},
        timeout=60,
    )
    return r.json()["credit_summary"]["total_remaining_credits"]


print("balance:", credits(), "(expected 989,380 if the failed route was free)")

# 1) Can REST read the heatmap that the MCP created?
r = requests.get(
    f"{BASE}/v1/status/bb5135cd-f6f0-40ef-8a78-2afdd594c3ce", headers=H, timeout=60
)
print("REST read of MCP heatmap:", r.status_code)
if r.ok:
    res = r.json()["data"]["result"]
    feats = res["map_data"]["features"]
    vals = [f["properties"]["average_temperature"] for f in feats]
    print(
        "  tiles:",
        len(feats),
        "unique values:",
        len(set(vals)),
        "min/max:",
        min(vals),
        max(vals),
    )
    print(
        "  extra map_data keys:",
        [k for k in res["map_data"] if k not in ("type", "features")],
    )
else:
    print("  ", r.text[:200])

# 2) The MCP-created route, read via REST
r = requests.get(
    f"{BASE}/v1/status/486e9fd6-d8ac-465f-9ee2-63811ce597da", headers=H, timeout=60
)
print("REST read of MCP route:", r.status_code)
if r.ok:
    d = r.json()["data"]
    print("  status:", d["status"])
    if d["status"] == "Completed":
        fs = d["result"]["result_routing"]["features"]
        print("  routes:", len(fs))
        for f in fs:
            p = f["properties"]
            print(
                "   ",
                p["label"],
                p["distance_km"],
                "km",
                p["duration_min"],
                "min",
                "mean",
                p["thermal"]["mean_c"],
            )

# 3) Does the second usage endpoint exist? A 422 will list the fields it wants.
r = requests.post(
    f"{BASE}/v1/system/fetch-api-key-custom-usage",
    headers=H,
    json={"api_key": KEY},
    timeout=60,
)
print("custom-usage probe:", r.status_code, r.text[:400])
