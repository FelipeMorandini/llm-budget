# Pricing Updates

## Overview

The pricing registry ships with built-in per-token pricing, but LLM providers change their prices regularly. The `update_pricing()` function fetches the latest pricing from a remote source and caches it locally.

## Programmatic Usage

```python
from llm_toll import update_pricing

# Fetches latest pricing, caches for 24 hours
ok = update_pricing()
if ok:
    print("Pricing updated")
else:
    print("Failed to update, using built-in pricing")
```

## CLI Usage

```bash
llm-toll --update-pricing
```

## How It Works

1. **Check local cache** -- Reads `~/.llm_toll/pricing_cache.json`. If the cache exists and is less than `ttl_hours` old, loads it directly.
2. **Fetch from remote** -- If the cache is stale or missing, fetches pricing JSON from the configured URL.
3. **Write cache** -- Writes the fetched pricing to the cache file atomically (via a temp file and `os.replace`).
4. **Apply to registry** -- Calls `registry.load_remote_pricing()` to merge the new pricing into the in-memory registry.

## Parameters

```python
update_pricing(
    url: str | None = None,        # Remote URL (default: GitHub-hosted pricing.json)
    ttl_hours: int = 24,           # Cache TTL in hours
    cache_path: Path | None = None, # Cache file path (default: ~/.llm_toll/pricing_cache.json)
    registry: PricingRegistry | None = None,  # Registry to update (default: shared)
)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `url` | GitHub-hosted `pricing.json` | URL to fetch pricing JSON |
| `ttl_hours` | `24` | Hours before the cache is considered stale |
| `cache_path` | `~/.llm_toll/pricing_cache.json` | Local cache file path |
| `registry` | `default_registry` | The pricing registry to update |

## Pricing JSON Format

The remote pricing source must be a JSON object mapping model names to `[input_cost, output_cost]` arrays:

```json
{
    "gpt-4o": [2.5e-06, 10.0e-06],
    "claude-sonnet-4-20250514": [3.0e-06, 1.5e-05],
    "gemini-2.5-flash": [1.5e-07, 6.0e-07]
}
```

Invalid entries (non-numeric values, negative costs, wrong array length) are silently skipped.

## Failure Handling

- **Network failure** -- Falls back to stale cache if available, otherwise returns `False` (built-in pricing is retained)
- **Malformed data** -- Raises `ValueError` if no valid entries are found
- **Cache corruption** -- Silently ignored; treated as cache miss

The function returns `True` if pricing was successfully updated (from cache or remote), `False` on failure.

## Caching Details

- Cache location: `~/.llm_toll/pricing_cache.json`
- Cache format: JSON with `updated_at` timestamp and `models` dict
- Cache writes are atomic (write to `.tmp`, then `os.replace`)
- The directory is created automatically if it does not exist
