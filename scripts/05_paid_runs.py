import os, time, json, requests

from dotenv import load_dotenv
load_dotenv()
KEY = os.environ["FORTYGUARD_KEY"]  # never hardcode; see .env.example
BASE = "https://api.fortyguard.com"
H = {"api-key": KEY, "Content-Type": "application/json"}
CAP = 25000

def credits():
    r = requests.post(f"{BASE}/v1/system/fetch-api-key-usage", headers=H, json={"api_key": KEY})
    return r.json()["credit_summary"]["total_remaining_credits"]

START = credits()

def run(label, path, body):
    if START - credits() > CAP:
        raise SystemExit("spending cap reached")
    before = credits()
    t0 = time.time()
    r = requests.post(f"{BASE}{path}", headers=H, json=body, timeout=60)
    print(f"\n[{label}] submit {r.status_code} {round(time.time()-t0,1)}s")
    if r.status_code != 200:
        print(r.text[:400]); return None
    aid = r.json()["data"]["activity_id"]
    polls = 0
    while True:
        time.sleep(4); polls += 1
        s = requests.get(f"{BASE}/v1/status/{aid}", headers=H, timeout=60)
        status = s.json().get("data", {}).get("status")
        if status in ("Completed", "Failed") or polls > 90:
            break
    total = round(time.time() - t0)
    after = credits()
    print(f"  status={status} polls={polls} total={total}s credits {before}->{after} (cost {before-after})")
    with open(f"result_{label}.json", "w") as f:
        f.write(s.text)
    if status != "Completed":
        print("  ", s.text[:500]); return None
    return s.json()["data"]["result"]

poly = {"type": "Polygon", "coordinates": [[[-86.20, 39.76], [-86.19, 39.76],
        [-86.19, 39.77], [-86.20, 39.77], [-86.20, 39.76]]]}
hour = {"start_date": "2024-07-15", "start_time": "14:00", "filter_type": 1}
day = {"start_date": "2024-07-15", "filter_type": 3}

def summarize(res):
    feats = res["map_data"]["features"]
    vals = [f["properties"].get("average_temperature") for f in feats]
    print("  tiles:", len(feats), "unique values:", len(set(vals)),
          "min/max:", min(vals), max(vals))
    print("  stats keys:", list(res["stats_data"].keys()))
    print("  coverage/extra keys:", [k for k in res["map_data"].keys() if k not in ("type", "features")])

# A) finer granularity, same area and hour
a = run("A_tcm_20m", "/v1/heatmap", {"polygon_aoi": poly, "date_time": hour, "granularity": 20})
if a: summarize(a)

# B) time-of-day semantics: 100 m (UTC per docs) vs 20 m (local per docs)
for g in (100, 20):
    b = run(f"B_tom_{g}m", "/v1/heatmap",
            {"polygon_aoi": poly, "date_time": day, "granularity": g, "analytic_type": "time_of_measure"})
    if b:
        vals = [f["properties"].get("average_temperature") for f in b["map_data"]["features"]]
        print(f"  {g} m: unique clock-hour values:", sorted(set(vals)))
        print("  stats units:", b["stats_data"].get("units"))

# C) env_params, chained from the baseline temperature
c = run("C_env", "/v1/env_params",
        {"latitude": 39.765, "longitude": -86.195, "temperature": 35.17, "date_time": hour,
         "analysis": ["heat_index_celsius", "wet_bulb_temperature_celsius", "relative_humidity_percent"]})
if c: print("  env result keys:", list(c.keys()) if isinstance(c, dict) else type(c))

# D) one short route
d = run("D_route", "/v1/routing",
        {"origin": {"lat": 39.7684, "lon": -86.1581}, "destination": {"lat": 39.9784, "lon": -86.118},
         "departure_time": "2024-07-15T14:00:00Z"})
if d: print("  route result keys:", list(d.keys()) if isinstance(d, dict) else type(d))