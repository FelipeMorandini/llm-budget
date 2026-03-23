# Changelog

All notable changes to llm-toll are documented here.

## v0.13.0

- Round all costs to 10 decimal places (`COST_ROUND_PLACES`) to prevent floating-point drift
- Web dashboard for cost trends and usage analytics

## v0.12.0

- PostgreSQL backend for team-wide cost tracking
- `PostgresStore` with `ThreadedConnectionPool` and row-level locking
- `create_store()` factory function with URL-based backend selection
- `LLM_TOLL_STORE_URL` environment variable support
- Graceful fallback to SQLite on connection failure

## v0.11.0

- Auto-updating pricing registry from remote source
- `update_pricing()` function with local caching (24h TTL)
- `--update-pricing` CLI command
- `load_remote_pricing()` for bulk pricing updates

## v0.10.0

- LangChain callback integration (`LangChainCallback`)
- Pre-call budget check in `on_llm_start`
- Post-call usage logging in `on_llm_end`

## v0.9.0

- LiteLLM callback integration (`LiteLLMCallback`)
- Model name normalization for LiteLLM provider prefixes
- Zero-decorator cost tracking for all LiteLLM calls

## v0.8.0

- Hardening batch 3: TPM retry_after calculation, prefix boundary matching, bounded dynamic cache
- Protected user-registered models from cache eviction
- Fixed prefix resolution race condition

## v0.7.0

- Hardening batch 2: TOCTOU documentation, mid-stream break test, coverage CI
- Hardening batch 1: version single source of truth, context manager support, pricing validation

## v0.6.0

- CLI dashboard for viewing costs and usage statistics
- `--stats`, `--reset`, `--export csv` commands
- `--project` and `--model` filters
- Color-coded cost output with `NO_COLOR` support

## v0.5.0

- Async decorator support for async functions and async generators
- `asyncio.to_thread` for non-blocking SQLite operations
- Transparent async stream wrapping

## v0.4.0

- Gemini SDK auto-parser
- Local/Ollama provider support with $0 cost tracking
- Rate limiting for local models

## v0.3.0

- `RateLimiter` with sliding-window RPM and TPM enforcement
- `LocalRateLimitError` with `retry_after` attribute
- Pre-call rate limit checks in the decorator

## v0.2.0

- Streaming support for OpenAI and Anthropic
- `StreamAccumulator` for chunk-based token tracking
- Character-based token estimation fallback

## v0.1.0

- Initial release
- `@track_costs` decorator with auto-detection for OpenAI and Anthropic
- `PricingRegistry` with built-in model pricing
- `SQLiteStore` for local persistence
- `CostReporter` with color-coded terminal output
- `BudgetExceededError` for budget enforcement
- GitHub Actions release pipeline
