# RateLimiter

Sliding-window rate limiter for RPM and TPM enforcement.

## Import

```python
from llm_toll import RateLimiter
```

## Constructor

```python
limiter = RateLimiter(
    rpm: int | None = None,
    tpm: int | None = None,
    *,
    _clock: Callable[[], float] | None = None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rpm` | `int \| None` | `None` | Maximum requests per minute. Must be positive or `None`. |
| `tpm` | `int \| None` | `None` | Maximum tokens per minute. Must be positive or `None`. |
| `_clock` | `Callable` | `time.monotonic` | Clock function for testing. Returns current time as float. |

Raises `ValueError` if `rpm` or `tpm` is zero or negative.

## Methods

### `check()`

Check if the next request would exceed rate limits.

- Prunes entries older than 60 seconds from the sliding window
- Checks RPM: if the number of requests in the window meets or exceeds `rpm`, raises `LocalRateLimitError`
- Checks TPM: if the total tokens in the window meets or exceeds `tpm`, raises `LocalRateLimitError`
- Does **not** record the request -- call `record()` after a successful API call

```python
try:
    limiter.check()
except LocalRateLimitError as e:
    print(f"Wait {e.retry_after:.1f}s")
```

### `record(tokens=0)`

Record a completed request for rate-limiting purposes.

- Adds the current timestamp to the RPM window
- Adds `(timestamp, tokens)` to the TPM window
- Called after a successful API call

```python
limiter.record(tokens=input_tokens + output_tokens)
```

## Sliding Window

The rate limiter uses a **60-second sliding window** implemented with `collections.deque`:

- `_request_timestamps`: deque of floats (timestamps for RPM tracking)
- `_token_log`: deque of `(float, int)` tuples (timestamp, token count for TPM tracking)

On each `check()` or `record()` call, entries older than 60 seconds are pruned.

## retry_after Calculation

For RPM limits, `retry_after` is calculated as:

```
retry_after = oldest_timestamp + 60.0 - now
```

For TPM limits, `retry_after` is the time until enough tokens expire to free capacity. The calculation walks from the oldest entry, accumulating freed tokens until enough capacity is available.

## Thread Safety

`check()` and `record()` each acquire the internal lock independently. Under concurrent use, multiple threads may pass `check()` before any calls `record()`, slightly exceeding the configured limit. This is intentional -- holding the lock across the API call would serialize all LLM requests.

## Testing with _clock

The `_clock` parameter allows injecting a fake clock for deterministic testing:

```python
t = 0.0
def fake_clock():
    return t

limiter = RateLimiter(rpm=2, _clock=fake_clock)

limiter.check()
limiter.record()

limiter.check()
limiter.record()

# Third call within same "second" should fail
try:
    limiter.check()  # raises LocalRateLimitError
except LocalRateLimitError:
    t += 61.0  # advance past window
    limiter.check()  # succeeds
```
