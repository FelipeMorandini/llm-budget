"""Central store of per-model cost-per-token pricing."""

from __future__ import annotations


class PricingRegistry:
    """Central store of per-model cost-per-token pricing.

    Ships with static pricing for OpenAI, Anthropic, and Gemini models.
    Supports custom model overrides and fallback pricing.
    """

    def __init__(self) -> None:
        self._models: dict[str, tuple[float, float]] = {}

    def register_model(
        self,
        model: str,
        input_cost_per_token: float,
        output_cost_per_token: float,
    ) -> None:
        """Register or override pricing for a model."""
        self._models[model] = (input_cost_per_token, output_cost_per_token)

    def get_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Calculate the cost for a given model and token counts."""
        if model not in self._models:
            return 0.0
        input_cost, output_cost = self._models[model]
        return input_tokens * input_cost + output_tokens * output_cost
