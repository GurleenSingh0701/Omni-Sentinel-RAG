# Data Folder

This folder contains synthetic tabular datasets used by the tabular retrieval path.

## Files

- `revenue.csv`: financial and operational performance by quarter.
- `incidents.csv`: incident response and SOC operations metrics by quarter.
- `customers.csv`: customer segment performance metrics by quarter.

## Schemas

### `revenue.csv`

- `year`
- `quarter`
- `revenue_usd_m`
- `growth_pct`
- `region`
- `new_customers`
- `renewal_rate_pct`
- `operating_margin_pct`
- `support_sla_pct`

### `incidents.csv`

- `year`
- `quarter`
- `region`
- `critical_incidents`
- `p1_mtta_min`
- `p1_mttr_min`
- `auto_resolved_pct`
- `false_positive_pct`

### `customers.csv`

- `year`
- `quarter`
- `segment`
- `active_customers`
- `new_logos`
- `expansion_mrr_usd_k`
- `churn_rate_pct`
- `nps_score`

## Notes

- All values are synthetic and safe for local demos.
- Replace with approved internal data before production deployment.
- Keep headers stable to avoid breaking query expectations and tests.
