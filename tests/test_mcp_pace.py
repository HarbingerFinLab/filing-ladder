"""The pace on the hosted repository's MCP calls (PROTOCOL §11): under the plan's caps, with a margin."""

from types import SimpleNamespace

from filing_ladder.representations.mcp import (
  PACE,
  SEC_ADVANCED_PLAN_MCP_CAPS,
  McpClient,
  Pacer,
)


class Clock:
  def __init__(self, start: float = 36000.0) -> None:
    self.now = start
    self.slept: list[float] = []

  def time(self) -> float:
    return self.now

  def sleep(self, seconds: float) -> None:
    self.slept.append(seconds)
    self.now += seconds


def pacer(per_minute: int, per_hour: int, clock: Clock) -> Pacer:
  return Pacer(per_minute, per_hour, clock=clock.time, sleep=clock.sleep)


def test_pace_sits_under_the_plan_caps():
  assert PACE[0] < SEC_ADVANCED_PLAN_MCP_CAPS[0]
  assert PACE[1] < SEC_ADVANCED_PLAN_MCP_CAPS[1]


def test_minute_window_holds_the_next_call_until_the_oldest_leaves():
  clock = Clock()
  p = pacer(3, 100, clock)
  assert [p.wait() for _ in range(3)] == [0, 0, 0]
  assert p.wait() == 60  # the fourth within the same second waits the window out
  assert clock.slept == [60] and p.calls == 4 and p.waited_s == 60
  clock.now += 30
  assert p.wait() == 0  # three in the trailing minute: the one at 60 s and this one


def test_hour_window_holds_until_the_next_utc_hour():
  clock = Clock(start=7300.0)  # 100 s into an hour
  p = pacer(1000, 5, clock)
  for _ in range(5):
    assert p.wait() == 0
    clock.now += 1
  waited = p.wait()
  assert waited == 10800 - 7305  # the top of the next hour
  assert p.calls == 6 and p.waited_s == waited
  assert p.wait() == 0  # a fresh hour


def test_client_call_paces_every_tool_call():
  clock = Clock()
  client = McpClient.__new__(McpClient)
  client.pacer = pacer(2, 100, clock)
  client._session = SimpleNamespace(call_tool=lambda name, args: (name, args))
  client._run = lambda coro: SimpleNamespace(  # type: ignore[method-assign]
    content=[SimpleNamespace(text='{"ok": true}')], isError=False
  )
  for _ in range(3):
    assert client.call("describe-filing", {"ticker": "MMM"}) == '{"ok": true}'
  assert client.pacer.calls == 3 and clock.slept == [60]
