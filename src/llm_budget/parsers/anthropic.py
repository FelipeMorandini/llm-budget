"""Auto-parser for Anthropic SDK response objects."""

from __future__ import annotations


def parse_anthropic_response(response: object) -> tuple[str, int, int] | None:
    """Extract model name and token usage from an Anthropic response.

    Uses duck-typing to detect Anthropic response objects without
    importing the anthropic package.

    Returns (model, input_tokens, output_tokens) or None.
    """
    return None
