# Architecture

## Core Principles

- Keep routing deterministic.
- Preserve baseline path with feature flags OFF.
- Add advanced capabilities as optional layers.

## ASCII Component Diagram

```text
+---------+    +-------------+    +--------------+    +--------------+
| Client  | -> | Sanitizer   | -> | Router       | -> | Fetchers      |
| CLI/API |    | + limits    |    | vector/table |    | vector/table  |
+---------+    +-------------+    +------+-------+    +------+--------+
                                              |               |
                                              +-------+-------+
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
