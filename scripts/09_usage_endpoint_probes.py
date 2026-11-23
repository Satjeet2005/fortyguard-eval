import os, requests
from dotenv import load_dotenv

load_dotenv()


B = "https://api.fortyguard.com/v1/system"
REAL = os.getenv("FORTYGUARD_KEY")
FAKE = "FAKE-KEY-FOR-TESTING-123"


def probe(label, path, body):
    r = requests.post(f"{B}/{path}", json=body, timeout=60)
    try:
        j = r.json()
        msg = j.get("message") or (j.get("details") or {}).get("message")
    except ValueError:
        msg = "(non-JSON)"
    print(
        f"{label}: {r.status_code} | {msg} | content-type={r.headers.get('content-type')}"
    )


dates = {"start_date": "2026-11-01", "end_date": "2026-11-18"}
probe("usage, fake key", "fetch-api-key-usage", {"api_key": FAKE})
probe("usage, empty key", "fetch-api-key-usage", {"api_key": ""})
probe("custom, fake key", "fetch-api-key-custom-usage", {"api_key": FAKE, **dates})
probe("custom, real key", "fetch-api-key-custom-usage", {"api_key": REAL, **dates})
