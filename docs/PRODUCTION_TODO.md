# Omni-Sentinel Advanced Production TODO

Goal: Upgrade the project to advanced/production level without breaking existing behavior.

Core rule: Keep the current graph and routing flow intact. Add features as optional modules behind config flags.

## Phase 0: Stability Baseline (Do First)
- [x] Freeze current behavior with 10 baseline prompts and expected route/output checks.
- [x] Add a `smoke_test` command that runs these prompts locally.
- [x] Record current latency and success rate as baseline metrics.

Exit criteria:
- [x] Current app behavior is reproducible before any advanced changes.

## Phase 1: Plug-and-Play Config Layer
- [x] Add `.env` support for all runtime values (model, base URL, temperature, timeouts).
- [x] Add feature flags (example: `ENABLE_GUARDRAILS`, `ENABLE_VERIFY`, `ENABLE_TRACING`).
- [x] Keep all new flags defaulted to OFF to preserve existing behavior.

Exit criteria:
- [x] Running with all flags OFF produces same behavior as baseline.

## Phase 2: Reliability Hardening (No Logic Rewrite)
- [x] Add timeout and retry wrapper around LLM calls.
- [x] Add safe fallback response when LM Studio is unavailable.
- [x] Add startup health check (`/health` equivalent function for local run).

Exit criteria:
- [x] Transient LM failures do not crash the app.

## Phase 3: Production Observability
- [x] Replace print statements with structured logging (JSON style).
- [x] Add `request_id` per query and log route, latency, and status.
- [x] Add optional tracing integration toggle (Phoenix/OpenTelemetry).

Exit criteria:
- [x] Every request has traceable logs with route + latency.

## Phase 4: Advanced Quality Layer (Optional, High Impact)
- [x] Add a verification pass: check whether final answer is supported by retrieved context.
- [x] Return confidence score + unsupported claim list.
- [x] Add strict mode for numeric queries: only answer numbers from table context.

Exit criteria:
- [x] Hallucination risk is reduced for business-critical prompts.

## Phase 5: API + Deployment Readiness
- [x] Add FastAPI wrapper endpoint for invoke (`POST /query`).
- [x] Keep CLI run path unchanged for backward compatibility.
- [x] Add container-ready config and environment docs.

Exit criteria:
- [x] App can run both as CLI and API without code branching hacks.

## Phase 6: Automated Evaluation
- [x] Build mini eval suite (route accuracy, response correctness, latency percentiles).
- [x] Add regression check in CI for baseline prompts.
- [x] Fail CI if route accuracy or latency degrades beyond threshold.

Exit criteria:
- [x] Quality and performance regressions are automatically caught.

## Phase 7: Security and Operational Controls
- [x] Add input length limits and sanitization.
- [x] Add redaction for sensitive data in logs.
- [x] Add configurable rate limiting for API mode.

Exit criteria:
- [x] Safe defaults for production-facing usage.

## Phase 8: Documentation and Runbooks
- [x] Add architecture diagram for current + optional modules.
- [x] Add runbook: local setup, troubleshooting, rollback steps.
- [x] Add model compatibility matrix for LM Studio model choices.
- [x] Add 30-minute onboarding and incident response playbooks.

Exit criteria:
- [x] A new engineer can run and operate the project in under 30 minutes.

---

## Recommended Build Order (Lowest Risk)
1. Baseline freeze
2. Config flags
3. Reliability wrappers
4. Logging and tracing
5. Verification layer
6. API mode
7. Eval + CI
8. Security + docs

## Non-Breaking Implementation Rules
- [x] Never remove existing graph nodes unless replaced behind a flag.
- [x] Default path must keep current behavior.
- [x] New modules must be injectable adapters, not hard-coded rewrites.
- [x] Add tests before turning ON any new feature by default.

## Definition of Done (Production Level)
- [x] Baseline behavior preserved with flags OFF.
- [ ] 99% request success in local soak tests.
- [x] Route accuracy >= target threshold.
- [x] P95 latency target documented and met.
- [x] Regression tests pass in CI.
- [x] Security/logging controls enabled and documented.
