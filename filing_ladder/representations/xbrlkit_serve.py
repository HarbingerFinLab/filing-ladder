"""Rung 4c — ``xbrlkit serve``: the filing's XBRL package behind xbrlkit's shaped tools — and,
for protocol v0.2's "+doc" controls, xbrlkit's two text tools as the document instrument.

The server is the one ``xbrlkit serve`` runs: ``xbrlkit.serve.build_server`` over a
``FilingSession`` holding the filing parsed from the package folder on disk (``read_from:
file`` — the filing as filed; no CDN, no EDGAR, no network), built in-process and called through
its own ``call_tool``, so the tools, their descriptions, their argument schemas and their answers
are the library's and not the harness's. Only the Streamable HTTP transport is left out; the
transport is not a variable.

Product profile, the document on: what ``uvx xbrlkit serve <package>`` gives a reader. ``--pure``
(a faithful reading of the filing and nothing more — the ladder's v0.1.1 hit shape and read cap)
exists for a replication wanting parity with the v0.1.1 "+doc" rows, and is not run.

Tools withheld from the rung, each for a reason (PROTOCOL §11): see ``WITHHELD``.
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Any, Callable

from ..providers.base import ToolDef
from .companyfacts import clip

# The analytical surface of an XBRL report, in the order the model is shown them.
SERVE_TOOLS: tuple[str, ...] = (
  "describe_filing",
  "resolve_element",
  "fact_grid",
  "statement",
  "calculation",
  "disclosures",
  "information_block",
  "search_text",
  "read_text",
)
DOCUMENT_TOOLS: tuple[str, ...] = ("search_text", "read_text")

# Protocol v0.2.1, rung 4c.1: the argument name each tool takes beside its original (xbrlkit 0.21.5).
ALIASES: dict[str, tuple[str, str]] = {
  "fact_grid": ("elements", "concepts"),
  "resolve_element": ("query", "phrase"),
}


def accepts_aliases(tools: list[ToolDef]) -> bool:
  """Whether the served tools take the v0.2.1 argument aliases; 4c.1 does not run otherwise."""
  by_name = {t.name: t for t in tools}
  return all(
    name in by_name
    and set(pair) <= set(by_name[name].input_schema.get("properties", {}))
    for name, pair in ALIASES.items()
  )


# Every other tool the server registers, with why the rung does not get it. A tool the
# library adds later lands in neither set and fails the registration test, so the decision
# is taken rather than defaulted.
WITHHELD: dict[str, str] = {
  "run_cypher": "raw Cypher over the same file is rung 7b",
  "load_filing": "the one-filing frame: a second filing is not the question's",
  "unload_filing": "the one-filing frame",
  "list_filings": "housekeeping (7a withholds list-subgraphs and get-graph-info the same way)",
  "search_filings": "the SEC's EDGAR full-text search — the publisher's surface, the 6+efts control",
  "export_filing": "a side effect, not an answer",
  "view_filing": "a side effect, not an answer",
  "documents": "the filing's other documents (exhibits): more than the one primary document every other rung has",
  "read_document": "the filing's other documents (exhibits), as above",
  "records": "the XML-lane tool (Forms 3/4/5, 13F, N-PORT); not applicable to an XBRL report",
}


class ServedFiling:
  """One filing behind xbrlkit's server, in-process."""

  def __init__(
    self, package_dir: Path, *, pure: bool = False, with_document: bool = True
  ) -> None:
    from xbrlkit.serve import FilingSession, build_server

    self.package_dir = Path(package_dir)
    self.pure = pure
    self.with_document = with_document
    self.session = FilingSession()
    self.filing = self.session.load(str(self.package_dir))
    # export_filing is withheld; the server still needs somewhere it may write.
    out_dir = Path(tempfile.gettempdir()) / "filing-ladder-xbrlkit"
    self.server = build_server(
      self.session,
      out_dir,
      pure=pure,
      with_document=with_document,
      graph_tools=False,
    )
    self._tools: list[ToolDef] | None = None

  @staticmethod
  def _run(coro: Any) -> Any:
    return asyncio.run(coro)

  def all_tools(self) -> list[ToolDef]:
    if self._tools is None:
      self._tools = tool_defs_from(self._run(self.server.list_tools()))
    return list(self._tools)

  def tool_defs(self, names: tuple[str, ...]) -> list[ToolDef]:
    """The server's own definitions of ``names``, in that order; a name the server does
    not register is an error, never silently dropped."""
    by_name = {t.name: t for t in self.all_tools()}
    missing = [n for n in names if n not in by_name]
    if missing:
      raise KeyError(f"xbrlkit serve registers no tool named {missing}")
    return [by_name[n] for n in names]

  def call(self, name: str, args: dict) -> str:
    try:
      result = self._run(self.server.call_tool(name, dict(args or {})))
    except Exception as exc:  # an argument the schema refused, an unknown tool
      return json.dumps({"error": f"{type(exc).__name__}: {exc}"})
    texts = [
      getattr(block, "text", None) for block in getattr(result, "content", []) or []
    ]
    body = "\n".join(t for t in texts if t is not None)
    if getattr(result, "is_error", False):
      return json.dumps({"error": body})
    return clip(body)

  @property
  def text_chars(self) -> int:
    text, _ = self.filing.readable(self.with_document)
    return len(text)

  def note(self) -> str:
    lf = self.filing
    read_from = lf.read_from.get("source") or lf.read_from.get("kind") or "file"
    return (
      f"xbrlkit {_version()}: {len(lf.model.facts):,} facts, "
      f"{self.text_chars:,} chars of {'document' if lf.has_document else 'text blocks'}, "
      f"read_from={read_from}"
    )


def _schema(tool: Any) -> dict:
  """The server's own argument schema, under the attribute mcp 2.x gives it or the wire name.
  v0.2 read the wire name alone and defaulted to ``{"type": "object"}`` (PROTOCOL §9, 2026-11-09)."""
  schema = getattr(tool, "input_schema", None) or getattr(tool, "inputSchema", None)
  if not isinstance(schema, dict) or not isinstance(schema.get("properties"), dict):
    raise RuntimeError(f"xbrlkit serve listed {tool.name!r} without an argument schema")
  return dict(schema)


def tool_defs_from(listed: list[Any]) -> list[ToolDef]:
  """The server's tools as the model will see them: name, description, and its own schema."""
  return [ToolDef(t.name, t.description or "", _schema(t)) for t in listed]


def _version() -> str:
  from xbrlkit import __version__

  return __version__


_SERVED: dict[Path, ServedFiling] = {}


def served(package_dir: Path) -> ServedFiling:
  """One loaded filing per package folder for the whole run: the rung and the "+doc"
  controls on the same filing share it."""
  key = Path(package_dir).resolve()
  if key not in _SERVED:
    _SERVED[key] = ServedFiling(key)
  return _SERVED[key]


def make_tool_runner(
  sf: ServedFiling, allowed: tuple[str, ...]
) -> Callable[[str, dict], str]:
  names = set(allowed)

  def run(name: str, args: dict) -> str:
    if name not in names:
      return json.dumps({"error": f"tool {name} is not available on this rung"})
    return sf.call(name, args)

  return run


def beside(
  tools: list[ToolDef],
  runner: Callable[[str, dict], str] | None,
  sf: ServedFiling,
) -> tuple[list[ToolDef], Callable[[str, dict], str]]:
  """A rung's own tools plus xbrlkit's two text tools, one runner dispatching between them
  (protocol v0.2's document instrument; v0.1.1's is ``document.beside``)."""
  doc_run = make_tool_runner(sf, DOCUMENT_TOOLS)

  def run(name: str, args: dict) -> str:
    if name in DOCUMENT_TOOLS:
      return doc_run(name, args)
    if runner is None:
      return json.dumps({"error": f"unknown tool {name}"})
    return runner(name, args)

  return [*tools, *sf.tool_defs(DOCUMENT_TOOLS)], run
