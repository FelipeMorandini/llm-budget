# OpenAI

## Auto-Detection

The OpenAI parser detects responses by checking for `usage.prompt_tokens` and `usage.completion_tokens` attributes (duck-typing). It works with:

- `openai.ChatCompletion` response objects
- Any object with a compatible `usage` attribute structure

## Supported Models

| Model | Input Cost (per token) | Output Cost (per token) |
|-------|----------------------|------------------------|
| gpt-4o | $2.50e-06 | $10.0e-06 |
| gpt-4o-mini | $1.50e-07 | $6.00e-07 |
| gpt-4-turbo | $1.00e-05 | $3.00e-05 |
| gpt-3.5-turbo | $5.00e-07 | $1.50e-06 |
| o1 | $1.50e-05 | $6.00e-05 |
| o1-mini | $3.00e-06 | $1.20e-05 |
| o3 | $1.00e-05 | $4.00e-05 |
| o3-mini | $1.10e-06 | $4.40e-06 |
| o4-mini | $1.10e-06 | $4.40e-06 |

Versioned model names (e.g., `gpt-4o-2024-08-06`) are resolved via longest-prefix matching to the base model pricing.

## Basic Usage

```python
from openai import OpenAI
from llm_toll import track_costs

client = OpenAI()

@track_costs(project="my_app", max_budget=5.00)
def chat(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response
```

## Streaming

```python
@track_costs(project="my_app")
def stream_chat(prompt):
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        stream_options={"include_usage": True},
    )

for chunk in stream_chat("Hello"):
    print(chunk.choices[0].delta.content or "", end="")
```

!!! tip
    Always pass `stream_options={"include_usage": True}` for accurate token counts. Without it, output tokens are estimated from character count.

## Async

```python
from openai import AsyncOpenAI

client = AsyncOpenAI()

@track_costs(project="my_app")
async def async_chat(prompt):
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response
```

## Response Format

The parser expects this structure on the response object:

```python
response.model         # str, e.g., "gpt-4o-2024-08-06"
response.usage.prompt_tokens       # int
response.usage.completion_tokens   # int
```
