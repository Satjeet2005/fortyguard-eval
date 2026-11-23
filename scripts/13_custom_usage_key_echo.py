import requests
r = requests.post("https://api.fortyguard.com/v1/system/fetch-api-key-custom-usage",
                  json={"api_key": "FAKE-KEY-FOR-TESTING-123"}, timeout=60)
print(r.status_code, r.text[:300])