"""Custom exceptions for llm_budget."""


class BudgetExceededError(Exception):
    """Raised when cumulative cost exceeds the configured budget cap."""


class LocalRateLimitError(Exception):
    """Raised when local RPM/TPM limit is breached before the API call is made."""


class PricingMatrixOutdatedWarning(UserWarning):
    """Emitted when a model is not found in the pricing registry."""
