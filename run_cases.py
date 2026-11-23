"""Reproducible, zero-cost harness for the API findings.

Every case is expected to FAIL validation, and failed requests are free, so the
credit balance must be identical before and after. `expect` is the status a
well-behaved API should return; a mismatch is reported as BUG with the finding id
(see FINDINGS_MAP.md). Key is read from FORTYGUARD_KEY only; request bodies for
usage endpoints are never printed.

    export FORTYGUARD_KEY=...      # or put it in .env
    python run_cases.py            # writes evidence/api/run_cases_result.json
"""
import json, os, sys, time
import requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ.get("FORTYGUARD_KEY")
if not KEY:
    sys.exit("Set FORTYGUARD_KEY (see .env.example)")

cfg = json.load(open("cases.json"))
BASE = cfg["base"]

def balance():
    r = requests.post(f"{BASE}/v1/system/fetch-api-key-usage",
                      headers={"api-key": KEY}, json={"api_key": KEY}, timeout=60)
    return r.json()["credit_summary"]["total_remaining_credits"]

def fill(o):
    if o == "$POLY": return cfg["polygon"]
    if isinstance(o, dict): return {k: fill(v) for k, v in o.items()}
    return o

before = balance()
rows = []
for c in cfg["cases"]:
    h = {"Content-Type": "application/json"}
    k = c.get("key", "good")
    if k == "good": h["api-key"] = KEY
    elif k == "bad": h["api-key"] = "0" * 32
    t = time.time()
    try:
        r = requests.request(c["method"], BASE + c["path"], headers=h,
                             json=fill(c["body"]) if c["body"] is not None else None, timeout=60)
        status, ctype = r.status_code, r.headers.get("content-type", "")
    except requests.RequestException as e:
        status, ctype = f"ERR {type(e).__name__}", ""
    ok = status == c["expect"]
    rows.append({"id": c["id"], "finding": c["finding"], "expect": c["expect"],
                 "actual": status, "result": "ok" if ok else "BUG",
                 "content_type": ctype, "seconds": round(time.time() - t, 2)})
    print(f'{c["id"]:<22}{c["finding"]:<5}expect={c["expect"]} actual={status} {"ok" if ok else "BUG"}')
after = balance()
print(f"\ncredits before={before} after={after} -> {'free as documented' if before == after else 'CHARGED (!)'}")
json.dump({"credits_before": before, "credits_after": after, "rows": rows},
          open("evidence/api/run_cases_result.json", "w"), indent=2)
