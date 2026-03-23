# Local / Ollama

## Overview

Local models (Ollama, llama.cpp, and other locally-hosted LLMs) are tracked at **$0 cost**. Rate limiting still applies, which is useful for managing local GPU resources.

## Recognized Prefixes

| Prefix | Cost |
|--------|------|
| `ollama/` | $0.00 |
| `local/` | $0.00 |
| `llama.cpp/` | $0.00 |

Any model name starting with these prefixes is matched via the pricing registry's prefix matching and tracked at zero cost.

## Usage with extract_usage

```python
from llm_toll import track_costs

@track_costs(
    model="ollama/llama3",
    rate_limit=10,       # limit local GPU to 10 RPM
    extract_usage=lambda r: ("ollama/llama3", r["prompt_tokens"], r["completion_tokens"])
)
def local_inference(prompt):
    # Ollama call here
    pass
```

## Usage with OpenAI-Compatible API

Ollama's API is OpenAI-compatible. If you use the `openai` client pointed at localhost, auto-parsing works automatically:

```python
from openai import OpenAI
from llm_toll import track_costs

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required but unused
)

@track_costs(model="ollama/llama3", rate_limit=10)
def local_chat(prompt):
    response = client.chat.completions.create(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )
    return response
```

!!! tip
    When using the OpenAI client with Ollama, set `model="ollama/llama3"` in the decorator to ensure the `ollama/` prefix pricing ($0) is applied. The model name from the response may not include the prefix.

## Rate Limiting Local Models

Even at $0 cost, rate limiting is valuable for local models:

```python
@track_costs(
    model="ollama/llama3",
    rate_limit=5,        # max 5 requests per minute
    tpm_limit=10000,     # max 10k tokens per minute
)
def gpu_bound_inference(prompt):
    ...
```

This prevents overwhelming local GPU resources with concurrent requests.

## Monitoring

Usage is still logged to the SQLite store even at $0 cost. You can view call counts and token usage via the CLI:

```bash
llm-toll --stats --model ollama/llama3
```
