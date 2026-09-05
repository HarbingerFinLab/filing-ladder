from filing_ladder.ladder import RUNGS, Rung, Shape
from filing_ladder.prompts import SOURCES, system_prompt


def test_every_rung_has_a_source_paragraph():
  """A rung without one crashes the run at the first question, after the plan printed."""
  missing = [rung for rung in Rung if rung not in SOURCES]
  assert missing == []
  for rung in Rung:
    prompt = system_prompt(rung)
    assert "ANSWER:" in prompt and SOURCES[rung] in prompt


def test_tool_rungs_describe_a_workflow_and_in_context_rungs_do_not():
  for spec in RUNGS:
    has_workflow = "Workflow:" in SOURCES[spec.rung]
    assert has_workflow == (spec.shape == Shape.TOOLS), spec.rung


def test_raw_query_rungs_are_worded_in_parallel():
  for rung, describe, query in (
    (Rung.TAVI_JQ, "describe_model", "run_jq"),
    (Rung.RDF_SPARQL, "describe_report", "run_sparql"),
    (Rung.LPG_CYPHER, "get-graph-schema", "read-graph-cypher"),
  ):
    source = SOURCES[rung]
    assert f"Call {describe} FIRST" in source and query in source
