# Incident Response

## First Response

1. Run health check.
2. Check API `/health`.
3. Check latest eval report.
4. Inspect structured logs.

## Common Incidents

- LM Studio unavailable
- latency spikes
- response quality regression
- API traffic spikes

## Recovery

1. Stabilize with baseline-safe flags.
2. Re-run smoke tests.
3. Validate latency and success thresholds.
4. Document root cause and permanent fix.
