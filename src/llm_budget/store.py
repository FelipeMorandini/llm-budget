"""Local SQLite persistence layer for usage logs and budget state."""

from __future__ import annotations


class UsageStore:
    """Local persistence layer using SQLite.

    Stores per-call usage logs and per-project budget state
    in ~/.llm_budget.db (configurable).
    """

    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path

    def log_usage(
        self,
        project: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
    ) -> None:
        """Log a single LLM API call's usage."""

    def get_total_cost(self, project: str) -> float:
        """Get the total accumulated cost for a project."""
        return 0.0
