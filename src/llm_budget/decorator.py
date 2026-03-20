"""Main entry point: the @track_costs decorator."""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, TypeVar, overload

F = TypeVar("F", bound=Callable[..., Any])


@overload
def track_costs(fn: F) -> F: ...


@overload
def track_costs(
    *,
    project: str = "default",
    model: str | None = None,
    max_budget: float | None = None,
    reset: str | None = None,
    rate_limit: int | None = None,
    tpm_limit: int | None = None,
    extract_usage: Callable[..., tuple[str, int, int]] | None = None,
) -> Callable[[F], F]: ...


def track_costs(
    fn: F | None = None,
    *,
    project: str = "default",
    model: str | None = None,
    max_budget: float | None = None,
    reset: str | None = None,
    rate_limit: int | None = None,
    tpm_limit: int | None = None,
    extract_usage: Callable[..., tuple[str, int, int]] | None = None,
) -> F | Callable[[F], F]:
    """Decorator to track costs, enforce budgets, and rate-limit LLM API calls.

    Can be used with or without arguments:
        @track_costs
        def my_func(): ...

        @track_costs(project="my-project", max_budget=10.0)
        def my_func(): ...
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    if fn is not None:
        return decorator(fn)
    return decorator
