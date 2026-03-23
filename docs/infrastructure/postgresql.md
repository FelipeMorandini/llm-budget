# PostgreSQL Backend

## Overview

For team-wide cost visibility, use a shared PostgreSQL database instead of the default local SQLite store. Multiple developers and processes can track costs against the same database with safe concurrent budget enforcement.

## Installation

```bash
pip install llm-toll[postgres]
```

This installs `psycopg2-binary` as a dependency.

## Configuration

### Environment Variable

The simplest approach -- set `LLM_TOLL_STORE_URL` and all `@track_costs` decorators auto-connect:

```bash
export LLM_TOLL_STORE_URL=postgresql://user:pass@host/llm_costs
```

### Programmatic

```python
from llm_toll import create_store, set_store

store = create_store(url="postgresql://user:pass@host/llm_costs")
set_store(store)
```

The `create_store` factory function detects `postgresql://` or `postgres://` URLs and returns a `PostgresStore` instance. All other URLs (or `None`) return a `SQLiteStore`.

## PostgresStore

The `PostgresStore` class mirrors the `SQLiteStore` API but uses PostgreSQL-native features:

| Feature | SQLite | PostgreSQL |
|---------|--------|-----------|
| Data types | `TEXT`, `REAL`, `INTEGER` | `TIMESTAMPTZ`, `DOUBLE PRECISION`, `SERIAL` |
| Connection management | Single connection with RLock | ThreadedConnectionPool |
| Budget enforcement | Single-transaction check-and-log | Row-level locking (`SELECT ... FOR UPDATE`) |
| Concurrency | Thread-safe via Python lock | Process-safe via database locks |

### Constructor

```python
PostgresStore(
    dsn: str,          # PostgreSQL connection string
    min_conn: int = 1, # Minimum pool connections
    max_conn: int = 10 # Maximum pool connections
)
```

### Connection Pooling

Uses `psycopg2.pool.ThreadedConnectionPool` for connection management:

- Connections are borrowed from the pool for each operation
- Read-only queries have their implicit transactions rolled back on return
- The pool is configured with sensible defaults (1-10 connections)

### Row-Level Locking

Budget enforcement uses `SELECT ... FOR UPDATE` to lock the budget row during atomic check-and-log operations. This prevents concurrent processes from double-spending the budget.

## Schema

The PostgreSQL schema is created automatically on first connection:

```sql
CREATE TABLE IF NOT EXISTS usage_logs (
    id            SERIAL PRIMARY KEY,
    project       TEXT        NOT NULL,
    model         TEXT        NOT NULL,
    input_tokens  INTEGER     NOT NULL,
    output_tokens INTEGER     NOT NULL,
    cost          DOUBLE PRECISION NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS budgets (
    project       TEXT PRIMARY KEY,
    total_cost    DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    last_reset_at TIMESTAMPTZ,
    updated_at    TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_usage_logs_project_created
    ON usage_logs (project, created_at DESC);
```

## CLI with PostgreSQL

```bash
# View stats
llm-toll --stats --store-url postgresql://user:pass@host/llm_costs

# Reset a project
llm-toll --reset --project my_app --store-url postgresql://user:pass@host/llm_costs

# Launch dashboard
llm-toll --dashboard --store-url postgresql://user:pass@host/llm_costs
```

## Fallback Behavior

If the `LLM_TOLL_STORE_URL` environment variable is set but the connection fails, the decorator falls back to local SQLite with a warning:

```
Failed to create store from LLM_TOLL_STORE_URL='postgresql://...': ... Falling back to local SQLite.
```
