# track_costs

The main entry point for llm-toll. A decorator that wraps any function making LLM API calls to track costs, enforce budgets, and rate-limit.

## Signature

```python
@track_costs
def my_func(): ...

@track_costs(
    project: str = "default",
    model: str | None = None,
    max_budget: float | None = None,
    reset: str | None = None,
    rate_limit: int | None = None,
    tpm_limit: int | None = None,
    extract_usage: Callable[..., tuple[str, int, int]] | None = None,
)
def my_func(): ...
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `project` | `str` | `"default"` | Project name for grouping usage in the store |
| `model` | `str \| None` | `None` | Override the model name (bypasses auto-detection) |
| `max_budget` | `float \| None` | `None` | Hard budget cap in USD |
| `reset` | `str \| None` | `None` | Budget reset period (e.g., `"monthly"`) |
| `rate_limit` | `int \| None` | `None` | Maximum requests per minute (RPM) |
| `tpm_limit` | `int \| None` | `None` | Maximum tokens per minute (TPM) |
| `extract_usage` | `Callable \| None` | `None` | Custom usage extractor: receives the return value, must return `(model, input_tokens, output_tokens)` |

## Usage Modes

### Bare Decorator

```python
@track_costs
def chat(prompt):
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
```

### With Arguments

```python
@track_costs(project="my_app", max_budget=5.00, rate_limit=50)
def chat(prompt):
    ...
```

### Async Functions

```python
@track_costs(project="my_app")
async def async_chat(prompt):
    response = await client.chat.completions.create(...)
    return response
```

### Async Generators

```python
@track_costs(project="my_app")
async def async_stream(prompt):
    stream = await client.chat.completions.create(..., stream=True)
    async for chunk in stream:
        yield chunk
```

## Behavior

1. **Sync functions** -- Wrapped with a sync wrapper. Budget and rate limit checks happen pre-call. Usage extraction and logging happen post-call.
2. **Async coroutines** -- Detected via `inspect.iscoroutinefunction()`. SQLite operations use `asyncio.to_thread()`.
3. **Async generators** -- Detected via `inspect.isasyncgenfunction()`. Wrapped to yield chunks transparently with deferred cost tracking.
4. **Sync generators/streams** -- Detected post-call by checking for `__next__` + `close()`. Wrapped via `wrap_sync_stream()`.
5. **Async streams (return value)** -- If an async function returns an async iterable, it is wrapped via `wrap_async_stream()`.

## Return Value

The decorator is transparent -- it returns whatever the wrapped function returns. For streaming responses, it returns a wrapped generator/async generator that yields the same chunks.

## Helper Functions

### `set_store(store)`

```python
from llm_toll import set_store, SQLiteStore

set_store(SQLiteStore(db_path="/custom/path.db"))
set_store(None)  # Reset to default
```

Inject a custom store for the decorator to use. All subsequent `@track_costs` calls will use this store.

### `set_reporter(reporter)`

```python
from llm_toll import set_reporter, CostReporter

set_reporter(CostReporter(enabled=False))  # Suppress output
set_reporter(None)  # Reset to default
```

Inject a custom `CostReporter` for the decorator to use.

## Exceptions

| Exception | When |
|-----------|------|
| `BudgetExceededError` | Pre-call or post-call budget check fails |
| `LocalRateLimitError` | Pre-call rate limit check fails |
| `PricingMatrixOutdatedWarning` | Model not found in pricing registry (warning, not exception) |
