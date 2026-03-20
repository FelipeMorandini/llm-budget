"""Unit tests for SDK parsers and auto-detection."""

from __future__ import annotations

from llm_budget.parsers import auto_detect_usage
from llm_budget.parsers.anthropic import parse_anthropic_response
from llm_budget.parsers.gemini import parse_gemini_response
from llm_budget.parsers.openai import parse_openai_response


class TestParsers:
    """Tests for individual SDK parsers returning None for arbitrary objects."""

    def test_parse_openai_response_returns_none(self) -> None:
        assert parse_openai_response({"not": "an openai response"}) is None

    def test_parse_anthropic_response_returns_none(self) -> None:
        assert parse_anthropic_response({"not": "an anthropic response"}) is None

    def test_parse_gemini_response_returns_none(self) -> None:
        assert parse_gemini_response({"not": "a gemini response"}) is None

    def test_auto_detect_usage_returns_none(self) -> None:
        assert auto_detect_usage({"arbitrary": "object"}) is None

    def test_auto_detect_usage_short_circuits_on_match(self) -> None:
        """When a parser returns a result, auto_detect_usage returns it immediately."""
        from unittest.mock import patch

        expected = ("gpt-4o", 100, 50)
        # Patch the source module so the imported reference in the tuple is replaced
        with patch(
            "llm_budget.parsers.openai.parse_openai_response", return_value=expected
        ) as mock_parser:
            # Re-import to pick up the patched function
            import importlib

            import llm_budget.parsers

            importlib.reload(llm_budget.parsers)
            from llm_budget.parsers import auto_detect_usage as reloaded_auto_detect

            result = reloaded_auto_detect({"mock": "response"})
        assert result == expected
        mock_parser.assert_called_once()
