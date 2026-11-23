import os, time, requests
from dotenv import load_dotenv

load_dotenv()

B = "https://api.fortyguard.com/v1/system"
REAL = os.getenv("FORTYGUARD_KEY")


def probe(label, path, body):
    r = requests.post(f"{B}/{path}", json=body, timeout=60)
    try:
        j = r.json()
        msg = j.get("message") or (j.get("details") or {}).get("message")
        extra = ""
        if r.ok and isinstance(j, dict):
            extra = f" | top-level keys: {list(j.keys())[:8]}"
    except ValueError:
        msg, extra = "(non-JSON)", ""
    print(f"{label}: {r.status_code} | {msg}{extra}")


# Control: this worked earlier
probe("CONTROL usage, real key", "fetch-api-key-usage", {"api_key": REAL})

# Custom usage with the real key, several date shapes (one change at a time)
cases = {
    "iso dates": {"start_date": "2026-11-01", "end_date": "2026-11-18"},
    "same day": {"start_date": "2026-11-18", "end_date": "2026-11-18"},
    "datetime strings": {
        "start_date": "2026-11-18T00:00:00Z",
        "end_date": "2026-11-18T23:59:59Z",
    },
    "us format": {"start_date": "11/01/2026", "end_date": "11/18/2026"},
    "end before start": {"start_date": "2026-11-18", "end_date": "2026-11-01"},
    "before this key began": {"start_date": "2026-10-01", "end_date": "2026-10-31"},
}
for label, dates in cases.items():
    probe(f"CUSTOM {label}", "fetch-api-key-custom-usage", {"api_key": REAL, **dates})
    time.sleep(1)
