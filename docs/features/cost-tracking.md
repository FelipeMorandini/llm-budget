# Cost Tracking

## How It Works

The `@track_costs` decorator wraps your function and performs the following steps on each call:

1. **Pre-call budget check** -- If `max_budget` is set, queries the store for the project's accumulated cost. Raises `BudgetExceededError` if the budget is already exhausted.
2. **Pre-call rate limit check** -- If `rate_limit` or `tpm_limit` is set, checks the sliding window. Raises `LocalRateLimitError` if limits would be breached.
3. **Execute the wrapped function** -- Calls your function normally.
4. **Extract token usage** -- Auto-detects the SDK from the response object using duck-typing. Falls back to the `extract_usage` callback if auto-detection fails.
5. **Calculate cost** -- Looks up per-token pricing in the `PricingRegistry` and computes `input_tokens * input_cost + output_tokens * output_cost`.
6. **Log usage** -- Writes the usage record to the store (SQLite or PostgreSQL) in an atomic transaction.
7. **Report cost** -- Prints a color-coded summary to stderr via `CostReporter`.

## Auto-Detection

The decorator uses duck-typing to detect response objects from supported SDKs:

- **OpenAI** -- Checks for `usage.prompt_tokens` and `usage.completion_tokens` attributes
- **Anthropic** -- Checks for `usage.input_tokens` and `usage.output_tokens` attributes
- **Gemini** -- Checks for `usage_metadata.prompt_token_count` and `usage_metadata.candidates_token_count`

Parsers are tried in sequence (OpenAI, Anthropic, Gemini). The first successful match is used.

## Manual Extraction

When auto-detection is not possible (e.g., raw HTTP responses, custom APIs), use the `extract_usage` parameter:

```python
@track_costs(
    extract_usage=lambda res: (res["model"], res["input_tokens"], res["output_tokens"])
)
def my_custom_llm_call(prompt):
    # Returns a dict with model, input_tokens, output_tokens
    return call_my_api(prompt)
```

The callable must return a tuple of `(model: str, input_tokens: int, output_tokens: int)`.

If `extract_usage` raises an exception, the decorator emits a warning and skips cost tracking for that call (the function's return value is still passed through).

## Pricing Registry

Costs are computed using the `PricingRegistry`, which stores per-token pricing for each model. The registry ships with built-in pricing for:

- **OpenAI**: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo, o1, o1-mini, o3, o3-mini, o4-mini
- **Anthropic**: claude-sonnet-4-20250514, claude-3.5-sonnet, claude-3-haiku, claude-3-opus, claude-3.5-haiku
- **Gemini**: gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash, gemini-2.5-pro, gemini-2.5-flash
- **Local**: ollama/, local/, llama.cpp/ (all $0.00)

Model lookup uses exact match first, then longest-prefix match (e.g., `gpt-4o-2024-08-06` resolves to `gpt-4o`).

### Custom Model Pricing

```python
from llm_toll import default_registry

# Register a custom model
default_registry.register_model(
    "my-custom-model",
    input_cost_per_token=1e-06,
    output_cost_per_token=3e-06,
)
```

### Fallback Pricing

```python
# Set fallback for any unrecognized model
default_registry.set_fallback_pricing(
    input_cost_per_token=1e-06,
    output_cost_per_token=3e-06,
)
```

Without fallback pricing, unrecognized models emit a `PricingMatrixOutdatedWarning` and are tracked at $0.00.

## Cost Rounding

All costs are rounded to 10 decimal places (`COST_ROUND_PLACES = 10`) to prevent floating-point drift from accumulating across many calls.

## Persistence

Usage logs and budget state are stored locally in `~/.llm_toll.db` (SQLite) by default. Each call creates:

- A row in `usage_logs` with project, model, token counts, cost, and timestamp
- An upsert to `budgets` incrementing the project's accumulated cost

See [PostgreSQL Backend](../infrastructure/postgresql.md) for team-wide tracking.
