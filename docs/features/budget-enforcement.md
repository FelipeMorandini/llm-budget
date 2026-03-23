# Budget Enforcement

## Overview

Budget enforcement prevents runaway LLM costs by halting execution when cumulative spend exceeds a configured threshold.

## Setting a Budget

```python
from llm_toll import track_costs

@track_costs(project="my_app", max_budget=5.00)
def chat(prompt):
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
```

The `max_budget` parameter is in USD. When the accumulated cost for the project reaches or exceeds this value, `BudgetExceededError` is raised **before** the next API call is made.

## How It Works

Budget checks happen at two points:

1. **Pre-call check** -- Before the wrapped function executes, the decorator queries the store for the project's total cost. If `current_cost >= max_budget`, the function is never called and `BudgetExceededError` is raised immediately.

2. **Atomic post-call check** -- After calculating the cost of a call, the decorator uses `log_usage_if_within_budget()` which atomically checks the budget and logs usage in a single transaction. If the new total would exceed the budget, the usage is not logged and `BudgetExceededError` is raised.

This two-phase approach prevents both over-budget calls and TOCTOU races in concurrent environments.

## BudgetExceededError

```python
from llm_toll.exceptions import BudgetExceededError

try:
    result = chat("Hello")
except BudgetExceededError as e:
    print(f"Project: {e.project}")
    print(f"Current cost: ${e.current_cost:.4f}")
    print(f"Budget limit: ${e.max_budget:.4f}")
```

The exception carries structured attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `project` | `str \| None` | Project name that exceeded its budget |
| `current_cost` | `float \| None` | Accumulated cost at the time of the error |
| `max_budget` | `float \| None` | Configured budget cap |

## Budget Reset

Reset a project's accumulated cost via the CLI:

```bash
llm-toll --reset --project my_app
```

Or programmatically:

```python
from llm_toll import SQLiteStore

store = SQLiteStore()
store.reset_budget("my_app")
```

## Streaming Budget Behavior

When a streaming response is consumed, the cost is real regardless of budget state. If a streaming call pushes the total over budget:

- The usage is **still logged** (via `log_usage`) to keep the running total accurate
- A **warning** is emitted explaining the budget was exceeded during streaming
- The **next** call to the decorated function will raise `BudgetExceededError` in the pre-call check

This design ensures the budget total stays accurate while acknowledging that a stream that has already been consumed cannot be "un-consumed."

## Budget Periods

The `reset` parameter controls automatic budget resets:

```python
@track_costs(project="my_app", max_budget=10.00, reset="monthly")
def chat(prompt):
    ...
```

!!! note
    Budget reset periods are tracked in the `budgets` table via the `last_reset_at` column.
