# UsageStore

The persistence layer for usage logs and budget state.

## BaseStore (Abstract)

All store backends implement the `BaseStore` abstract base class:

```python
from llm_toll import BaseStore
```

### Abstract Methods

#### `log_usage(project, model, input_tokens, output_tokens, cost)`

Log a single LLM API call and update the project budget.

#### `log_usage_if_within_budget(project, model, input_tokens, output_tokens, cost, max_budget) -> float`

Atomically check budget and log usage. Returns the new total cost. Raises `BudgetExceededError` if the budget would be exceeded.

#### `get_total_cost(project) -> float`

Get the total accumulated cost for a project. Returns `0.0` if no data exists.

#### `get_usage_logs(project, limit=100) -> list[dict]`

Return recent usage log entries for a project, ordered by timestamp descending.

#### `get_all_project_summaries() -> list[dict]`

Return aggregated usage stats per project. Each dict contains: `project`, `total_cost`, `total_input_tokens`, `total_output_tokens`, `call_count`, `last_used`.

#### `get_model_summaries(project=None) -> list[dict]`

Return aggregated usage stats per model. Optionally filtered by project. Each dict contains: `model`, `total_cost`, `total_input_tokens`, `total_output_tokens`, `call_count`.

#### `get_project_summaries_for_model(model) -> list[dict]`

Return aggregated usage stats per project for a specific model.

#### `get_usage_logs_filtered(project=None, model=None, limit=1000) -> list[dict]`

Return usage log entries with optional project/model filters.

#### `get_daily_cost_trends(days=30) -> list[dict]`

Return daily aggregated cost and token data for recent days.

#### `get_budget_utilization() -> list[dict]`

Return budget utilization for all projects.

#### `reset_budget(project)`

Reset the accumulated cost for a project to zero.

#### `close()`

Close the store and release resources.

### Context Manager

`BaseStore` supports the context manager protocol:

```python
with SQLiteStore() as store:
    store.log_usage("project", "gpt-4o", 100, 50, 0.001)
# store.close() called automatically
```

## SQLiteStore

```python
from llm_toll import SQLiteStore

store = SQLiteStore(db_path=None)  # default: ~/.llm_toll.db
store = SQLiteStore(db_path="/custom/path.db")
```

### Features

- Default database: `~/.llm_toll.db`
- Lazy connection initialization (opened on first use)
- Thread-safe via `threading.RLock`
- WAL journal mode for concurrent reads
- `PRAGMA busy_timeout=5000` for lock contention
- `PRAGMA synchronous=NORMAL` for performance
- File permissions set to `0600` on creation (owner read/write only)
- Path traversal prevention (rejects `..` in paths)

### Schema

```sql
CREATE TABLE usage_logs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    project       TEXT    NOT NULL,
    model         TEXT    NOT NULL,
    input_tokens  INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    cost          REAL    NOT NULL,
    created_at    TEXT    NOT NULL
);

CREATE TABLE budgets (
    project       TEXT PRIMARY KEY,
    total_cost    REAL NOT NULL DEFAULT 0.0,
    last_reset_at TEXT,
    updated_at    TEXT NOT NULL
);
```

## UsageStore (Alias)

`UsageStore` is a backward-compatible alias for `SQLiteStore`:

```python
from llm_toll import UsageStore
# UsageStore is SQLiteStore
```

## create_store Factory

```python
from llm_toll import create_store

# SQLite (default)
store = create_store()
store = create_store(url="/path/to/db.sqlite")

# PostgreSQL
store = create_store(url="postgresql://user:pass@host/db")
```

The factory detects `postgresql://` or `postgres://` URLs and returns a `PostgresStore`. All other inputs return a `SQLiteStore`.

## PostgresStore

```python
from llm_toll._postgres_store import PostgresStore

store = PostgresStore(
    dsn="postgresql://user:pass@host/db",
    min_conn=1,
    max_conn=10,
)
```

See [PostgreSQL Backend](../infrastructure/postgresql.md) for details.
