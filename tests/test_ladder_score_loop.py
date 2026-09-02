from filing_ladder.ladder import BY_RUNG, V0_RUNGS, Rung, Shape, parse_rungs
from filing_ladder.loop import _looks_empty
from filing_ladder.score import Record, aggregate


def test_rungs():
  assert (
    parse_rungs("v0") == list(V0_RUNGS)
    and Rung.PDF in V0_RUNGS
    and Rung.XBRL_PACKAGE not in V0_RUNGS
  )
  assert parse_rungs("2,7c") == [Rung.HTML_TEXT, Rung.RDF_SPARQL]
  assert BY_RUNG[Rung.RDF_SPARQL].shape == Shape.TOOLS


def test_looks_empty():
  assert _looks_empty('{"columns":["x"],"row_count":0,"rows":[]}')
  assert _looks_empty("[]") and not _looks_empty('{"rows":[{"x":1}],"row_count":1}')


def _rec(q, k, correct, abstained=False, extracted=None, cost=0.01):
  return Record(
    "7c",
    q,
    k,
    "T1",
    "lookup",
    "",
    correct,
    abstained,
    False,
    False,
    False,
    True,
    False,
    cost,
    1000,
    100,
    0,
    0,
    2,
    1,
    0,
    1.0,
    extracted,
  )


def test_aggregate_metrics():
  recs = [
    _rec("q1", 1, True, extracted=1.0),
    _rec("q1", 2, True, extracted=1.0),
    _rec("q2", 1, False, extracted=5.0),
    _rec("q2", 2, False, abstained=True),
  ]
  cell = aggregate(recs, by_stratum=False)[0]
  assert cell.n == 4 and cell.questions == 2
  assert (
    cell.accuracy == 0.5 and cell.abstention == 0.25 and cell.confident_wrong == 0.25
  )
  assert cell.repeatability == 0.5
  assert cell.cost_per_question == 0.01 and cell.cost_per_correct == 0.02
