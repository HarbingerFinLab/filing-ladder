"""List prices per million tokens — the exhibit is reported at list, whatever was paid.

Defaults cover the models this benchmark names; ``prices.json`` at the repo root overrides or
extends them (verify every entry against the provider's price page on the day of the run and
record the date). A model with no price gets ``None`` for cost, never silently zero.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .base import Usage


@dataclass(frozen=True)
class Price:
  input: float
  output: float
  cache_write: float | None = None
  cache_read: float | None = None
  as_of: str = ""


DEFAULTS: dict[str, Price] = {
  # Verified against platform.claude.com/pricing before each run; see prices.json.
  "claude-sonnet-4-5": Price(3.0, 15.0, 3.75, 0.30, "2025-09-29"),
  "claude-opus-4-5": Price(5.0, 25.0, 6.25, 0.50, "2025-11-24"),
  # Free tier: paid $0; reported as $0 with the token counts — never a published rung.
  "moonshotai/kimi-k3": Price(0.0, 0.0, None, None, "nvidia-build-free"),
  "deepseek-ai/deepseek-v4-flash-0731": Price(
    0.0, 0.0, None, None, "nvidia-build-free"
  ),
}


def load_prices(repo_root: Path | None = None) -> dict[str, Price]:
  prices = dict(DEFAULTS)
  path = (repo_root or Path.cwd()) / "prices.json"
  if path.exists():
    for model, row in json.loads(path.read_text()).items():
      if model.startswith("_"):
        continue
      prices[model] = Price(
        float(row["input"]),
        float(row["output"]),
        row.get("cache_write"),
        row.get("cache_read"),
        row.get("as_of", ""),
      )
  return prices


def cost_usd(usage: Usage, model: str, prices: dict[str, Price]) -> float | None:
  price = prices.get(model)
  if price is None:
    return None
  per = 1_000_000
  total = (
    usage.input_tokens / per * price.input + usage.output_tokens / per * price.output
  )
  if price.cache_write is not None:
    total += usage.cache_write_tokens / per * price.cache_write
  if price.cache_read is not None:
    total += usage.cache_read_tokens / per * price.cache_read
  return round(total, 6)
