# Model Compatibility

Omni-Sentinel connects to LM Studio using OpenAI-compatible chat completions.

## Quick Matrix

| Profile | Example | VRAM | Latency | Use Case |
| --- | --- | --- | --- | --- |
| Small | Llama 3.2 1B/3B | 4-8 GB | Fast | Dev and CI checks |
| Medium | Llama 3.1 8B | 10-16 GB | Medium | Balanced production |
| Large | 14B+ instruct | 20+ GB | Slow | Higher quality |

## Validation Checklist

- `uv run python main.py health_check`
- `uv run python main.py smoke_test`
- Verify p95 latency target
- Verify route accuracy target
