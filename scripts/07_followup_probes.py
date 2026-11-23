import os, re, time, json, requests
from dotenv import load_dotenv

load_dotenv()

BASE = "https://api.fortyguard.com"
KEY = os.getenv("FORTYGUARD_KEY")
H = {"api-key": KEY, "Content-Type": "application/json"}
CAP = 15000


def redact(s):
    s = re.sub(r"https://[^\s\"]*X-Amz-[^\s\"]*", "<signed-url-redacted>", s)
    s = re.sub(r"AKIA[0-9A-Z]{16}", "<aws-key-id>", s)
    return re.sub(r"acc(%23|#)[A-Za-z0-9]+", "acc#<redacted>", s)


def credits():
    r = requests.post(
        f"{BASE}/v1/system/fetch-api-key-usage",
        headers=H,
        json={"api_key": KEY},
        timeout=60,
    )
    return r.json()["credit_summary"]["total_remaining_credits"]


START = credits()


def log(label, r, dt):
    keep = {
        k: v
        for k, v in r.headers.items()
        if k.lower().startswith(("x-ratelimit", "content-type", "allow"))
    }
    with open("log6.jsonl", "a") as f:
        f.write(
            json.dumps(
                {
                    "label": label,
                    "status": r.status_code,
                    "seconds": dt,
                    "headers": keep,
                    "body": redact(r.text[:700]),
                }
            )
            + "\n"
        )
    print(
        f"[{label}] {r.status_code} {dt}s allow={r.headers.get('allow')} | {redact(r.text[:200])!r}"
    )


def submit(label, body):
    if START - credits() > CAP:
        raise SystemExit("cap reached")
    before = credits()
    t = time.time()
    r = requests.post(f"{BASE}/v1/heatmap", headers=H, json=body, timeout=90)
    log(label, r, round(time.time() - t, 1))
    if r.status_code != 200:
        return
    aid = r.json()["data"]["activity_id"]
    for _ in range(60):
        time.sleep(4)
        s = requests.get(f"{BASE}/v1/status/{aid}", headers=H, timeout=60).json()
        st = s["data"]["status"]
        if st in ("Completed", "Failed"):
            break
    print(f"   -> {st} after {round(time.time()-t)}s | message: {s.get('message')!r}")
    print(f"   -> credits {before} -> {credits()}")
    if st == "Failed":
        print("   -> failure detail:", redact(json.dumps(s)[:500]))


# 1) Allowed methods (safe)
fake = "00000000-0000-0000-0000-000000000000"
for label, path in (
    ("OPTIONS heatmap", "/v1/heatmap"),
    ("OPTIONS status", f"/v1/status/{fake}"),
):
    t = time.time()
    r = requests.options(BASE + path, headers=H, timeout=30)
    log(label, r, round(time.time() - t, 1))

sq = lambda lon, lat, d: {
    "type": "Polygon",
    "coordinates": [
        [[lon, lat], [lon + d, lat], [lon + d, lat + d], [lon, lat + d], [lon, lat]]
    ],
}
indy = sq(-86.20, 39.76, 0.01)
hour = {"start_date": "2024-07-15", "start_time": "14:00", "filter_type": 1}

# 2) Date limits
submit(
    "date_2018-12-31",
    {
        "polygon_aoi": indy,
        "date_time": {**hour, "start_date": "2018-12-31"},
        "granularity": 100,
    },
)
submit(
    "date_future_2027-06-01",
    {
        "polygon_aoi": indy,
        "date_time": {**hour, "start_date": "2027-06-01"},
        "granularity": 100,
    },
)

# 3) Area cap: about 52.7 mi2 vs the 50 mi2 Premium limit
submit(
    "area_over_cap",
    {"polygon_aoi": sq(-86.26, 39.70, 0.12), "date_time": hour, "granularity": 100},
)

# 4) Coverage outside the US: downtown Dubai, same size as the baseline
submit(
    "dubai",
    {"polygon_aoi": sq(55.270, 25.190, 0.01), "date_time": hour, "granularity": 100},
)

print("total spent this run:", START - credits())
