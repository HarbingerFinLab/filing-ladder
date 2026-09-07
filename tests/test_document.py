import json

from filing_ladder.providers.base import ToolDef
from filing_ladder.representations.document import (
  HARD_MAX_HITS,
  MAX_READ,
  DocumentText,
  beside,
  make_tool_runner,
)


def _doc(tmp_path, text):
  p = tmp_path / "filing.txt"
  p.write_text(text)
  return DocumentText(p)


def test_search_windows_are_centred_and_offsets_exact(tmp_path):
  text = "a" * 500 + "Elinor Mertz Chief Financial Officer" + "b" * 500
  doc = _doc(tmp_path, text)
  out = doc.search("chief financial officer", window=100)
  assert out["total_matches"] == 1 and out["returned"] == 1
  hit = out["hits"][0]
  assert hit["offset"] == text.index("Chief")
  assert "Elinor Mertz Chief Financial Officer" in hit["window"]
  assert len(hit["window"]) == 100 + len("Chief Financial Officer")


def test_search_caps_and_counts_every_match(tmp_path):
  doc = _doc(tmp_path, "revenue " * 40)
  out = doc.search("revenue", max_hits=3)
  assert out["total_matches"] == 40 and out["returned"] == 3
  assert doc.search("revenue", max_hits=1000)["returned"] == HARD_MAX_HITS


def test_bad_pattern_is_an_error_not_a_crash(tmp_path):
  assert "error" in _doc(tmp_path, "x").search("(")


def test_read_spans_and_clamps(tmp_path):
  doc = _doc(tmp_path, "0123456789" * 1000)
  assert doc.read(5, 4)["text"] == "5678"
  assert doc.read(0, 10**9)["length"] == MAX_READ
  assert doc.read(10**9)["text"] == "" and doc.read(-5, 3)["offset"] == 0


def test_beside_dispatches_between_document_and_the_rungs_own_tools(tmp_path):
  doc = _doc(tmp_path, "Net sales were $24,575 million")
  own = [ToolDef("run_jq", "", {"type": "object"})]
  tools, run = beside(own, lambda name, args: f"own:{name}", doc)
  assert [t.name for t in tools] == ["run_jq", "search_text", "read_text"]
  assert run("run_jq", {}) == "own:run_jq"
  assert json.loads(run("search_text", {"pattern": "net sales"}))["total_matches"] == 1
  assert run("nope", {}) == "own:nope"  # unknown names go to the rung's own runner
  _, alone = beside([], None, doc)
  assert "error" in json.loads(alone("nope", {}))


def test_runner_alone_rejects_unknown(tmp_path):
  run = make_tool_runner(_doc(tmp_path, "x"))
  assert "error" in json.loads(run("grep", {"pattern": "x"}))
