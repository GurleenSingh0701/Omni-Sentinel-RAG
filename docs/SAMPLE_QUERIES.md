# Sample Queries

Use these queries to test routing quality and answer behavior across semantic and tabular paths.

## Vector / Semantic Queries

1. What is Omni-Sentinel Analytics and what products does it offer?
2. Summarize the synthetic compliance and security posture.
3. What are the roadmap themes mentioned in the company overview?
4. Explain the support escalation tiers in simple terms.

## Tabular Finance Queries (`revenue.csv`)

1. What was the Q4 2024 revenue and growth percentage?
2. Compare Q4 2024 vs Q4 2025 revenue and new customers.
3. Show the trend of renewal_rate_pct from 2022 Q1 to 2025 Q4.
4. Which quarter has the highest operating_margin_pct?

## Tabular Incident Queries (`incidents.csv`)

1. What were critical incidents and MTTR in Q4 2025?
2. How did p1_mtta_min change from 2022 Q1 to 2025 Q4?
3. Which quarter has the best auto_resolved_pct?
4. Compare false_positive_pct between 2023 Q4 and 2025 Q4.

## Tabular Customer Queries (`customers.csv`)

1. How many active enterprise customers were there in Q4 2025?
2. Compare churn_rate_pct across SMB, Mid-Market, and Enterprise in Q4 2025.
3. What is the NPS trend for Enterprise from 2022 Q1 to 2025 Q4?
4. Which segment has the highest expansion_mrr_usd_k in Q4 2025?

## Cross-Table Demo Queries

1. For Q4 2025, summarize revenue, critical incidents, and enterprise NPS in one answer.
2. Do higher renewal rates align with lower churn in the latest year?
3. Summarize Q4 2025 performance using finance, incidents, and customer metrics.

## CLI Run Format

```bash
uv run python main.py run --query "For Q4 2025, summarize revenue, critical incidents, and enterprise NPS in one answer."
```
