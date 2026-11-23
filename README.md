# FortyGuard Temperature Platform: evaluation evidence

Evidence and reproduction scripts for my SDE Intern (Jan 2027) product evaluation of the
FortyGuard **Temperature Dashboard**, **Temperature API** and **Temperature MCP**.
Author: Satjeet2005 (satjeet2005@gmail.com). The written report and form answers are linked from my submission.

> Tested with an intern-session trial key, which may differ from a real customer account.
> Findings about key generation/expiry are scoped to that.

## Quick reproduction (free, about 1 minute)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # put your trial key in .env (git-ignored)
python run_cases.py
```

`run_cases.py` sends invalid requests only. Failed requests are free, and the harness checks
that the credit balance is identical before and after. Each case states the status a
well-behaved API should return (`expect`); a mismatch prints `BUG` with its finding ID.

## Layout

| Path | What |
|---|---|
| `run_cases.py`, `cases.json` | One-command, zero-cost reproduction of the validation findings |
| `scripts/01..13_*.py` | The original exploratory scripts, in the order I ran them (see below) |
| `evidence/api/logs/` | Raw request/response logs (redacted) |
| `evidence/api/results/` | Completed heatmap / env / route results (paid runs) |
| `redact.py` | Strips signed URLs, AWS key IDs, account IDs, hex keys from output before committing |
| `FINDINGS_MAP.md` | Report finding IDs to the file that proves them |

## Scripts

| Script | Purpose | Writes |
|---|---|---|
| 01_validation_probes | auth and body validation on `/v1/heatmap` | log.jsonl |
| 02_date_time_probes | every `date_time` rule and geometry edge | log2.jsonl |
| 03_baseline_heatmap | one paid baseline run, submit and poll | baseline_result.json |
| 04_env_routing_probes | env_params, routing, status probes | log3.jsonl |
| 05_paid_runs | paid runs with a credit cap (heatmap 20/100 m, env, route) | result_*.json |
| 06_signed_url_expiry | `result_delivery=links` and signed URL lifetime | log5.jsonl |
| 07_followup_probes | follow-up probes with built-in redaction | log6.jsonl |
| 08_key_expiry_check | key expiry/usage behaviour | log4.jsonl |
| 09-10_usage_endpoint_probes | `fetch-api-key-usage` failure modes | stdout |
| 11_mcp_check | cross-check MCP output against REST results (needs activity IDs set in the file) | stdout |
| 12-13_key_echo | **placeholder key only**: shows the 422 echoes the submitted `api_key` | stdout |

Scripts write their logs to the current directory; the files under `evidence/` are the
redacted copies of those runs. New raw output is git-ignored until redacted.

## Safety

* Keys come only from `FORTYGUARD_KEY`. No key is committed anywhere in this repo.
* Run `python redact.py <file>` before adding any new log.
* Paid scripts (03, 05, 06) spend credits; 05 has a hard cap.
