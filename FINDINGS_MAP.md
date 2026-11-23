# Findings map

Finding IDs are from the written report. Only mappings I can point to a file for are listed;
dashboard (D1-D12) and MCP (M1-M14) findings rest on screenshots and the Claude Code session,
not on scripts here.

| ID | Finding | Reproduce | Evidence |
|---|---|---|---|
| A1 | Date/time and distance-rule violations return unhandled **500** instead of 422 | `run_cases.py` cases `type1_no_start_time`, `type2_no_end_time`, `end_before_start`, `bad_*_format` | `evidence/api/logs/log2.jsonl`, `log3.jsonl` (`env_*`, `route_over_200km`) |
| A2 | Three different time conventions across endpoints | `scripts/03`, `04`, `05` | `evidence/api/results/*.json` (compare `metadata` blocks) |
| A3 | Granularity limits inconsistent (100/60 m flat vs 20 m varied) | `scripts/05_paid_runs.py` | `result_A_*`, `result_B_*` |
| A5 | Seven distinct error body shapes | `run_cases.py` (all cases record content-type) | `evidence/api/logs/log.jsonl`, `log3.jsonl` |
| A8 | API key sent in JSON body on usage endpoints; the 422 echoes it back | `scripts/12`, `13` (placeholder key) | stdout of those scripts |
| M-series | MCP exposes 11 tools, 9 documented | see report | dashboard/MCP notes in the report |
