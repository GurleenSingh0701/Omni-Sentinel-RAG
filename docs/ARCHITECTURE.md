# Architecture

## Core Principles

- Keep routing deterministic.
- Preserve baseline path with feature flags OFF.
- Add advanced capabilities as optional layers.

## ASCII Component Diagram

```text
+---------+    +-------------+    +-----------------+
| Client  | -> | Sanitizer   | -> | Router          |
| CLI/API |    | + limits    |    | vector / tabular|
+---------+    +-------------+    +--------+--------+
                                             |
                           +-----------------+-----------------+
                           |                                   |
                           v                                   v
                 +---------------------+            +--------------------------+
                 | Vector Fetcher      |            | Table Fetcher Catalog    |
                 | company_overview.txt|            | revenue/incidents/       |
                 +----------+----------+            | customers CSV            |
                            |                       +------------+-------------+
                            +------------+----------------------+ 
                                         v
                              +-------------------+
                              | Generator (LLM)   |
                              | + Guardrails opt  |
                              | + Verify opt      |
                              +---------+---------+
                                        v
                              +-------------------+
                              | Response + Logs   |
                              +-------------------+
```

## Optional Modules

- Structured logging
- Verification pass
- Numeric guardrails
- Tracing hook
- Rate limiting
- Eval report generation

## Data Layer Notes

- Semantic path reads from `docs/company_overview.txt`.
- Tabular path reads multiple CSV files and concatenates them into markdown sections.
- Default tabular catalog:
        - `data/revenue.csv`
        - `data/incidents.csv`
        - `data/customers.csv`
