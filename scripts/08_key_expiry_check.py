import os, time, json, requests
from dotenv import load_dotenv

load_dotenv()

BASE = "https://api.fortyguard.com"
NEW = os.getenv("FORTYGUARD_KEY")
OLD = os.getenv("FORTYGUARD_OLD_KEY")

def hdrs(k): return {"api-key": k, "Content-Type": "application/json"}

def log(label, r, dt):
    keep = {k: v for k, v in r.headers.items()
            if k.lower().startswith(("x-", "content-type", "server", "retry", "www-"))}
    rec = {"label": label, "status": r.status_code, "seconds": dt, "headers": keep, "body": r.text[:800]}
    with open("log4.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"[{label}] {r.status_code} {dt}s {keep.get('content-type')}\n  {r.text[:300]!r}\n")

def usage(label, key):
    t = time.time()
    try:
        r = requests.post(f"{BASE}/v1/system/fetch-api-key-usage", headers=hdrs(key),
                          json={"api_key": key}, timeout=90)
    except requests.RequestException as e:
        print(f"[{label}] request failed: {e}")
        return None
    log(label, r, round(time.time() - t, 1))
    return r

# 1) New key, up to 3 tries, 15 s apart
good = None
for i in range(3):
    r = usage(f"new_usage_try{i+1}", NEW)
    if r is not None and r.status_code == 200:
        good = r.json()
        break
    time.sleep(15)

if good:
    print("plan:", good["plan_details"])
    print("key:", good["api_key_details"])
    print("credits:", good["credit_summary"]["total_remaining_credits"])

# 2) Does the new key work at all? Empty body to /v1/heatmap costs nothing: 422 = key accepted.
t = time.time()
r = requests.post(f"{BASE}/v1/heatmap", headers=hdrs(NEW), json={}, timeout=60)
log("new_key_heatmap_empty", r, round(time.time() - t, 1))

# 3) Old, expired key
if OLD:
    usage("old_usage", OLD)
    t = time.time()
    r = requests.post(f"{BASE}/v1/heatmap", headers=hdrs(OLD), json={}, timeout=60)
    log("old_key_heatmap_empty", r, round(time.time() - t, 1))