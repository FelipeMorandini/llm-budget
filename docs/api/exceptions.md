# Exceptions

## BudgetExceededError

Raised when cumulative cost exceeds the configured budget cap.

```python
from llm_toll.exceptions import BudgetExceededError
```

### Constructor

```python
BudgetExceededError(
    message: str | None = None,
    *,
    project: str | None = None,
    current_cost: float | None = None,
    max_budget: float | None = None,
)
```

If `message` is `None` and all keyword arguments are provided, a default message is generated:

```
Budget exceeded for project 'my_app': $5.0012 >= $5.0000
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `project` | `str \| None` | The project name that exceeded its budget |
| `current_cost` | `float \| None` | The accumulated cost at the time of the error |
| `max_budget` | `float \| None` | The configured budget cap |

### Usage

```python
try:
    result = chat("Hello")
except BudgetExceededError as e:
    print(f"Project '{e.project}' over budget")
    print(f"Spent ${e.current_cost:.4f} of ${e.max_budget:.4f}")
```

---

## LocalRateLimitError

Raised when local RPM/TPM limit is breached before the API call is made.

```python
from llm_toll.exceptions import LocalRateLimitError
```

### Constructor

```python
LocalRateLimitError(
    message: str | None = None,
    *,
    limit_type: str | None = None,
    limit_value: int | None = None,
    retry_after: float | None = None,
)
```

If `message` is `None` and `limit_type`/`limit_value` are provided, a default message is generated:

```
Rate limit exceeded: 50 rpm limit reached. Retry after 12.3s.
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `limit_type` | `str \| None` | The type of limit breached: `"rpm"` or `"tpm"` |
| `limit_value` | `int \| None` | The configured limit value |
| `retry_after` | `float \| None` | Seconds until the next request is allowed |

### Usage

```python
import time
from llm_toll.exceptions import LocalRateLimitError

try:
    result = chat("Hello")
except LocalRateLimitError as e:
    if e.retry_after is not None:
        time.sleep(e.retry_after)
        result = chat("Hello")  # retry
```

---

## PricingMatrixOutdatedWarning

Emitted as a `UserWarning` when a model is not found in the pricing registry. The model is tracked at $0.00 cost.

```python
from llm_toll.exceptions import PricingMatrixOutdatedWarning
```

### When It Occurs

- A response contains a model name not in the built-in pricing
- No prefix match is found
- No fallback pricing is configured

### Suppressing

```python
import warnings
from llm_toll.exceptions import PricingMatrixOutdatedWarning

warnings.filterwarnings("ignore", category=PricingMatrixOutdatedWarning)
```

### Preventing

Register the model or set fallback pricing before making calls:

```python
from llm_toll import default_registry

# Option 1: Register the specific model
default_registry.register_model("new-model", 1e-06, 3e-06)

# Option 2: Set fallback for all unknown models
default_registry.set_fallback_pricing(1e-06, 3e-06)

# Option 3: Update from remote pricing
from llm_toll import update_pricing
update_pricing()
```
