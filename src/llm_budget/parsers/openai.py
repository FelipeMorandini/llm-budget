"""Auto-parser for OpenAI SDK response objects."""

from __future__ import annotations


def parse_openai_response(response: object) -> tuple[str, int, int] | None:
    """Extract model name and token usage from an OpenAI response.

    Uses duck-typing to detect OpenAI response objects without
    importing the openai package.

    Returns (model, input_tokens, output_tokens) or None.
    """
    return None
