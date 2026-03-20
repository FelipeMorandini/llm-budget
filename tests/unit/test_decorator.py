"""Unit tests for the track_costs decorator."""

from __future__ import annotations

from llm_budget.decorator import track_costs


class TestTrackCostsDecorator:
    """Tests for the track_costs decorator's wrapping behavior."""

    def test_bare_decorator_preserves_return_value(self) -> None:
        @track_costs
        def greet() -> str:
            return "hello"

        assert greet() == "hello"

    def test_decorator_with_arguments_preserves_return_value(self) -> None:
        @track_costs(project="test", max_budget=10.0)
        def greet() -> str:
            return "hello"

        assert greet() == "hello"

    def test_decorated_function_preserves_name(self) -> None:
        @track_costs
        def my_function() -> None:
            """My docstring."""

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."

    def test_decorator_with_all_parameters(self) -> None:
        def custom_extractor(resp: object) -> tuple[str, int, int]:
            return ("model", 0, 0)

        @track_costs(
            project="proj",
            model="gpt-4o",
            max_budget=5.0,
            reset="monthly",
            rate_limit=60,
            tpm_limit=100_000,
            extract_usage=custom_extractor,
        )
        def call_llm() -> str:
            return "response"

        assert call_llm() == "response"

    def test_decorated_function_passes_through_args_and_kwargs(self) -> None:
        @track_costs
        def add(a: int, b: int, extra: int = 0) -> int:
            return a + b + extra

        assert add(1, 2) == 3
        assert add(1, 2, extra=10) == 13
