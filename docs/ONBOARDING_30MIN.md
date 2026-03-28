# 30-Minute Onboarding

## 0-10 Minutes

1. Start LM Studio and load a model.
2. Copy `.env.example` to `.env`.
3. Set `LMSTUDIO_MODEL` and run health check.
4. Confirm synthetic data files exist:
	- `docs/company_overview.txt`
	- `data/revenue.csv`
	- `data/incidents.csv`
	- `data/customers.csv`

## 10-20 Minutes

1. Run CLI query.
2. Start API and hit `/health` and `/query`.
3. Validate multi-table query:
	- `uv run python main.py run --query "Summarize Q4 2025 incidents and enterprise customers"`

## 20-30 Minutes

1. Run route-only smoke regression.
2. Open `eval_report.json`.
3. Read `docs/RUNBOOK.md` and `docs/INCIDENT_RESPONSE.md`.
