import requests
u = "https://api.fortyguard.com/v1/system/fetch-api-key-custom-usage"
r = requests.post(u, json={"api_key": "FAKE-KEY-FOR-TESTING-123",
                           "start_date": "2026-11-01", "end_date": "2026-11-18"}, timeout=60)
print(r.status_code, r.text[:300])