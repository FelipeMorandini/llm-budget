# Anthropic

## Auto-Detection

The Anthropic parser detects responses by checking for `usage.input_tokens` and `usage.output_tokens` attributes (duck-typing). It works with:

- `anthropic.Message` response objects
- Any object with a compatible `usage` attribute structure

## Supported Models

| Model | Input Cost (per token) | Output Cost (per token) |
|-------|----------------------|------------------------|
| claude-sonnet-4-20250514 | $3.00e-06 | $1.50e-05 |
| claude-3.5-sonnet | $3.00e-06 | $1.50e-05 |
| claude-3-haiku | $2.50e-07 | $1.25e-06 |
| claude-3-opus | $1.50e-05 | $7.50e-05 |
| claude-3.5-haiku | $8.00e-07 | $4.00e-06 |

Versioned model names are resolved via longest-prefix matching.

## Basic Usage

```python
from anthropic import Anthropic
from llm_toll import track_costs

client = Anthropic()

@track_costs(project="my_app", max_budget=5.00)
def chat(prompt):
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response
```

## Streaming

```python
@track_costs(project="my_app")
def stream_chat(prompt):
    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            yield text
```

The stream accumulator processes Anthropic event types:

- `message_start` -- Extracts model name and input tokens
- `content_block_delta` -- Accumulates text for character count
- `message_delta` -- Extracts output tokens

## Async

```python
from anthropic import AsyncAnthropic

client = AsyncAnthropic()

@track_costs(project="my_app")
async def async_chat(prompt):
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response
```

## Response Format

The parser expects this structure on the response object:

```python
response.model                # str, e.g., "claude-sonnet-4-20250514"
response.usage.input_tokens   # int
response.usage.output_tokens  # int
```
