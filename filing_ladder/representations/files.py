"""Rungs 4 and 5a — files on disk behind three tools: list, read a line range, grep.

Nothing is parsed for the model; the XBRL package (rung 4) or the OIM export (rung 5a) is
exactly what the publisher ships, and the model has to find its way through it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable

from ..providers.base import ToolDef
from .companyfacts import clip

MAX_LINES = 200
MAX_HITS = 60


class FileTools:
  def __init__(self, root: Path) -> None:
    self.root = root.resolve()

  def _resolve(self, name: str) -> Path:
    path = (self.root / name).resolve()
    if self.root not in path.parents and path != self.root:
      raise ValueError("path escapes the filing directory")
    if not path.is_file():
      raise FileNotFoundError(name)
    return path

  def list_files(self) -> list[dict]:
    return [
      {
        "name": p.relative_to(self.root).as_posix(),
        "bytes": p.stat().st_size,
        "lines": _line_count(p),
      }
      for p in sorted(self.root.rglob("*"))
      if p.is_file()
    ]

  def read_lines(self, name: str, start: int = 1, count: int = 100) -> dict:
    path = self._resolve(name)
    count = max(1, min(int(count), MAX_LINES))
    start = max(1, int(start))
    out: list[str] = []
    with path.open(encoding="utf-8", errors="replace") as fh:
      for i, line in enumerate(fh, start=1):
        if i < start:
          continue
        if i >= start + count:
          break
        out.append(f"{i}: {line.rstrip()[:2000]}")
    return {"file": name, "start": start, "returned": len(out), "text": "\n".join(out)}

  def grep(
    self, pattern: str, name: str | None = None, max_hits: int = MAX_HITS
  ) -> dict:
    rx = re.compile(pattern, re.I)
    hits: list[dict] = []
    files = (
      [self._resolve(name)]
      if name
      else [p for p in sorted(self.root.rglob("*")) if p.is_file()]
    )
    for path in files:
      with path.open(encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh, start=1):
          if rx.search(line):
            hits.append(
              {
                "file": path.relative_to(self.root).as_posix(),
                "line": i,
                "text": line.strip()[:400],
              }
            )
            if len(hits) >= max_hits:
              return {"pattern": pattern, "hits": hits, "truncated": True}
    return {"pattern": pattern, "hits": hits, "truncated": False}


def _line_count(path: Path) -> int:
  with path.open("rb") as fh:
    return sum(1 for _ in fh)


TOOL_DEFS: list[ToolDef] = [
  ToolDef(
    "list_files",
    "List the files in the filing directory with sizes and line counts.",
    {"type": "object", "properties": {}},
  ),
  ToolDef(
    "read_lines",
    f"Read up to {MAX_LINES} lines of one file starting at a line number (1-based).",
    {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "start": {"type": "integer"},
        "count": {"type": "integer"},
      },
      "required": ["name"],
    },
  ),
  ToolDef(
    "grep",
    f"Case-insensitive regular-expression search across the files (or one file); returns up to {MAX_HITS} matching lines with line numbers.",
    {
      "type": "object",
      "properties": {"pattern": {"type": "string"}, "name": {"type": "string"}},
      "required": ["pattern"],
    },
  ),
]


def make_tool_runner(tools: FileTools) -> Callable[[str, dict], str]:
  def run(name: str, args: dict) -> str:
    if name == "list_files":
      return clip(json.dumps(tools.list_files()))
    if name == "read_lines":
      return clip(
        json.dumps(
          tools.read_lines(args["name"], args.get("start", 1), args.get("count", 100))
        )
      )
    if name == "grep":
      return clip(json.dumps(tools.grep(args["pattern"], args.get("name"))))
    return json.dumps({"error": f"unknown tool {name}"})

  return run
