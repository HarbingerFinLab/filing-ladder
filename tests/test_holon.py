from rdflib import RDF, Graph, Literal, Namespace, URIRef

from filing_ladder.representations.holon import (
  PREFIX_BLOCK,
  describe_report,
  run_sparql,
)

RS = Namespace("https://robosystems.ai/vocab/")
XBRLI = Namespace("http://www.xbrl.org/2003/instance#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")


def tiny_graph() -> Graph:
  g = Graph()
  el = URIRef("http://fasb.org/us-gaap/Revenues")
  p = URIRef("urn:p1")
  f = URIRef("urn:f1")
  g.add((el, RDF.type, RS.Element))
  g.add((el, RS.internalId, Literal("us-gaap:Revenues")))
  g.add((el, SKOS.prefLabel, Literal("Revenues")))
  g.add((p, RDF.type, RS.Period))
  g.add((p, XBRLI.periodType, Literal("duration")))
  g.add((p, XBRLI.startDate, Literal("2024-01-01")))
  g.add((p, XBRLI.endDate, Literal("2024-12-31")))
  g.add((p, RS.durationType, Literal("annual")))
  g.add((f, RDF.type, RS.Fact))
  g.add((f, RS.element, el))
  g.add((f, RS.period, p))
  g.add((f, RS.numericValue, Literal(24575.0)))
  return g


def test_describe_and_query():
  g = tiny_graph()
  d = describe_report(g)
  assert "us-gaap:Revenues" in d and "rs:Fact" in d and "Example queries" in d
  q = f"{PREFIX_BLOCK}\nSELECT ?v WHERE {{ ?f a rs:Fact ; rs:numericValue ?v . FILTER NOT EXISTS {{ ?f rs:dimension ?d }} }}"
  out = run_sparql(g, q)
  assert '"row_count":1' in out and "24575" in out


def test_read_only_and_errors():
  g = tiny_graph()
  assert "Only SELECT" in run_sparql(g, "INSERT DATA { <a> <b> <c> }")
  assert "SPARQL error" in run_sparql(g, "SELECT ?x WHERE { ?x ?y")
  assert "0 rows" in run_sparql(
    g, f"{PREFIX_BLOCK}\nSELECT ?x WHERE {{ ?x a rs:Unit }}"
  )


def test_run_sparql_times_out_on_a_runaway_query(monkeypatch):
  import json
  import time

  from rdflib import Graph

  from filing_ladder.representations import holon

  def slow(graph, query, max_rows):
    time.sleep(5)
    return "{}"

  monkeypatch.setattr(holon, "_evaluate", slow)
  out = json.loads(
    holon.run_sparql(Graph(), "SELECT * WHERE { ?s ?p ?o }", timeout_s=0.5)
  )
  assert "timed out" in out["error"]


def test_run_sparql_returns_rows_from_the_child():
  import json

  from rdflib import Graph, Literal, URIRef

  from filing_ladder.representations import holon

  g = Graph()
  g.add((URIRef("urn:a"), URIRef("urn:p"), Literal("x")))
  out = json.loads(holon.run_sparql(g, "SELECT ?o WHERE { ?s ?p ?o }", timeout_s=10))
  assert out["row_count"] == 1 and out["rows"][0]["o"] == "x"
