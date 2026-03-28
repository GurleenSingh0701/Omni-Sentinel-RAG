# Baseline Metrics (Phase 0)

Date: 2026-03-28

Command used:

```bash
set LLM_TIMEOUT_SECONDS=5
set LLM_MAX_RETRIES=0
uv run python main.py smoke_test
```

## Results
- Total cases: 10
- Passed cases: 7
- Runtime errors: 0
- Success rate: 70.0%
- Route accuracy: 100.0%
- Content check pass rate: 70.0%
- Average latency: 3705.8 ms
- P95 latency: 5094.9 ms

## Notes
- Current failures are due to local model timeouts on some vector queries, which triggers fallback behavior by design.
- Routing baseline is stable at 100% for the current prompt suite.
- This baseline should be re-recorded after any routing, prompt, or model-setting change.
