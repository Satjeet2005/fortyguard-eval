import os, time, json, requests
from dotenv import load_dotenv

load_dotenv()

BASE = "https://api.fortyguard.com"
KEY = os.getenv("FORTYGUARD_KEY")
OLD = os.getenv("FORTYGUARD_OLD_KEY")
H = {"api-key": KEY, "Content-Type": "application/json"}
OLD_AID = "b20fc2e9-ffb6-42c7-9289-3d0eea7f9869"   # baseline made with the old key

def req(label, method, path, headers=H, **kw):
    t = time.time()
    try:
        r = requests.request(method, BASE + path, headers=headers, timeout=90, **kw)
    except requests.RequestException as e:
        print(f"[{label}] request failed: {e}"); return None
    keep = {k: v for k, v in r.headers.items()
            if k.lower().startswith(("x-ratelimit", "content-type", "allow", "retry"))}
    with open("log5.jsonl", "a") as f:
        f.write(json.dumps({"label": label, "status": r.status_code, "seconds": round(time.time()-t, 1),
                            "headers": keep, "body": r.text[:600]}) + "\n")
    print(f"[{label}] {r.status_code} {round(time.time()-t,1)}s {keep.get('content-type')} | {r.text[:140]!r}")
    return r

def credits():
    r = req("credits", "POST", "/v1/system/fetch-api-key-usage", json={"api_key": KEY})
    return r.json()["credit_summary"]["total_remaining_credits"] if r is not None and r.status_code == 200 else None

c0 = credits()

# 1) Is an API spec published? (no key)
for p in ("/openapi.json", "/docs", "/redoc"):
    req(f"spec{p}", "GET", p, headers={})

# 2) Can the new key see a result made by the old key? Can the old key?
r = req("refetch_new_key", "GET", f"/v1/status/{OLD_AID}")
if OLD:
    req("refetch_old_key", "GET", f"/v1/status/{OLD_AID}",
        headers={"api-key": OLD, "Content-Type": "application/json"})

# 3) Need a result for the links test: use the old one if visible, else make one (4,220 credits)
aid = OLD_AID if (r is not None and r.status_code == 200) else None
if aid is None:
    poly = {"type": "Polygon", "coordinates": [[[-86.20, 39.76], [-86.19, 39.76],
            [-86.19, 39.77], [-86.20, 39.77], [-86.20, 39.76]]]}
    body = {"polygon_aoi": poly, "granularity": 100,
            "date_time": {"start_date": "2024-07-15", "start_time": "14:00", "filter_type": 1}}
    s = req("submit_baseline", "POST", "/v1/heatmap", json=body)
    if s is not None and s.status_code == 200:
        aid = s.json()["data"]["activity_id"]
        for _ in range(40):
            time.sleep(4)
            st = requests.get(f"{BASE}/v1/status/{aid}", headers=H, timeout=60).json()["data"]["status"]
            if st in ("Completed", "Failed"):
                print("baseline status:", st); break

# 4) Links delivery: do signed URLs work? Is the file double-encoded?
if aid:
    r2 = req("links", "GET", f"/v1/status/{aid}", params={"result_delivery": "links"})
    try:
        res = r2.json()["data"]["result"]
        print("  result keys:", list(res.keys()))
        url = res.get("map_download_url")
        if url:
            f = requests.get(url, timeout=60)          # URL not printed: it's a credential
            print("  download:", f.status_code, f.headers.get("content-type"), len(f.content), "bytes")
            first = json.loads(f.text)
            print("  after 1 decode:", type(first).__name__)
            if isinstance(first, str):
                print("  after 2 decodes:", type(json.loads(first)).__name__, "(double-encoded)")
    except Exception as e:
        print("  could not parse links response:", e)

# 5) Wrong methods and missing resources
fake = "00000000-0000-0000-0000-000000000000"
req("GET /v1/heatmap", "GET", "/v1/heatmap")
req("DELETE status(fake)", "DELETE", f"/v1/status/{fake}")
req("GET /v1/activities", "GET", "/v1/activities")

# 6) Rate-limit headers on one normal rejected call
req("ratelimit_probe", "POST", "/v1/heatmap", json={})

c1 = credits()
print("credits:", c0, "->", c1, "| charged:", (c0 - c1) if None not in (c0, c1) else "unknown")