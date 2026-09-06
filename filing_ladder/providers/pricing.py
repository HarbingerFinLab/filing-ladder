"""List prices per million tokens — the exhibit is reported at list, whatever was paid.

Defaults cover the models this benchmark names; ``prices.json`` at the repo root overrides or
extends them (verify every entry against the provider's price page on the day of the run and
record the date). A model with no price gets ``None`` for cost, never silently zero.

Some providers bill a request whose prompt reaches a threshold at long-context rates
(OpenAI: 272K tokens). That tier is a property of each request, not of a run, so a transcript
is costed turn by turn from its ``turn_usage`` and the threshold is tested on each turn's
prompt (input plus cached tokens). A record without per-turn usage is costed on its total.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
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
  long_threshold: int | None = (
    None  # prompt tokens at or above this bill at the long rates
  )
  long_input: float | None = None
  long_output: float | None = None
  long_cache_write: float | None = None
  long_cache_read: float | None = None


DEFAULTS: dict[str, Price] = {
  # Verified against platform.claude.com/pricing before each run; see prices.json.
  "claude-sonnet-5": Price(2.0, 10.0, 2.50, 0.20, "2026-09-03"),
  "claude-opus-5": Price(5.0, 25.0, 6.25, 0.50, "2026-09-03"),
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
        row.get("long_threshold"),
        row.get("long_input"),
        row.get("long_output"),
        row.get("long_cache_write"),
        row.get("long_cache_read"),
      )
  return prices


def cost_usd(usage: Usage, model: str, prices: dict[str, Price]) -> float | None:
  """Cost of one request at list price; the long-context tier applies to the whole request."""
  price = prices.get(model)
  if price is None:
    return None
  prompt = usage.input_tokens + usage.cache_read_tokens + usage.cache_write_tokens
  long = price.long_threshold is not None and prompt >= price.long_threshold
  rate_in = price.long_input if long and price.long_input is not None else price.input
  rate_out = (
    price.long_output if long and price.long_output is not None else price.output
  )
  rate_cw = (
    price.long_cache_write
    if long and price.long_cache_write is not None
    else price.cache_write
  )
  rate_cr = (
    price.long_cache_read
    if long and price.long_cache_read is not None
    else price.cache_read
  )
  per = 1_000_000
  total = usage.input_tokens / per * rate_in + usage.output_tokens / per * rate_out
  if rate_cw is not None:
    total += usage.cache_write_tokens / per * rate_cw
  if rate_cr is not None:
    total += usage.cache_read_tokens / per * rate_cr
  return round(total, 6)


def cost_of_turns(
  turns: Iterable[Usage], model: str, prices: dict[str, Price]
) -> float | None:
  """Sum of per-request costs, so a long-context threshold is tested on each turn's prompt."""
  total = 0.0
  for usage in turns:
    cost = cost_usd(usage, model, prices)
    if cost is None:
      return None
    total += cost
  return round(total, 6)
