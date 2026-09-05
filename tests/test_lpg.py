import json
from pathlib import Path

import pytest

from filing_ladder.representations import lpg

ladybug = pytest.importorskip("ladybug")


def tiny_graph(path: Path) -> Path:
  """A three-table graph in the sec schema's shape, enough for describe and a query."""
  db = ladybug.Database(str(path))
  conn = ladybug.Connection(db)
  conn.execute(
    "CREATE NODE TABLE Entity(identifier STRING, name STRING, PRIMARY KEY(identifier))"
  )
  conn.execute(
    "CREATE NODE TABLE Report(identifier STRING, form STRING, fiscal_year_focus INT32, "
    "fiscal_period_focus STRING, accession_number STRING, filing_date STRING, PRIMARY KEY(identifier))"
  )
  conn.execute(
    "CREATE NODE TABLE Element(identifier STRING, qname STRING, is_textblock BOOLEAN, PRIMARY KEY(identifier))"
  )
  conn.execute(
    "CREATE NODE TABLE Label(identifier STRING, value STRING, type STRING, PRIMARY KEY(identifier))"
  )
  conn.execute(
    "CREATE NODE TABLE Period(identifier STRING, period_type STRING, start_date STRING, end_date STRING, "
    "duration_type STRING, PRIMARY KEY(identifier))"
  )
  conn.execute(
    "CREATE NODE TABLE Unit(identifier STRING, measure STRING, PRIMARY KEY(identifier))"
  )
  conn.execute(
    "CREATE NODE TABLE Fact(identifier STRING, value STRING, numeric_value DOUBLE, has_dimensions BOOLEAN, PRIMARY KEY(identifier))"
  )
  for rel in (
    "ENTITY_HAS_REPORT(FROM Entity TO Report)",
    "FACT_HAS_ELEMENT(FROM Fact TO Element)",
    "FACT_HAS_PERIOD(FROM Fact TO Period)",
    "FACT_HAS_UNIT(FROM Fact TO Unit)",
    "ELEMENT_HAS_LABEL(FROM Element TO Label)",
  ):
    conn.execute(f"CREATE REL TABLE {rel}")
  conn.execute("CREATE (:Entity {identifier: 'en', name: '3M CO'})")
  conn.execute(
    "CREATE (:Report {identifier: 'r', form: '10-K', fiscal_year_focus: 2024, fiscal_period_focus: 'FY', "
    "accession_number: '0000066740-25-000006', filing_date: '2025-02-05'})"
  )
  conn.execute(
    "MATCH (e:Entity {identifier: 'en'}), (r:Report {identifier: 'r'}) CREATE (e)-[:ENTITY_HAS_REPORT]->(r)"
  )
  conn.execute(
    "CREATE (:Element {identifier: 'el', qname: 'us-gaap:Revenues', is_textblock: false})"
  )
  conn.execute(
    f"CREATE (:Label {{identifier: 'l', value: 'Revenues', type: '{lpg.STANDARD_LABEL}'}})"
  )
  conn.execute(
    "MATCH (e:Element {identifier: 'el'}), (l:Label {identifier: 'l'}) CREATE (e)-[:ELEMENT_HAS_LABEL]->(l)"
  )
  conn.execute(
    "CREATE (:Period {identifier: 'p', period_type: 'duration', start_date: '2024-01-01', end_date: '2024-12-31', duration_type: 'annual'})"
  )
  conn.execute("CREATE (:Unit {identifier: 'u', measure: 'iso4217:USD'})")
  conn.execute(
    "CREATE (:Fact {identifier: 'f', value: '24575000000', numeric_value: 24575000000.0, has_dimensions: false})"
  )
  conn.execute("MATCH (f:Fact), (e:Element) CREATE (f)-[:FACT_HAS_ELEMENT]->(e)")
  conn.execute("MATCH (f:Fact), (p:Period) CREATE (f)-[:FACT_HAS_PERIOD]->(p)")
  conn.execute("MATCH (f:Fact), (u:Unit) CREATE (f)-[:FACT_HAS_UNIT]->(u)")
  conn.close()
  db.close()
  return path


@pytest.fixture
def graph(tmp_path: Path) -> Path:
  return tiny_graph(tmp_path / "filing.lbug")


def test_describe_graph_is_computed_from_the_database(graph: Path):
  text = lpg.describe_graph(graph)
  assert (
    "Report: 3M CO — form 10-K, fiscal year 2024 FY, accession 0000066740-25-000006"
    in text
  )
  assert (
    "Fact: identifier STRING, value STRING, numeric_value DOUBLE, has_dimensions BOOL"
    in text
  )
  assert "(Fact)-[:FACT_HAS_ELEMENT]->(Element) | 1" in text
  assert '- us-gaap:Revenues → "Revenues" (1 facts)' in text
  assert "2024-01-01 → 2024-12-31 (annual): 1 facts" in text
  assert "iso4217:USD: 1 facts" in text
  assert "# Read a note." in text and "run_cypher" not in text
  assert (
    lpg.summary_note(graph)
    == f"1 facts, 1 elements, {graph.stat().st_size / 1e6:.0f} MB"
  )


def test_run_cypher_returns_rows_and_counts(graph: Path):
  out = json.loads(
    lpg.run_cypher(
      graph,
      "MATCH (f:Fact)-[:FACT_HAS_ELEMENT]->(e:Element) RETURN e.qname, f.numeric_value LIMIT 5",
      timeout_s=30,
    )
  )
  assert out["columns"] == ["e.qname", "f.numeric_value"]
  assert out["rows"] == [
    {"e.qname": "us-gaap:Revenues", "f.numeric_value": 24575000000.0}
  ]
  assert out["row_count"] == 1


def test_run_cypher_caps_rows_and_explains_empty_results(graph: Path):
  out = json.loads(
    lpg.run_cypher(graph, "UNWIND [1,2,3] AS n RETURN n", max_rows=2, timeout_s=30)
  )
  assert (
    out["row_count"] == 3 and len(out["rows"]) == 2 and "showing 2 of 3" in out["note"]
  )
  out = json.loads(
    lpg.run_cypher(
      graph, "MATCH (e:Element {qname: 'nope'}) RETURN e.qname", timeout_s=30
    )
  )
  assert out["row_count"] == 0 and "0 rows" in out["note"]


def test_run_cypher_rejects_writes_and_reports_errors(graph: Path):
  for bad in (
    "CREATE (:Fact {identifier: 'x'})",
    "MATCH (f:Fact) SET f.value = 'x' RETURN f",
    "MATCH (f:Fact) DELETE f",
    "COPY Fact FROM 'x.parquet'",
  ):
    assert (
      "Only read-only Cypher"
      in json.loads(lpg.run_cypher(graph, bad, timeout_s=30))["error"]
    )
  out = json.loads(
    lpg.run_cypher(graph, "MATCH (f:Nope) RETURN f.value LIMIT 1", timeout_s=30)
  )
  assert out["error"].startswith("Cypher error")


def test_run_cypher_times_out(graph: Path, monkeypatch):
  import time

  def slow(path, query, max_rows):
    time.sleep(5)
    return "{}"

  monkeypatch.setattr(lpg, "_evaluate", slow)
  out = json.loads(
    lpg.run_cypher(graph, "MATCH (f:Fact) RETURN f LIMIT 1", timeout_s=0.5)
  )
  assert "timed out" in out["error"]


def test_tool_runner_serves_both_tools(graph: Path):
  run = lpg.make_tool_runner(graph)
  assert "Report: 3M CO" in run("describe_graph", {})
  assert json.loads(run("run_cypher", {"query": "MATCH (r:Report) RETURN r.form"}))[
    "rows"
  ] == [{"r.form": "10-K"}]
  assert "unknown tool" in run("nope", {})
