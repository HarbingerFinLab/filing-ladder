"""Rung 7c — the filing as RDF (``holon.jsonld``) in an in-memory store, queried with SPARQL.

Two tools, parallel to the property-graph rung's hand-off: ``describe_report`` (the
vocabulary, the node shapes computed from the actual graph, the concepts and periods
present, and example queries) and ``run_sparql`` (read-only SELECT / ASK). The holon is
built by ``robosystems-xbrl-holon`` and loaded exactly as its own query layer loads it.
"""

from __future__ import annotations

import json
import multiprocessing
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable

from rdflib import RDF, Graph
from rdflib.term import Literal, URIRef, Variable

from .companyfacts import clip

PREFIXES: dict[str, str] = {
  "rs": "https://robosystems.ai/vocab/",
  "skos": "http://www.w3.org/2004/02/skos/core#",
  "xbrli": "http://www.xbrl.org/2003/instance#",
  "xlink": "http://www.w3.org/1999/xlink#",
  "link": "http://www.xbrl.org/2003/linkbase#",
  "us-gaap": "http://fasb.org/us-gaap/",
  "dei": "http://xbrl.sec.gov/dei/",
  "srt": "http://fasb.org/srt/",
  "iso4217": "http://www.xbrl.org/2003/iso4217#",
  "concept": "https://robosystems.ai/concept/",
}

PREFIX_BLOCK = "\n".join(f"PREFIX {k}: <{v}>" for k, v in PREFIXES.items())

EXAMPLE_QUERIES: list[tuple[str, str]] = [
  (
    "Find a concept by its label (the qname is what every other query needs).",
    """SELECT ?qname ?label (COUNT(?f) AS ?facts) WHERE {
  ?el a rs:Element ; rs:internalId ?qname ; skos:prefLabel ?label .
  OPTIONAL { ?f rs:element ?el }
  FILTER (CONTAINS(LCASE(?label), "property, plant"))
} GROUP BY ?qname ?label ORDER BY DESC(?facts)""",
  ),
  (
    "Consolidated (undimensioned) values of one concept, with the period pinned. Two facts "
    "can share an end date (the annual and the fourth quarter); rs:durationType and the "
    "start date tell them apart.",
    """SELECT ?qname ?label ?value ?start ?end ?instant ?ptype ?dtype ?measure WHERE {
  ?f a rs:Fact ; rs:element ?el ; rs:period ?p ; rs:numericValue ?value .
  ?el rs:internalId ?qname .
  OPTIONAL { ?el skos:prefLabel ?label }
  ?p xbrli:periodType ?ptype .
  OPTIONAL { ?p xbrli:startDate ?start } OPTIONAL { ?p xbrli:endDate ?end }
  OPTIONAL { ?p xbrli:instant ?instant } OPTIONAL { ?p rs:durationType ?dtype }
  OPTIONAL { ?f rs:unit ?u . ?u xbrli:measure ?measure }
  FILTER NOT EXISTS { ?f rs:dimension ?d }
  FILTER (?qname = "us-gaap:Revenues")
} ORDER BY DESC(?end) DESC(?instant)""",
  ),
  (
    "The dimensional breakdown of a concept (segments, members) for one period end.",
    """SELECT ?axis ?member ?value ?start ?end WHERE {
  ?f a rs:Fact ; rs:element ?el ; rs:period ?p ; rs:numericValue ?value ; rs:dimension ?d .
  ?el rs:internalId "us-gaap:Revenues" .
  ?d rs:axis ?axis ; rs:member ?member .
  ?p xbrli:endDate ?end . OPTIONAL { ?p xbrli:startDate ?start }
  FILTER (?end = "2024-12-31"^^<http://www.w3.org/2001/XMLSchema#date> || STR(?end) = "2024-12-31")
} ORDER BY ?axis ?member""",
  ),
  (
    "What sums to a concept: its calculation children with weights (the taxonomy is in the graph).",
    """SELECT ?childQname ?childLabel ?weight ?order WHERE {
  ?a rs:associationType "calculation" ; xlink:from ?parent ; xlink:to ?child ;
     link:weight ?weight ; link:order ?order .
  ?parent rs:internalId "us-gaap:OperatingIncomeLoss" .
  ?child rs:internalId ?childQname . OPTIONAL { ?child skos:prefLabel ?childLabel }
} ORDER BY ?order""",
  ),
  (
    "Which statements or notes a concept appears on (presentation structures), and its label there.",
    """SELECT ?structureLabel ?preferredLabel WHERE {
  ?s a rs:Structure ; skos:prefLabel ?structureLabel ; rs:hasAssociation ?a .
  ?a rs:associationType "presentation" ; xlink:to ?el .
  OPTIONAL { ?a rs:preferredLabel ?preferredLabel }
  ?el rs:internalId "us-gaap:Goodwill" .
}""",
  ),
]

_READ_ONLY = re.compile(r"^\s*(PREFIX\s+\S+\s+<[^>]*>\s*)*(SELECT|ASK)\b", re.I | re.S)


def build_holon(cik: str, accession: str, out: Path, user_agent: str) -> Path:
  """Build ``holon.jsonld`` with the holon CLI in a subprocess (Arelle keeps global state)."""
  out.parent.mkdir(parents=True, exist_ok=True)
  cmd = [
    sys.executable,
    "-c",
    "import sys; from robosystems_xbrl_holon.cli import main; sys.exit(main(sys.argv[1:]))",
    "--user-agent",
    user_agent,
    "build",
    "--cik",
    cik,
    "--accno",
    accession,
    "-o",
    str(out),
  ]
  proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
  if proc.returncode != 0 or not out.exists():
    raise RuntimeError(f"holon build failed: {proc.stderr[-2000:]}")
  return out


def load_holon(path: Path) -> Graph:
  from robosystems_xbrl_holon.query import load_holon as _load

  return _load(path)


def compact(iri: str) -> str:
  for prefix, base in PREFIXES.items():
    if iri.startswith(base):
      return f"{prefix}:{iri[len(base) :]}"
  return f"<{iri}>"


def describe_report(graph: Graph) -> str:
  shapes = _node_shapes(graph)
  concepts = _concepts_present(graph)
  periods = _periods_present(graph)
  units = _units_present(graph)
  entity = _entity(graph)
  examples = "\n\n".join(f"# {why}\n{PREFIX_BLOCK}\n{q}" for why, q in EXAMPLE_QUERIES)
  return f"""This is ONE financial report as RDF (an XBRL "holon"), queryable with read-only SPARQL 1.1.
Always include these PREFIX lines:

{PREFIX_BLOCK}

{entity}
Node shapes, computed from this graph (type: predicate ×count):
{shapes}

Reading a value: a rs:Fact has rs:element (the concept), rs:period, rs:unit, and rs:numericValue
or rs:stringValue. A fact with any rs:dimension is a breakdown (segment, member); the
consolidated total is the fact WITHOUT rs:dimension — use FILTER NOT EXISTS {{ ?f rs:dimension ?d }}.
Concepts are identified by rs:internalId (the qname, e.g. "us-gaap:Revenues"); join
skos:prefLabel for the human label. Periods carry xbrli:startDate / xbrli:endDate (duration) or
xbrli:instant, plus rs:durationType (annual | quarterly | other). Presentation, calculation and
definition relationships are rs:Association nodes (xlink:from, xlink:to, link:order, link:weight,
rs:associationType) grouped under rs:Structure nodes — the taxonomy is in this graph.

Most-reported concepts in this report (qname → label; the full set is found by query):
{concepts}

Periods present:
{periods}

Units present:
{units}

Example queries (working patterns for this graph — start from these):

{examples}"""


SPARQL_TIMEOUT_S = 60.0


def run_sparql(
  graph: Graph, query: str, max_rows: int = 200, timeout_s: float = SPARQL_TIMEOUT_S
) -> str:
  """Evaluate a read-only query with a hard wall-clock limit.

  rdflib evaluates in-process and cannot be interrupted, and a model-written pattern with a
  cross product can run for hours (seen 2026-09-03: one query held a run for 51 minutes at
  100% CPU). The query runs in a forked child; on timeout the child is killed and the model
  gets a tool error it can recover from — the same shape as the graph API's server-side
  timeout on the Cypher rung.
  """
  if not _READ_ONLY.match(query):
    return json.dumps({"error": "Only SELECT or ASK queries are allowed."})
  ctx = multiprocessing.get_context("fork")
  parent_conn, child_conn = ctx.Pipe(duplex=False)
  proc = ctx.Process(
    target=_evaluate_in_child, args=(graph, query, max_rows, child_conn)
  )
  proc.daemon = True
  proc.start()
  child_conn.close()
  try:
    if parent_conn.poll(timeout_s):
      out = parent_conn.recv()
      proc.join(5)
      return out
  except EOFError:
    pass
  proc.kill()
  proc.join(5)
  return json.dumps(
    {
      "error": (
        f"SPARQL query timed out after {timeout_s:.0f}s — the pattern is too broad "
        "(an unbounded join or cross product). Anchor on the report, one concept or one "
        "period, and add a LIMIT."
      )
    }
  )


def _evaluate_in_child(graph: Graph, query: str, max_rows: int, conn) -> None:
  try:
    conn.send(_evaluate(graph, query, max_rows))
  except Exception as exc:  # pragma: no cover - surfaced to the model as a tool error
    conn.send(json.dumps({"error": f"SPARQL error: {exc}"}))
  finally:
    conn.close()


def _evaluate(graph: Graph, query: str, max_rows: int) -> str:
  try:
    result = graph.query(query)
  except Exception as exc:  # rdflib raises many parser/eval types
    return json.dumps({"error": f"SPARQL error: {exc}"})
  if result.type == "ASK":
    return json.dumps({"ask": bool(result.askAnswer)})
  variables = [str(v) for v in (result.vars or [])]
  rows: list[dict] = []
  total = 0
  for binding in result.bindings:
    total += 1
    if len(rows) >= max_rows:
      continue
    rows.append({v: _plain(binding.get(Variable(v))) for v in variables})
  payload = {"columns": variables, "row_count": total, "rows": rows}
  if total > max_rows:
    payload["note"] = f"showing {max_rows} of {total} rows; add a FILTER or LIMIT"
  if total == 0:
    payload["note"] = (
      "0 rows — the pattern matched nothing; check the qname, the period shape and the PREFIX lines"
    )
  return clip(json.dumps(payload, separators=(",", ":"), default=str))


TOOL_DEFS: list[dict] = [
  {
    "name": "describe_report",
    "description": (
      "Return the report's RDF vocabulary (SPARQL prefixes, node shapes computed from the graph), "
      "the concepts and periods present, and example queries. Call this first — never guess the schema."
    ),
    "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
  },
  {
    "name": "run_sparql",
    "description": (
      "Run a read-only SPARQL 1.1 SELECT or ASK query over this report and return the rows. "
      "Use the prefixes and patterns from describe_report."
    ),
    "input_schema": {
      "type": "object",
      "properties": {
        "query": {"type": "string", "description": "A SPARQL SELECT or ASK query."}
      },
      "required": ["query"],
      "additionalProperties": False,
    },
  },
]


def make_tool_runner(graph: Graph) -> Callable[[str, dict], str]:
  description = describe_report(graph)

  def run(name: str, args: dict) -> str:
    if name == "describe_report":
      return description
    if name == "run_sparql":
      return run_sparql(graph, str(args.get("query", "")))
    return json.dumps({"error": f"unknown tool {name}"})

  return run


# ---- describe_report pieces ----------------------------------------------------


def _node_shapes(graph: Graph) -> str:
  by_type: dict[str, Counter] = defaultdict(Counter)
  for subject, rdf_type in graph.subject_objects(RDF.type):
    for predicate in graph.predicates(subject):
      if predicate != RDF.type:
        by_type[str(rdf_type)][str(predicate)] += 1
  lines = []
  for rdf_type, preds in sorted(by_type.items(), key=lambda kv: kv[0]):
    inner = ", ".join(f"{compact(p)} ×{n}" for p, n in preds.most_common())
    lines.append(f"  {compact(rdf_type)}: {inner}")
  return "\n".join(lines)


CONCEPTS_LISTED = 40


def _concepts_present(graph: Graph) -> str:
  """The most-reported concepts as orientation; the rest are found by query (example 1)."""
  q = f"""{PREFIX_BLOCK}
SELECT ?qname (SAMPLE(?label) AS ?l) (COUNT(?f) AS ?n) WHERE {{
  ?f a rs:Fact ; rs:element ?el . ?el rs:internalId ?qname .
  OPTIONAL {{ ?el skos:prefLabel ?label }}
}} GROUP BY ?qname ORDER BY DESC(?n) ?qname"""
  rows = list(graph.query(q))
  shown = [f'  - {r.qname} → "{r.l}" ({r.n} facts)' for r in rows[:CONCEPTS_LISTED]]
  if len(rows) > CONCEPTS_LISTED:
    shown.append(
      f"  … and {len(rows) - CONCEPTS_LISTED} more concepts — find one by label with example query 1."
    )
  return "\n".join(shown)


def _periods_present(graph: Graph) -> str:
  q = f"""{PREFIX_BLOCK}
SELECT ?p ?ptype ?start ?end ?instant ?dtype (COUNT(?f) AS ?n) WHERE {{
  ?p a rs:Period ; xbrli:periodType ?ptype .
  OPTIONAL {{ ?p xbrli:startDate ?start }} OPTIONAL {{ ?p xbrli:endDate ?end }}
  OPTIONAL {{ ?p xbrli:instant ?instant }} OPTIONAL {{ ?p rs:durationType ?dtype }}
  OPTIONAL {{ ?f rs:period ?p }}
}} GROUP BY ?p ?ptype ?start ?end ?instant ?dtype ORDER BY DESC(?end) DESC(?instant)"""
  rows = []
  for r in graph.query(q):
    when = (
      f"{r.instant} (instant)"
      if r.instant
      else f"{r.start} → {r.end} ({r.dtype or 'duration'})"
    )
    rows.append(f"  - {when}: {r.n} facts")
  return "\n".join(rows)


def _units_present(graph: Graph) -> str:
  q = f"""{PREFIX_BLOCK}
SELECT ?measure (COUNT(?f) AS ?n) WHERE {{ ?u a rs:Unit ; xbrli:measure ?measure . OPTIONAL {{ ?f rs:unit ?u }} }}
GROUP BY ?measure ORDER BY DESC(?n)"""
  return "\n".join(f"  - {r.measure}: {r.n} facts" for r in graph.query(q))


def _entity(graph: Graph) -> str:
  q = f"""{PREFIX_BLOCK}
SELECT ?name ?form ?fy ?fp ?accession WHERE {{
  ?r a rs:Report . OPTIONAL {{ ?r rs:form ?form }} OPTIONAL {{ ?r rs:fiscalYearFocus ?fy }}
  OPTIONAL {{ ?r rs:fiscalPeriodFocus ?fp }} OPTIONAL {{ ?r rs:accessionNumber ?accession }}
  OPTIONAL {{ ?r rs:entity ?e . ?e skos:prefLabel ?name }}
}} LIMIT 1"""
  for r in graph.query(q):
    return f"Report: {r.name or '?'} — form {r.form or '?'}, fiscal year {r.fy or '?'} {r.fp or ''}, accession {r.accession or '?'}\n"
  return ""


def _plain(value: object) -> object:
  if isinstance(value, Literal):
    py = value.toPython()
    return py if isinstance(py, (int, float, bool, str)) else str(py)
  if isinstance(value, URIRef):
    return compact(str(value))
  return None if value is None else str(value)
