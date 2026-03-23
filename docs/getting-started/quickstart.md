# Quick Start

## Basic Usage (Auto-detect)

For standard SDK clients, the decorator automatically extracts the model name and token counts from the response object:

```python
from llm_toll import track_costs

@track_costs(project="my_scraper", max_budget=2.00, reset="monthly")
def generate_summary(text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": text}]
    )
    return response  # Decorator parses the usage from this object
```

The decorator intercepts the return value, extracts token usage via duck-typing, calculates the cost from the built-in pricing registry, and logs everything to the local SQLite database.

## Bare Decorator

If you just want basic tracking with defaults, use the decorator without arguments:

```python
@track_costs
def chat(prompt):
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
```

This uses `project="default"` with no budget cap or rate limits.

## Advanced Usage (Rate Limits & Explicit Models)

For custom setups or raw API requests, explicitly specify the model and limits:

```python
from llm_toll import track_costs

@track_costs(
    model="claude-sonnet-4-20250514",
    rate_limit=50,       # max 50 requests per minute
    tpm_limit=40000,     # max 40k tokens per minute
    extract_usage=lambda res: (res['model'], res['in_tokens'], res['out_tokens'])
)
def custom_anthropic_call(prompt):
    # custom logic here
    pass
```

The `extract_usage` callable receives the function's return value and must return a tuple of `(model_name, input_tokens, output_tokens)`.

## Error Handling

```python
from llm_toll.exceptions import BudgetExceededError, LocalRateLimitError

try:
    result = generate_summary("some text")
except BudgetExceededError as e:
    print(f"Budget exceeded: ${e.current_cost:.4f} >= ${e.max_budget:.4f}")
except LocalRateLimitError as e:
    print(f"Rate limit hit, retry after {e.retry_after:.1f}s")
```

## Terminal Output

Each call prints a color-coded cost summary to stderr:

```
[cost] gpt-4o: 150 in / 83 out -> $0.0012
```

Session totals are available via the `CostReporter`:

```python
from llm_toll import CostReporter

reporter = CostReporter()
# ... run your calls ...
reporter.report_session()
# [session] 5 calls, 750 in / 415 out, total $0.0058
```

## What's Next?

- [Cost Tracking](../features/cost-tracking.md) -- How the tracking pipeline works
- [Budget Enforcement](../features/budget-enforcement.md) -- Setting budget caps
- [Rate Limiting](../features/rate-limiting.md) -- RPM and TPM limits
- [Streaming](../features/streaming.md) -- Streaming response support
- [Providers](../providers/openai.md) -- Provider-specific guides
