"""Model providers behind one small interface, so every rung runs on any model with tool use."""

from __future__ import annotations

from ..config import Settings
from .base import Provider


def make_provider(name: str, model: str, settings: Settings, **kwargs) -> Provider:
  if name == "anthropic":
    from .anthropic import AnthropicProvider

    return AnthropicProvider(settings.require("anthropic_api_key"), model, **kwargs)
  if name == "nvidia":
    from .openai_compat import OpenAICompatProvider

    return OpenAICompatProvider(
      api_key=settings.require("nvidia_api_key"),
      base_url="https://integrate.api.nvidia.com/v1",
      model=model,
      name="nvidia",
      **kwargs,
    )
  if name == "openrouter":
    from .openai_compat import OpenAICompatProvider

    return OpenAICompatProvider(
      api_key=settings.require("openrouter_api_key"),
      base_url="https://openrouter.ai/api/v1",
      model=model,
      name="openrouter",
      **kwargs,
    )
  raise SystemExit(f"unknown provider {name!r} (anthropic | nvidia | openrouter)")
