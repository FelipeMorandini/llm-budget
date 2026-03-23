# llm-toll

[![PyPI version](https://img.shields.io/pypi/v/llm-toll)](https://pypi.org/project/llm-toll/)
[![Python](https://img.shields.io/pypi/pyversions/llm-toll)](https://pypi.org/project/llm-toll/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Lightweight, drop-in Python decorator to track costs, monitor token usage, and enforce budget and rate limits for LLM API calls.**

## Why llm-toll?

LLM API costs add up fast during prototyping and development. `llm-toll` gives you visibility and control with a single decorator -- no config files, no initialization steps, no external services.

```python
from llm_toll import track_costs

@track_costs(project="my_app", max_budget=5.00)
def summarize(text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": text}]
    )
    return response
```

That's it. Every call is logged, costs are calculated, and budget is enforced automatically.

## Key Features

- **Drop-In Decorator** -- One line of code. No config files, no initialization.
- **Multi-Provider** -- Built-in support for OpenAI, Anthropic, Gemini, and OpenAI-compatible endpoints.
- **Hard Budget Caps** -- Prevents execution when cumulative cost exceeds your threshold.
- **Rate Limiting** -- Local RPM and TPM enforcement to prevent HTTP 429 errors.
- **Streaming Support** -- Transparent cost tracking for sync and async streaming responses.
- **Local Persistence** -- SQLite-backed usage tracking across sessions. Optional PostgreSQL for teams.
- **Cost Reporting** -- Color-coded terminal summaries per call and per session.
- **CLI & Web Dashboard** -- View stats, export CSV, launch a browser-based analytics dashboard.

## Supported Providers

| Provider | SDK Auto-Parsing | Streaming | Custom Overrides |
|----------|:---:|:---:|:---:|
| OpenAI | Yes | Yes | Yes |
| Anthropic | Yes | Yes | Yes |
| Google Gemini | Yes | Yes | Yes |
| Local/Ollama | Via OpenAI-compat | N/A | Rate limiting only |

## Quick Install

```bash
pip install llm-toll
```

See the [Installation](getting-started/installation.md) page for extras and provider-specific packages.

## Quick Start

```python
from llm_toll import track_costs

# Bare decorator -- auto-detects model and tokens from SDK response
@track_costs
def chat(prompt):
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

# With budget and rate limits
@track_costs(project="my_app", max_budget=2.00, rate_limit=50)
def chat_limited(prompt):
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
```

See the [Quick Start guide](getting-started/quickstart.md) for more examples.
