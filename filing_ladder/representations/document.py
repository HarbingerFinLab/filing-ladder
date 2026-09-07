"""The filing's primary document as plain text behind two tools: search_text and read_text.

The constant for protocol v0.1.1: the same two tools, the same descriptions and caps, on every
tool rung that carries the document beside its own material, and the only tools on rung 2t.
The text is rung 2's — the EDGAR primary document with its tags stripped — never re-chunked or
re-ordered. It is one line of several hundred thousand characters, so the tools work on
character offsets, not lines.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable

from ..providers.base import ToolDef
from .companyfacts import clip

WINDOW = 300
MAX_WINDOW = 1_500
MAX_HITS = 10
HARD_MAX_HITS = 25
MAX_READ = 4_000
TOOL_NAMES = ("search_text", "read_text")


class DocumentText:
  def __init__(self, path: Path) -> None:
    self.text = path.read_text(encoding="utf-8", errors="replace")

  @property
  def chars(self) -> int:
    return len(self.text)

  def search(
    self, pattern: str, window: int = WINDOW, max_hits: int = MAX_HITS
  ) -> dict:
    window = max(40, min(int(window), MAX_WINDOW))
    max_hits = max(1, min(int(max_hits), HARD_MAX_HITS))
    try:
      rx = re.compile(pattern, re.I)
    except re.error as exc:
      return {"error": f"bad pattern: {exc}"}
    half = window // 2
    hits: list[dict] = []
    total = 0
    for m in rx.finditer(self.text):
      total += 1
      if len(hits) < max_hits:
        start = max(0, m.start() - half)
        end = min(len(self.text), m.end() + half)
        hits.append({"offset": m.start(), "window": self.text[start:end]})
    return {
      "pattern": pattern,
      "total_matches": total,
      "returned": len(hits),
      "hits": hits,
      "document_chars": len(self.text),
    }

  def read(self, offset: int, length: int = MAX_READ) -> dict:
    offset = max(0, min(int(offset), len(self.text)))
    length = max(1, min(int(length), MAX_READ))
    span = self.text[offset : offset + length]
    return {
      "offset": offset,
      "length": len(span),
      "text": span,
      "document_chars": len(self.text),
    }


TOOL_DEFS: list[ToolDef] = [
  ToolDef(
    "search_text",
    "Case-insensitive regular-expression search over the filing's primary document as plain "
    f"text. Returns up to {MAX_HITS} matches (max {HARD_MAX_HITS}), each with its character "
    f"offset and a window of text centred on it (default {WINDOW} characters, max "
    f"{MAX_WINDOW}), plus the total number of matches. Follow up with read_text at an offset.",
    {
      "type": "object",
      "properties": {
        "pattern": {"type": "string"},
        "window": {"type": "integer"},
        "max_hits": {"type": "integer"},
      },
      "required": ["pattern"],
    },
  ),
  ToolDef(
    "read_text",
    f"Read up to {MAX_READ} characters of the filing's primary document as plain text, "
    "starting at a character offset (from search_text).",
    {
      "type": "object",
      "properties": {"offset": {"type": "integer"}, "length": {"type": "integer"}},
      "required": ["offset"],
    },
  ),
]


def make_tool_runner(doc: DocumentText) -> Callable[[str, dict], str]:
  def run(name: str, args: dict) -> str:
    if name == "search_text":
      return clip(
        json.dumps(
          doc.search(
            args["pattern"], args.get("window", WINDOW), args.get("max_hits", MAX_HITS)
          )
        )
      )
    if name == "read_text":
      return clip(json.dumps(doc.read(args["offset"], args.get("length", MAX_READ))))
    return json.dumps({"error": f"unknown tool {name}"})

  return run


def beside(
  tools: list[ToolDef],
  runner: Callable[[str, dict], str] | None,
  doc: DocumentText,
) -> tuple[list[ToolDef], Callable[[str, dict], str]]:
  """A rung's own tools plus the document's two, one runner dispatching between them."""
  doc_run = make_tool_runner(doc)

  def run(name: str, args: dict) -> str:
    if name in TOOL_NAMES:
      return doc_run(name, args)
    if runner is None:
      return json.dumps({"error": f"unknown tool {name}"})
    return runner(name, args)

  return [*tools, *TOOL_DEFS], run
