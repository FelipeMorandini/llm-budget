# Gemini

## Auto-Detection

The Gemini parser detects responses by checking for `usage_metadata` with `prompt_token_count` and `candidates_token_count` attributes (duck-typing). It works with:

- `google.genai.GenerateContentResponse` objects
- Any object with a compatible `usage_metadata` attribute structure

## Supported Models

| Model | Input Cost (per token) | Output Cost (per token) |
|-------|----------------------|------------------------|
| gemini-1.5-pro | $1.25e-06 | $5.00e-06 |
| gemini-1.5-flash | $7.50e-08 | $3.00e-07 |
| gemini-2.0-flash | $1.00e-07 | $4.00e-07 |
| gemini-2.5-pro | $1.25e-06 | $1.00e-05 |
| gemini-2.5-flash | $1.50e-07 | $6.00e-07 |

## Basic Usage

```python
from google import genai
from llm_toll import track_costs

client = genai.Client()

@track_costs(project="my_app", max_budget=5.00)
def chat(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response
```

## Streaming

```python
@track_costs(project="my_app")
def stream_chat(prompt):
    return client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=prompt,
    )

for chunk in stream_chat("Hello"):
    print(chunk.text, end="")
```

The stream accumulator extracts:

- Text from `candidates[0].content.parts[0].text`
- Model version from `chunk.model_version`
- Token counts from `usage_metadata.prompt_token_count` and `candidates_token_count`

## Async

```python
@track_costs(project="my_app")
async def async_chat(prompt):
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response
```

## Response Format

The parser expects this structure:

```python
response.model_version                          # str (optional)
response.usage_metadata.prompt_token_count      # int
response.usage_metadata.candidates_token_count  # int
```

## Model Name Extraction

Gemini responses carry the model version in `model_version` rather than `model`. The parser uses this when available. For streaming, the model version may not appear in every chunk.
