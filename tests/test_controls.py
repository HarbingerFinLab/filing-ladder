import json

import httpx

from filing_ladder.ladder import (
  BY_RUNG,
  CONTROLS_V0_1_1,
  Rung,
  base_rung,
  carries_document,
  parse_rungs,
  uses_mcp,
)
from filing_ladder.prompts import SOURCES, system_prompt
from filing_ladder.providers.base import ToolDef
from filing_ladder.representations.efts import FilingSearch, beside
from filing_ladder.representations.mcp import make_tagged_runner


def test_controls_are_nine_and_not_v0():
  assert len(CONTROLS_V0_1_1) == 9 and parse_rungs("v0.1.1") == list(CONTROLS_V0_1_1)
  assert all(BY_RUNG[r].control and not BY_RUNG[r].v0 for r in CONTROLS_V0_1_1)
  assert parse_rungs("v0") == [r for r in parse_rungs("v0") if not BY_RUNG[r].control]


def test_bases_and_document_flags():
  assert base_rung(Rung.TEXT_SEARCH) is None
  assert base_rung(Rung.LPG_SHAPED_TAGGED) == Rung.LPG_SHAPED
  assert base_rung(Rung.COMPANYFACTS_EFTS) == Rung.COMPANYFACTS
  assert base_rung(Rung.RDF_SPARQL) == Rung.RDF_SPARQL
  assert carries_document(Rung.TEXT_SEARCH) and carries_document(Rung.TAVI_JQ_DOC)
  assert not carries_document(Rung.LPG_SHAPED_TAGGED) and not carries_document(
    Rung.COMPANYFACTS_EFTS
  )
  assert uses_mcp(Rung.LPG_SHAPED_DOC) and uses_mcp(Rung.LPG_SHAPED_TAGGED)
  assert not uses_mcp(Rung.LPG_CYPHER_DOC)


def test_every_control_has_a_prompt_and_the_tagged_one_is_silent():
  for rung in CONTROLS_V0_1_1:
    assert system_prompt(rung)
  assert SOURCES[Rung.LPG_SHAPED_TAGGED] == SOURCES[Rung.LPG_SHAPED]
  assert "search_text" in SOURCES[Rung.RDF_SPARQL_DOC]
  assert "search_filings" in SOURCES[Rung.COMPANYFACTS_EFTS]


class _FakeMcp:
  def __init__(self):
    self.calls = []

  def call(self, name, args):
    self.calls.append((name, args))
    if name == "search-documents":
      return json.dumps(
        {
          "total": 3,
          "hits": [
            {
              "document_id": "n1",
              "source_type": "narrative_section",
              "next_document_id": "n2",
            },
            {
              "document_id": "d1",
              "source_type": "ixbrl_disclosure",
              "next_document_id": "d2",
            },
            {"document_id": "n3", "source_type": "narrative_section"},
          ],
        }
      )
    if name == "get-document-section":
      return json.dumps({"document_id": args["document_id"], "content": "…"})
    return "other"


def test_tagged_runner_drops_narrative_and_refuses_unseen_sections():
  tools = [
    ToolDef(n, "", {"type": "object"})
    for n in ("search-documents", "get-document-section", "build-fact-grid")
  ]
  run = make_tagged_runner(_FakeMcp(), tools)
  out = json.loads(run("search-documents", {"query": "cfo"}))
  assert [h["document_id"] for h in out["hits"]] == ["d1"] and out["total"] == 1
  assert "content" in json.loads(run("get-document-section", {"document_id": "d1"}))
  assert "content" in json.loads(run("get-document-section", {"document_id": "d2"}))
  assert "error" in json.loads(run("get-document-section", {"document_id": "n1"}))
  assert run("build-fact-grid", {}) == "other"
  assert "error" in json.loads(run("read-graph-cypher", {}))


def test_efts_pins_to_the_resolved_filing_and_carries_no_text():
  def handler(request: httpx.Request) -> httpx.Response:
    assert request.url.params["ciks"] == "0001559720"
    assert request.url.params["forms"] == "10-K"
    assert request.url.params["q"] == '"Elinor Mertz"'
    return httpx.Response(
      200,
      json={
        "hits": {
          "total": {"value": 2},
          "hits": [
            {
              "_id": "0001559720-26-000004:exh312.htm",
              "_score": 36.0,
              "_source": {"file_type": "EX-31.2"},
            },
            {
              "_id": "0001559720-25-000010:abnb-20241231.htm",
              "_score": 30.0,
              "_source": {"file_type": "10-K", "file_description": "10-K"},
            },
          ],
        }
      },
    )

  search = FilingSearch(
    "test agent",
    "1559720",
    "0001559720-25-000010",
    "10-K",
    transport=httpx.MockTransport(handler),
  )
  tools, run = beside([], None, search)
  assert [t.name for t in tools] == ["search_filings"]
  out = json.loads(run("search_filings", {"phrase": "Elinor Mertz"}))
  assert out["files_matching"] == 1 and out["hits"][0]["file"] == "abnb-20241231.htm"
  assert "text" not in out["hits"][0] and "content" not in out["hits"][0]
