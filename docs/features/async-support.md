# Async Support

## Overview

The `@track_costs` decorator auto-detects async functions and async generators at decoration time. No changes to the decorator call are needed.

## Async Functions

```python
from llm_toll import track_costs

@track_costs(project="my_app", max_budget=5.00)
async def async_chat(text):
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": text}]
    )
    return response
```

The decorator wraps the coroutine and:

1. Runs budget checks via `asyncio.to_thread` so SQLite queries don't block the event loop
2. Awaits the wrapped function
3. Extracts usage from the response
4. Logs cost via `asyncio.to_thread`

## Async Generators (Streaming)

```python
@track_costs(project="my_app")
async def async_stream(text):
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": text}],
        stream=True,
        stream_options={"include_usage": True},
    )
    async for chunk in stream:
        yield chunk
```

Async generators are detected via `inspect.isasyncgenfunction()` and wrapped with the same cost tracking logic as sync streams.

## Async Stream Detection

When an async coroutine returns an async iterable (rather than being an async generator itself), the decorator detects this and wraps it:

```python
@track_costs(project="my_app")
async def get_stream(text):
    # Returns an async stream object, not an async generator
    return await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": text}],
        stream=True,
    )
```

Async streams are identified by checking for `__aiter__` and `__anext__` methods.

## SQLite and the Event Loop

All SQLite operations (`get_total_cost`, `log_usage`, `log_usage_if_within_budget`) are wrapped in `asyncio.to_thread()` so the event loop is never blocked:

```python
# This happens internally:
current_cost = await asyncio.to_thread(store.get_total_cost, project)
```

The `SQLiteStore` uses `check_same_thread=False` and a threading `RLock` for safe cross-thread access.

## Usage with asyncio

```python
import asyncio
from llm_toll import track_costs

@track_costs(project="batch", max_budget=10.00)
async def process(item):
    return await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": item}]
    )

async def main():
    items = ["item1", "item2", "item3"]
    results = await asyncio.gather(*[process(item) for item in items])

asyncio.run(main())
```

!!! note
    Budget enforcement is per-project, not per-coroutine. When running concurrent async calls, budget checks are not serialized -- multiple calls may pass the pre-call check simultaneously. The atomic `log_usage_if_within_budget` transaction provides the final safety net.
