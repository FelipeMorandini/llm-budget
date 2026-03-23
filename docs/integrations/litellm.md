# LiteLLM Integration

## Overview

The `LiteLLMCallback` provides zero-decorator cost tracking for all LiteLLM completions. Register it once and every LiteLLM call is automatically tracked.

## Setup

```python
import litellm
from llm_toll import LiteLLMCallback

litellm.callbacks = [LiteLLMCallback(project="my-app", max_budget=10.0)]

# All litellm completions are now tracked automatically
response = litellm.completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `project` | `str` | `"default"` | Project name for grouping usage |
| `max_budget` | `float \| None` | `None` | Hard budget cap in USD |
| `store` | `BaseStore \| None` | `None` | Custom store instance (defaults to shared store) |
| `reporter` | `CostReporter \| None` | `None` | Custom reporter instance |

## Model Normalization

LiteLLM uses model strings with provider prefixes like `"openai/gpt-4o"` or `"anthropic/claude-sonnet-4-20250514"`. The callback automatically strips the provider prefix when the suffix is a known model in the pricing registry.

This preserves namespace-prefixed models like `"ollama/llama3"` that rely on the `"ollama/"` pricing prefix.

**Examples:**

| LiteLLM Model | Resolved Model |
|---------------|---------------|
| `openai/gpt-4o` | `gpt-4o` |
| `anthropic/claude-sonnet-4-20250514` | `claude-sonnet-4-20250514` |
| `ollama/llama3` | `ollama/llama3` (preserved) |

## Callback Methods

### `log_success_event`

Called by LiteLLM after a successful completion. Extracts token usage from the response object using the same auto-detection pipeline as `@track_costs`, calculates cost, and logs it to the store.

### `log_failure_event`

Called by LiteLLM after a failed completion. No-op -- failed calls are not tracked.

## Budget Enforcement

When `max_budget` is set, the callback checks the budget on the **next** successful completion. If the accumulated cost exceeds the budget, `BudgetExceededError` is raised.

!!! note
    Budget is checked at log time (after the call), not before. For pre-call budget enforcement, combine with the `@track_costs` decorator.

## Combining with @track_costs

The callback and decorator can be used together:

```python
import litellm
from llm_toll import LiteLLMCallback, track_costs

litellm.callbacks = [LiteLLMCallback(project="my-app")]

@track_costs(project="my-app", max_budget=10.0)
def important_call(prompt):
    return litellm.completion(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
```

!!! warning
    If you use both, the call may be tracked twice. Use one or the other unless you have a specific reason to combine them.
