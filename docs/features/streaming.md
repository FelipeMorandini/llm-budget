# Streaming Support

## Overview

The decorator automatically detects streaming responses (generators and SDK stream objects) and wraps them transparently. Cost is tracked after the stream is fully consumed or the consumer breaks out.

## Sync Streaming

```python
from llm_toll import track_costs

@track_costs(project="my_app", max_budget=5.00)
def stream_response(text):
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": text}],
        stream=True,
        stream_options={"include_usage": True},  # recommended
    )

for chunk in stream_response("Hello"):
    print(chunk.choices[0].delta.content, end="")
# Cost is logged automatically after the stream completes
```

## Stream Detection

The decorator identifies sync streams by checking for:

- Python `GeneratorType` objects
- SDK stream objects that expose both `__next__` and `close()` methods and are iterable

Plain iterators like `map`, `filter`, and `zip` are excluded (they lack a `close` method).

## Supported Chunk Formats

The `StreamAccumulator` processes chunks from all three supported providers:

### OpenAI Chunks

Detects `ChatCompletionChunk` objects by checking for `choices` and `model` attributes. Extracts:

- Text content from `choices[0].delta.content`
- Model name from `chunk.model`
- Token usage from `chunk.usage` (final chunk with `stream_options={"include_usage": True}`)

### Anthropic Events

Detects events by the `type` attribute:

- `message_start` -- Extracts model name and input token count
- `content_block_delta` -- Accumulates text character count
- `message_delta` -- Extracts output token count

### Gemini Chunks

Detects `GenerateContentResponse` chunks by checking for `candidates` and `usage_metadata`. Extracts:

- Text from `candidates[0].content.parts[0].text`
- Token counts from `usage_metadata.prompt_token_count` and `candidates_token_count`

## Token Estimation Fallback

When the API does not provide usage data in the stream (e.g., OpenAI without `stream_options`), output tokens are estimated using a character-based heuristic:

```
estimated_tokens = max(1, char_count // 4)
```

A warning is emitted when estimation is used.

!!! tip
    For accurate token counts with OpenAI streaming, always pass `stream_options={"include_usage": True}`. Without it, output tokens are estimated and input tokens are reported as 0.

## Early Break

If the consumer breaks out of the stream early (e.g., `break` in a `for` loop), the `finally` block still triggers:

- Accumulated usage is extracted and logged
- The underlying SDK stream is closed via `stream.close()`
- Cost is calculated from whatever was consumed

## Budget and Streaming

Since a stream is consumed progressively by the caller, the decorator cannot prevent a streaming call from exceeding the budget mid-stream. Instead:

- A **pre-call budget check** prevents starting a new stream if the budget is already exhausted
- If the stream pushes the total **over** budget, the cost is still logged and a warning is emitted
- The **next** call will be blocked by the pre-call check

See [Budget Enforcement](budget-enforcement.md) for details.

## Async Streaming

Async generators and async streams are also supported transparently:

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

See [Async Support](async-support.md) for more details.
