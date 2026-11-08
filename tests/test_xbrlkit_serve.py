"""Rung 4c and the v0.1.2 document instrument: xbrlkit's server in-process."""

import asyncio
import json
from pathlib import Path

import pytest

from filing_ladder.ladder import (
  BY_RUNG,
  V0_1_2_RUNGS,
  Rung,
  Shape,
  base_rung,
  carries_document,
  parse_rungs,
  uses_mcp,
)
from filing_ladder.prompts import SOURCES
from filing_ladder.providers.base import ToolDef
from filing_ladder.representations import xbrlkit_serve as xk

MMM = Path("data/0000066740-25-000006/package")


def _registered_names() -> set[str]:
  from xbrlkit.serve import FilingSession, build_server

  server = build_server(FilingSession(), graph_tools=True)
  return {t.name for t in asyncio.run(server.list_tools())}


def test_every_server_tool_is_either_given_or_withheld_for_a_reason():
  names = _registered_names()
  assert set(xk.SERVE_TOOLS) <= names
  assert set(xk.WITHHELD) <= names
  # A tool xbrlkit adds later must be placed, not defaulted into the rung.
  assert names == set(xk.SERVE_TOOLS) | set(xk.WITHHELD)
  assert not set(xk.SERVE_TOOLS) & set(xk.WITHHELD)
  assert "run_cypher" in xk.WITHHELD and set(xk.DOCUMENT_TOOLS) <= set(xk.SERVE_TOOLS)


def test_rung_4c_is_a_rung_in_the_v0_1_2_lineup_and_needs_no_server():
  spec = BY_RUNG[Rung.XBRLKIT_SERVE]
  assert spec.shape == Shape.TOOLS and not spec.control and not spec.v0
  assert spec.needs == () and not uses_mcp(Rung.XBRLKIT_SERVE)
  assert base_rung(Rung.XBRLKIT_SERVE) == Rung.XBRLKIT_SERVE
  assert not carries_document(Rung.XBRLKIT_SERVE)
  assert parse_rungs("v0.1.2") == list(V0_1_2_RUNGS)
  assert V0_1_2_RUNGS[0] == Rung.XBRLKIT_SERVE and V0_1_2_RUNGS[-1] == Rung.HTML_TEXT
  assert Rung.XBRLKIT_SERVE not in parse_rungs("v0")
  assert Rung.XBRLKIT_SERVE not in parse_rungs("v0.1.1")


def test_prompts_name_the_tools_the_model_has():
  for name in xk.SERVE_TOOLS:
    assert name in SOURCES[Rung.XBRLKIT_SERVE], name
  assert "Call describe_filing FIRST" in SOURCES[Rung.XBRLKIT_SERVE]
  for name in (
    "describe-filing",
    "disclosures",
    "information-block",
    "search-text",
    "read-text",
  ):
    assert name in SOURCES[Rung.LPG_SHAPED], name


def test_runner_refuses_a_tool_outside_the_rung():
  class Fake:
    def call(self, name, args):
      return json.dumps({"ok": name})

  run = xk.make_tool_runner(Fake(), ("search_text",))  # type: ignore[arg-type]
  assert json.loads(run("search_text", {"pattern": "x"})) == {"ok": "search_text"}
  assert "not available" in run("run_cypher", {"query": "MATCH (n) RETURN n"})


def test_beside_adds_exactly_the_two_text_tools_and_dispatches():
  class Fake:
    def tool_defs(self, names):
      return [ToolDef(n, f"xbrlkit's {n}", {"type": "object"}) for n in names]

    def call(self, name, args):
      return json.dumps({"from": "xbrlkit", "tool": name})

  own = [ToolDef("run_jq", "jq", {"type": "object"})]
  tools, run = xk.beside(own, lambda n, a: json.dumps({"from": "rung"}), Fake())  # type: ignore[arg-type]
  assert [t.name for t in tools] == ["run_jq", "search_text", "read_text"]
  assert tools[1].description == "xbrlkit's search_text"
  assert json.loads(run("read_text", {"offset": 0}))["from"] == "xbrlkit"
  assert json.loads(run("run_jq", {"program": "."}))["from"] == "rung"
  assert "unknown tool" in xk.beside(own, None, Fake())[1]("run_jq", {})  # type: ignore[arg-type]


@pytest.mark.skipif(not MMM.exists(), reason="the corpus is not materialized here")
def test_a_corpus_filing_loads_from_its_package_with_its_document():
  sf = xk.served(MMM)
  assert sf.filing.has_document and sf.filing.read_from.get("kind", "file") in (
    "file",
    "",
  )
  assert sf.text_chars > 300_000  # the whole primary document, not the text blocks
  tools = sf.tool_defs(xk.SERVE_TOOLS)
  assert [t.name for t in tools] == list(xk.SERVE_TOOLS)
  assert "Follow up with read_text" in tools[-2].description
  hit = json.loads(
    sf.call("search_text", {"pattern": "research, development and related"})
  )
  assert hit["total"] >= 1 and "section" in hit["hits"][0]
  page = json.loads(
    sf.call("read_text", {"offset": hit["hits"][0]["offset"], "length": 200})
  )
  assert page["length"] == 200 and "next_offset" in page
  assert "error" in json.loads(sf.call("read_text", {"offset": 10**9}))
  assert "not available" in xk.make_tool_runner(sf, xk.SERVE_TOOLS)("run_cypher", {})
  assert "error" in json.loads(sf.call("no_such_tool", {}))
