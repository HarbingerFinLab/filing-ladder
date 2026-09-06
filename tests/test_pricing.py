import json

from filing_ladder.providers.base import Usage
from filing_ladder.providers.pricing import Price, cost_of_turns, cost_usd, load_prices

TIERED = {
  "m": Price(
    2.0,
    12.0,
    2.5,
    0.2,
    "2026-09-05",
    long_threshold=272_000,
    long_input=4.0,
    long_output=18.0,
    long_cache_write=5.0,
    long_cache_read=0.4,
  )
}


def test_short_request_bills_at_the_short_rates():
  assert (
    cost_usd(Usage(100_000, 1_000), "m", TIERED) == 100_000 / 1e6 * 2 + 1_000 / 1e6 * 12
  )


def test_reaching_the_threshold_bills_the_whole_request_long():
  # cached tokens count toward the prompt that decides the tier
  u = Usage(input_tokens=72_000, output_tokens=1_000, cache_read_tokens=200_000)
  assert cost_usd(u, "m", TIERED) == round(
    72_000 / 1e6 * 4 + 1_000 / 1e6 * 18 + 200_000 / 1e6 * 0.4, 6
  )


def test_turns_are_costed_one_request_at_a_time():
  # twelve 30K-token turns never reach 272K in any one request, even though they sum past it
  turns = [Usage(30_000, 500) for _ in range(12)]
  assert cost_of_turns(turns, "m", TIERED) == round(
    12 * (30_000 / 1e6 * 2 + 500 / 1e6 * 12), 6
  )
  total = Usage()
  for t in turns:
    total.add(t)
  assert cost_usd(total, "m", TIERED) > cost_of_turns(turns, "m", TIERED)


def test_unknown_model_costs_none():
  assert cost_usd(Usage(1, 1), "nope", TIERED) is None
  assert cost_of_turns([Usage(1, 1)], "nope", TIERED) is None


def test_repo_prices_load_with_long_tier(tmp_path):
  (tmp_path / "prices.json").write_text(
    json.dumps(
      {
        "x": {
          "input": 1,
          "output": 2,
          "cache_read": 0.1,
          "long_threshold": 10,
          "long_input": 3,
          "long_output": 4,
          "as_of": "2026-09-05",
          "source": "ignored",
        }
      }
    )
  )
  prices = load_prices(tmp_path)
  assert prices["x"].long_threshold == 10 and prices["x"].long_input == 3
  assert cost_usd(Usage(10, 0), "x", prices) == round(10 / 1e6 * 3, 6)


def test_committed_prices_json_parses():
  prices = load_prices()
  assert prices["gpt-5.6-terra"].long_threshold == 272_000
  assert prices["claude-sonnet-5"].long_threshold is None
