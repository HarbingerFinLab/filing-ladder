"""The tool loop — one question, one rung, one model, with every cost line recorded.

Errors from tools are returned to the model for correction, not swallowed; the loop stops at
the turn budget and reports it. Everything the essay needs is in the ``Transcript``: turns,
tool calls, tool errors, empty query results, tokens by kind, wall-clock, and the final text.
"""

from __future__ import annotations

import json
import time
import traceback
from dataclasses import asdict, dataclass, field
from typing import Callable

from .providers.base import Attachment, CannotAttempt, Provider, ToolDef, Usage

ToolRunner = Callable[[str, dict], str]


@dataclass
class ToolEvent:
  turn: int
  name: str
  args: dict
  result_chars: int
  is_error: bool
  empty_result: bool
  elapsed_s: float


@dataclass
class Transcript:
  rung: str
  question_id: str
  run_index: int
  provider: str
  model: str
  turns: int = 0
  tool_calls: int = 0
  tool_errors: int = 0
  usage: dict = field(default_factory=dict)
  turn_usage: list[dict] = field(default_factory=list)
  wall_s: float = 0.0
  stop_reason: str = ""
  final_text: str = ""
  citations: list[dict] = field(default_factory=list)
  tool_events: list[ToolEvent] = field(default_factory=list)
  cannot_attempt: str | None = None
  error: str | None = None
  messages: list[dict] = field(default_factory=list)

  def as_dict(self) -> dict:
    d = asdict(self)
    return d


def run_question(
  provider: Provider,
  rung: str,
  question_id: str,
  run_index: int,
  system: str,
  user_text: str,
  attachments: list[Attachment],
  tools: list[ToolDef],
  tool_runner: ToolRunner | None,
  max_turns: int = 12,
) -> Transcript:
  t = Transcript(rung, question_id, run_index, provider.name, provider.model)
  usage = Usage()
  t0 = time.monotonic()
  try:
    conversation = provider.start(system, user_text, attachments, tools)
    for turn_index in range(1, max_turns + 1):
      t.turns = turn_index
      turn = provider.step(conversation)
      usage.add(turn.usage)
      t.turn_usage.append(turn.usage.as_dict())
      t.citations.extend(turn.citations)
      if not turn.tool_calls:
        t.final_text = turn.text
        t.stop_reason = turn.stop_reason
        break
      results = []
      for call in turn.tool_calls:
        t.tool_calls += 1
        started = time.monotonic()
        if tool_runner is None:
          text, is_error = json.dumps({"error": "no tools on this rung"}), True
        else:
          try:
            text, is_error = tool_runner(call.name, call.args), False
            if text.lstrip().startswith('{"error"'):
              is_error = True
          except Exception as exc:  # returned to the model, never swallowed
            text, is_error = json.dumps({"error": f"{type(exc).__name__}: {exc}"}), True
        t.tool_errors += int(is_error)
        t.tool_events.append(
          ToolEvent(
            turn_index,
            call.name,
            call.args,
            len(text),
            is_error,
            _looks_empty(text),
            time.monotonic() - started,
          )
        )
        results.append((call, text, is_error))
      provider.add_tool_results(conversation, results)
      if turn.text and turn_index == max_turns:
        t.final_text = turn.text
    else:
      t.stop_reason = "max_turns"
    t.messages = provider.serialize(conversation)
  except CannotAttempt as exc:
    t.cannot_attempt = str(exc)
    t.stop_reason = "cannot_attempt"
  except Exception as exc:
    t.error = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()[-1500:]}"
    t.stop_reason = "error"
  t.usage = usage.as_dict()
  t.wall_s = round(time.monotonic() - t0, 3)
  return t


def _looks_empty(text: str) -> bool:
  """An empty query result — the silent-failure input for the empty-result-answered metric."""
  s = text.strip()
  if s in ("", "[]", "{}", "null"):
    return True
  if (
    '"row_count":0' in s
    or '"row_count": 0' in s
    or '"rows":[]' in s
    or '"rows": []' in s
  ):
    return True
  if (
    s.startswith("0 rows")
    or "returned 0 rows" in s.lower()
    or "no results" in s.lower()
  ):
    return True
  return False
