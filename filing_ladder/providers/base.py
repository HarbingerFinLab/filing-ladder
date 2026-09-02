"""The provider interface: start a conversation, take a step, hand back tool results.

Each provider owns its native message history (``Conversation`` is opaque). The loop only
sees ``Turn``s: text, tool calls, usage, citations.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol, TypeVar


@dataclass(frozen=True)
class ToolDef:
  name: str
  description: str
  input_schema: dict

  @classmethod
  def from_dict(cls, d: dict) -> ToolDef:
    return cls(
      d["name"],
      d.get("description", ""),
      d.get("input_schema") or d.get("inputSchema") or {"type": "object"},
    )


@dataclass(frozen=True)
class ToolCall:
  id: str
  name: str
  args: dict


@dataclass
class Usage:
  input_tokens: int = 0
  output_tokens: int = 0
  cache_read_tokens: int = 0
  cache_write_tokens: int = 0

  def add(self, other: Usage) -> None:
    self.input_tokens += other.input_tokens
    self.output_tokens += other.output_tokens
    self.cache_read_tokens += other.cache_read_tokens
    self.cache_write_tokens += other.cache_write_tokens

  def as_dict(self) -> dict[str, int]:
    return {
      "input_tokens": self.input_tokens,
      "output_tokens": self.output_tokens,
      "cache_read_tokens": self.cache_read_tokens,
      "cache_write_tokens": self.cache_write_tokens,
    }


@dataclass
class Turn:
  text: str
  tool_calls: list[ToolCall]
  usage: Usage
  stop_reason: str
  citations: list[dict] = field(default_factory=list)
  reasoning: str | None = None
  raw: Any = None


@dataclass(frozen=True)
class Attachment:
  """Something handed to the model in context: a PDF (bytes) or a text document (str)."""

  name: str
  media_type: (
    str  # application/pdf | text/plain | text/html | application/json | text/csv
  )
  data: bytes | str

  @property
  def is_pdf(self) -> bool:
    return self.media_type == "application/pdf"


class CannotAttempt(Exception):
  """The rung cannot be attempted on this provider/model (no PDF input, context too small, ...).

  Scored as a miss and reported separately, with whatever it cost to find out.
  """


class Provider(Protocol):
  name: str
  model: str

  def start(
    self,
    system: str,
    user_text: str,
    attachments: list[Attachment],
    tools: list[ToolDef],
  ) -> Any: ...

  def step(self, conversation: Any) -> Turn: ...

  def add_tool_results(
    self, conversation: Any, results: list[tuple[ToolCall, str, bool]]
  ) -> None: ...

  def serialize(self, conversation: Any) -> list[dict]: ...


T = TypeVar("T")


def with_backoff(
  fn: Callable[[], T],
  retryable: Callable[[Exception], bool],
  attempts: int = 8,
  base: float = 2.0,
  cap: float = 120.0,
) -> T:
  """Exponential backoff with full jitter on retryable errors (rate limits, overload, timeouts)."""
  for attempt in range(attempts):
    try:
      return fn()
    except Exception as exc:
      if attempt == attempts - 1 or not retryable(exc):
        raise
      delay = random.uniform(0, min(cap, base * (2**attempt)))
      time.sleep(delay)
  raise AssertionError("unreachable")
