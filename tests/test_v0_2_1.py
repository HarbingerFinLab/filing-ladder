"""Protocol v0.2.1 (PROTOCOL §12): two rows beside 4c and 7a, each its base with one friction removed."""

from filing_ladder.ladder import (
  BY_RUNG,
  V0_2_1_RUNGS,
  V0_2_RUNGS,
  Rung,
  Shape,
  base_rung,
  carries_document,
  parse_rungs,
  uses_mcp,
)
from filing_ladder.prompts import SOURCES, system_prompt
from filing_ladder.providers.base import ToolDef
from filing_ladder.representations import xbrlkit_serve as xk

MCP_TOOLS_7A = (
  "financial-statement-analysis",
  "build-fact-grid",
  "resolve-element",
  "describe-filing",
  "disclosures",
  "information-block",
  "search-text",
  "read-text",
  "search-documents",
  "read-graph-cypher",
  "get-example-queries",
  "get-graph-schema",
)


def test_v0_2_1_is_two_rows_built_on_4c_and_7a():
  assert parse_rungs("v0.2.1") == list(V0_2_1_RUNGS)
  assert V0_2_1_RUNGS == (Rung.XBRLKIT_SERVE_V021, Rung.LPG_SHAPED_V021)
  for rung in V0_2_1_RUNGS:
    spec = BY_RUNG[rung]
    assert spec.shape == Shape.TOOLS and not spec.control and not spec.v0
    assert rung not in V0_2_RUNGS and rung not in parse_rungs("v0")
    assert rung not in parse_rungs("v0.1.1")
    assert not carries_document(rung)
  assert base_rung(Rung.XBRLKIT_SERVE_V021) == Rung.XBRLKIT_SERVE
  assert base_rung(Rung.LPG_SHAPED_V021) == Rung.LPG_SHAPED
  assert uses_mcp(Rung.LPG_SHAPED_V021) and not uses_mcp(Rung.XBRLKIT_SERVE_V021)
  assert BY_RUNG[Rung.LPG_SHAPED_V021].needs == BY_RUNG[Rung.LPG_SHAPED].needs
  assert BY_RUNG[Rung.XBRLKIT_SERVE_V021].needs == ()


def test_4c_1_prompt_is_4c_s_word_for_word():
  assert SOURCES[Rung.XBRLKIT_SERVE_V021] is SOURCES[Rung.XBRLKIT_SERVE]
  assert system_prompt(Rung.XBRLKIT_SERVE_V021) == system_prompt(Rung.XBRLKIT_SERVE)


def test_7a_1_prompt_differs_from_7a_s_in_steps_1_and_2_only():
  old, new = SOURCES[Rung.LPG_SHAPED], SOURCES[Rung.LPG_SHAPED_V021]
  assert old != new
  old_source, old_steps = old.split("Workflow:")
  new_source, new_steps = new.split("Workflow:")
  assert old_source == new_source  # the paragraph saying what the model has
  old_lines, new_lines = old_steps.split("\n"), new_steps.split("\n")
  assert len(old_lines) == len(new_lines) == 5  # "", then steps 1-4
  assert old_lines[3:] == new_lines[3:]  # steps 3 and 4 untouched
  assert old_lines[1].startswith(
    "1. Call get-example-queries and get-graph-schema first"
  )
  assert "get-example-queries" not in new_lines[1]
  assert new_lines[1].startswith("1. Start with the shaped tool the question calls for")
  assert "read-graph-cypher" in new_lines[2] and "get-example-queries" in new_lines[2]
  for name in MCP_TOOLS_7A:
    assert name in old and name in new, name
  # The skeleton around the source is the same.
  assert system_prompt(Rung.LPG_SHAPED_V021).replace(new, "") == system_prompt(
    Rung.LPG_SHAPED
  ).replace(old, "")


def test_4c_1_refuses_an_xbrlkit_without_the_aliases():
  def tool(name: str, *props: str) -> ToolDef:
    return ToolDef(name, "", {"type": "object", "properties": {p: {} for p in props}})

  before = [tool("fact_grid", "elements"), tool("resolve_element", "query")]
  after = [
    tool("fact_grid", "elements", "concepts"),
    tool("resolve_element", "query", "phrase"),
  ]
  assert not xk.accepts_aliases(before) and xk.accepts_aliases(after)
  assert not xk.accepts_aliases([]) and not xk.accepts_aliases(after[:1])
