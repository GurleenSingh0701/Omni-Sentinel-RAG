# Runbook

## Standard Commands

- Health check: `uv run python main.py health_check`
- Run query: `uv run python main.py run --query "What was the Q4 revenue?"`
- Smoke test: `uv run python main.py smoke_test`
- API server: `uv run uvicorn api:app --host 0.0.0.0 --port 8000`

## Troubleshooting

- Health check fails:
  - Verify LM Studio server is running.
  - Verify `LMSTUDIO_BASE_URL` and `LMSTUDIO_MODEL`.
- Latency high:
  - Tune model size.
  - Reduce retries.
  - Re-check timeout.
- 429 errors:
  - Increase `API_RATE_LIMIT_REQUESTS` or window.

## Rollback

- Disable advanced toggles:
  - `ENABLE_VERIFY=false`
  - `ENABLE_GUARDRAILS=false`
  - `ENABLE_TRACING=false`
- Keep security toggles ON.
- Re-run smoke test and health check.
