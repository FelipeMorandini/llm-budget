# Rate Limiting

## Overview

llm-toll provides local rate limiting to prevent HTTP 429 errors from LLM providers. Limits are enforced **before** the API call is made, saving you both time and potential retry costs.

## Configuration

```python
from llm_toll import track_costs

@track_costs(
    rate_limit=50,     # max 50 requests per minute (RPM)
    tpm_limit=40000,   # max 40,000 tokens per minute (TPM)
)
def chat(prompt):
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `rate_limit` | `int \| None` | Maximum requests per minute (RPM). `None` to disable. |
| `tpm_limit` | `int \| None` | Maximum tokens per minute (TPM). `None` to disable. |

## Sliding Window Algorithm

The rate limiter uses a **60-second sliding window**:

- For RPM: tracks timestamps of recent requests in a deque
- For TPM: tracks `(timestamp, token_count)` tuples in a deque

On each check, entries older than 60 seconds are pruned. If the remaining count meets or exceeds the limit, `LocalRateLimitError` is raised.

## LocalRateLimitError

```python
from llm_toll.exceptions import LocalRateLimitError

try:
    result = chat("Hello")
except LocalRateLimitError as e:
    print(f"Limit type: {e.limit_type}")    # "rpm" or "tpm"
    print(f"Limit value: {e.limit_value}")   # e.g., 50
    print(f"Retry after: {e.retry_after:.1f}s")
```

The `retry_after` attribute tells you exactly how many seconds to wait before the next request is allowed.

| Attribute | Type | Description |
|-----------|------|-------------|
| `limit_type` | `str \| None` | `"rpm"` or `"tpm"` |
| `limit_value` | `int \| None` | The configured limit value |
| `retry_after` | `float \| None` | Seconds until the next request is allowed |

## Scoping

Each `@track_costs` decorator gets its own `RateLimiter` instance. Limits are scoped per-decorator, not per-project or globally.

```python
# These have independent rate limiters
@track_costs(rate_limit=10)
def func_a(): ...

@track_costs(rate_limit=20)
def func_b(): ...
```

## Check vs Record

The rate limiter separates checking from recording:

- `check()` -- Called **before** the API call. Raises `LocalRateLimitError` if limits would be breached.
- `record(tokens=N)` -- Called **after** a successful API call. Adds the request to the sliding window.

This two-step approach avoids counting failed or skipped calls against your limits.

!!! note "Concurrency Note"
    Under concurrent use, multiple threads may pass `check()` before any of them calls `record()`, slightly exceeding the configured limit. This is an accepted trade-off: the alternative (holding the lock across the API call) would serialize all LLM requests.

## Combining with Budget

Rate limits and budget enforcement work together:

```python
@track_costs(
    project="my_app",
    max_budget=5.00,
    rate_limit=50,
    tpm_limit=40000,
)
def chat(prompt):
    ...
```

The order of checks is:

1. Budget check (pre-call)
2. Rate limit check (pre-call)
3. Execute function
4. Extract usage and log cost (post-call)
