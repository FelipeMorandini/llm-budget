# PricingRegistry

In-memory store of per-model cost-per-token pricing.

## Import

```python
from llm_toll import PricingRegistry, default_registry
```

`default_registry` is the shared singleton used by `@track_costs` and all callbacks.

## Constructor

```python
registry = PricingRegistry()
```

Pre-loaded with built-in pricing for OpenAI, Anthropic, Gemini, and local/Ollama models.

## Methods

### `register_model(model, input_cost_per_token, output_cost_per_token)`

Register or override pricing for a model.

```python
default_registry.register_model(
    "my-custom-model",
    input_cost_per_token=1e-06,
    output_cost_per_token=3e-06,
)
```

Raises `ValueError` if costs are negative.

### `set_fallback_pricing(input_cost_per_token, output_cost_per_token)`

Set fallback pricing for any model not yet resolved.

```python
default_registry.set_fallback_pricing(
    input_cost_per_token=1e-06,
    output_cost_per_token=3e-06,
)
```

!!! note
    Models already queried (and cached as unknown) will not retroactively use the fallback. Set fallback before first use.

### `get_cost(model, input_tokens, output_tokens) -> float`

Calculate the cost for a given model and token counts.

**Lookup order:**

1. Exact match in registered models
2. Longest-prefix match (cached for subsequent calls)
3. Fallback pricing if configured
4. Emits `PricingMatrixOutdatedWarning` and returns `0.0`

```python
cost = default_registry.get_cost("gpt-4o", input_tokens=100, output_tokens=50)
```

### `load_remote_pricing(models) -> int`

Bulk-load pricing from a remote source. Merges into the registry, overriding existing entries. Returns the number of models loaded.

```python
count = default_registry.load_remote_pricing({
    "new-model": (1e-06, 3e-06),
    "gpt-4o": (2.5e-06, 10e-06),  # override
})
```

### `has_model(model) -> bool`

Check if a model has pricing registered (exact match only).

### `list_models() -> list[str]`

Return all registered model names (sorted).

## Model Resolution

The registry uses a two-tier lookup:

1. **Exact match** -- `"gpt-4o"` matches `"gpt-4o"` directly
2. **Prefix match** -- `"gpt-4o-2024-08-06"` matches `"gpt-4o"` via longest-prefix

Prefix matching uses boundary detection: the character after the prefix must be `-`, `/`, or end-of-string. This prevents `"o3"` from matching `"o3000"`.

Namespace prefixes ending with `/` or `-` (e.g., `"ollama/"`) always match any suffix.

### Dynamic Cache

Prefix-resolved models are cached for subsequent lookups. The cache is bounded at 1,000 dynamic entries. When the limit is reached, the oldest dynamic entry is evicted. User-registered models (via `register_model`) are never evicted.

## Constants

### `COST_ROUND_PLACES`

```python
from llm_toll.pricing import COST_ROUND_PLACES
# COST_ROUND_PLACES = 10
```

Number of decimal places to round costs to, preventing floating-point drift across many accumulated calls.
