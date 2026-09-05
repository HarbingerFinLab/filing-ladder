"""Rung 7b — the filing as a property graph (LadybugDB), queried with read-only Cypher.

The graph is the filing projected by ``xbrlkit`` (``xbrlkit build --format lpg``) into the
same tables the RoboSystems ``sec`` graph is built from — the same node labels, relationship
types, properties and ids — held in one local database file. What differs from the shared
graph is what the platform adds after projection: text blocks stay inline in ``Fact.value``
(the platform serves them from a CDN and indexes them for rung 7a's search tool), and the
enrichment columns (``canonical_concept``, ``canonical_type``) are empty.

Two tools, the same hand-off as rungs 5c and 7c: ``describe_graph`` (the schema computed
from the database, how to read a value, the concepts, periods and units present, and example
queries) and ``run_cypher`` (one read-only query, in a child process with a wall-clock limit).
Nothing here reaches a server: the rung runs from the file, so it is reproducible without the
platform being up, and 7a vs 7b measures the tool layer, the serving shape and the corpus
context together.
"""

from __future__ import annotations

import json
import multiprocessing
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from .companyfacts import clip

STANDARD_LABEL = "http://www.xbrl.org/2003/role/label"

# A query is read-only when it starts as a read and names no write or DDL clause. The
# database is also opened read-only, so this is belt and braces.
_READ_START = re.compile(
  r"^\s*(MATCH|OPTIONAL\s+MATCH|WITH|RETURN|UNWIND|CALL\s+(show_tables|table_info))\b",
  re.I,
)
_WRITE_CLAUSE = re.compile(
  r"\b(CREATE|MERGE|SET|DELETE|DETACH|REMOVE|DROP|ALTER|COPY|LOAD|INSTALL|ATTACH|"
  r"IMPORT|EXPORT|BEGIN|COMMIT|ROLLBACK|CHECKPOINT|USE)\b",
  re.I,
)

EXAMPLE_QUERIES: list[tuple[str, str]] = [
  (
    "Find a concept by its label (the qname is what every other query needs). Labels hang "
    "off Element through ELEMENT_HAS_LABEL; Label.type is the role, and the standard label's "
    "role is http://www.xbrl.org/2003/role/label.",
    """MATCH (e:Element)-[:ELEMENT_HAS_LABEL]->(l:Label {type: 'http://www.xbrl.org/2003/role/label'})
WHERE contains(lower(l.value), 'property, plant')
OPTIONAL MATCH (e)<-[:FACT_HAS_ELEMENT]-(f:Fact)
RETURN e.qname, l.value, count(f) AS facts ORDER BY facts DESC LIMIT 20""",
  ),
  (
    "Consolidated (undimensioned) values of one concept, with the period pinned. Two facts can "
    "share an end date (the annual and the fourth quarter); Period.duration_type and start_date "
    "tell them apart. has_dimensions: false is the consolidated total.",
    """MATCH (f:Fact {has_dimensions: false})-[:FACT_HAS_ELEMENT]->(e:Element {qname: 'us-gaap:Revenues'}),
      (f)-[:FACT_HAS_PERIOD]->(p:Period)
OPTIONAL MATCH (f)-[:FACT_HAS_UNIT]->(u:Unit)
RETURN e.qname, p.period_type, p.start_date, p.end_date, p.duration_type, f.numeric_value, u.measure, f.decimals
ORDER BY p.end_date DESC LIMIT 20""",
  ),
  (
    "The dimensional breakdown of a concept (segments, members) for one period end.",
    """MATCH (f:Fact {has_dimensions: true})-[:FACT_HAS_ELEMENT]->(e:Element {qname: 'us-gaap:Revenues'}),
      (f)-[:FACT_HAS_PERIOD]->(p:Period {end_date: '2024-12-31', period_type: 'duration'}),
      (f)-[:FACT_HAS_DIMENSION]->(d:Dimension)
RETURN d.axis, d.member, p.start_date, p.end_date, f.numeric_value ORDER BY d.axis, d.member LIMIT 100""",
  ),
  (
    "What sums to a concept: its calculation children with weights (the taxonomy is in the "
    "graph). Structure is the statement or note; Association is one arc, FROM the parent TO "
    "the child.",
    """MATCH (s:Structure)-[:STRUCTURE_HAS_ASSOCIATION]->(a:Association {association_type: 'Calculation'})
      -[:ASSOCIATION_HAS_FROM_ELEMENT]->(parent:Element {qname: 'us-gaap:OperatingIncomeLoss'}),
      (a)-[:ASSOCIATION_HAS_TO_ELEMENT]->(child:Element)
RETURN s.name, child.qname, a.weight, a.order_value ORDER BY s.name, a.order_value LIMIT 50""",
  ),
  (
    "Which statements or notes a concept appears on (presentation structures), and its label there.",
    """MATCH (s:Structure)-[:STRUCTURE_HAS_ASSOCIATION]->(a:Association {association_type: 'Presentation'})
      -[:ASSOCIATION_HAS_TO_ELEMENT]->(e:Element {qname: 'us-gaap:Goodwill'})
RETURN DISTINCT s.name, s.type, a.preferred_label LIMIT 50""",
  ),
  (
    "Read a note. Text blocks are facts whose Element.is_textblock is true; Fact.value holds "
    "the note's XHTML inline, tens of thousands of characters. Never RETURN a whole note — find "
    "the block with contains(), then read a window with regexp_extract() or substring() "
    "(1-based start, length).",
    """MATCH (f:Fact)-[:FACT_HAS_ELEMENT]->(e:Element {is_textblock: true})
WHERE contains(lower(f.value), 'exit')
RETURN e.qname, size(f.value) AS chars, regexp_extract(f.value, '.{0,300}[Ee]xit.{0,300}') AS window
ORDER BY chars LIMIT 10""",
  ),
]


def build_lbug(cik: str, accession: str, out: Path, user_agent: str) -> Path:
  """Build the filing's property graph with the xbrlkit CLI in a subprocess."""
  out.parent.mkdir(parents=True, exist_ok=True)
  cmd = [
    sys.executable,
    "-c",
    "import sys; from xbrlkit.cli import main; sys.exit(main(sys.argv[1:]))",
    "--user-agent",
    user_agent,
    "build",
    "--cik",
    cik,
    "--accno",
    accession,
    "--format",
    "lpg",
    "-o",
    str(out),
  ]
  proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
  if proc.returncode != 0 or not out.exists():
    raise RuntimeError(f"property graph build failed: {proc.stderr[-2000:]}")
  return out


def _open(path: Path):
  import ladybug as lbug

  db = lbug.Database(str(path), read_only=True)
  return db, lbug.Connection(db)


def _rows(conn, query: str) -> list[list[Any]]:
  return conn.execute(query).get_all()


def summary_note(path: Path) -> str:
  db, conn = _open(path)
  try:
    facts = _rows(conn, "MATCH (f:Fact) RETURN count(f)")[0][0]
    elements = _rows(conn, "MATCH (e:Element) RETURN count(e)")[0][0]
    return f"{facts:,} facts, {elements:,} elements, {path.stat().st_size / 1e6:.0f} MB"
  finally:
    conn.close()
    db.close()


def describe_graph(path: Path) -> str:
  db, conn = _open(path)
  try:
    report = _report(conn)
    schema = _schema(conn)
    concepts = _concepts_present(conn)
    periods = _periods_present(conn)
    units = _units_present(conn)
  finally:
    conn.close()
    db.close()
  examples = "\n\n".join(f"# {why}\n{q}" for why, q in EXAMPLE_QUERIES)
  return f"""This is ONE financial report as a property graph (LadybugDB, Cypher), queryable with read-only Cypher.
It has the same node labels, relationship types and properties as the RoboSystems `sec` graph, holding one filing.

{report}
Schema, computed from this database (label: property type, … | rows):
{schema}

Reading a value: a Fact has numeric_value (numbers) and value (the reported string; for a text block,
the note's XHTML inline). It reaches its concept through FACT_HAS_ELEMENT (Element.qname, e.g.
"us-gaap:Revenues"), its period through FACT_HAS_PERIOD (Period.period_type instant | duration,
start_date / end_date as 'YYYY-MM-DD' strings, duration_type annual | quarterly | other), its unit
through FACT_HAS_UNIT (Unit.measure) and its breakdowns through FACT_HAS_DIMENSION (Dimension.axis,
Dimension.member). A fact with has_dimensions: true is a breakdown (segment, member); the consolidated
total is the fact with has_dimensions: false. Labels hang off Element via ELEMENT_HAS_LABEL (Label.value,
Label.type = the label role). Presentation, calculation and definition relationships are Association
nodes (arcrole, association_type, order_value, weight, preferred_label) under Structure nodes
(name, type Statement | Disclosure, definition) — the taxonomy is in this graph.

String functions that exist: contains(s, sub), lower(s), upper(s), size(s), substring(s, start, length)
with a 1-based start, regexp_matches(s, re), regexp_extract(s, re). There is no split, position,
instr, APOC or full-text index. Always end a query with LIMIT.

Most-reported concepts in this report (qname → standard label; the full set is found by query):
{concepts}

Periods present:
{periods}

Units present:
{units}

Example queries (working patterns for this graph — start from these):

{examples}"""


CYPHER_TIMEOUT_S = 60.0


def run_cypher(
  path: Path, query: str, max_rows: int = 200, timeout_s: float = CYPHER_TIMEOUT_S
) -> str:
  """Run one read-only query with a hard wall-clock limit.

  The database engine evaluates in-process and cannot be interrupted, and a model-written
  pattern with a cross product can run for a long time. The query runs in a forked child
  that opens the file read-only; on timeout the child is killed and the model gets a tool
  error it can recover from — the same shape as the SPARQL and jq rungs.
  """
  if not _READ_START.match(query) or _WRITE_CLAUSE.search(query):
    return json.dumps(
      {"error": "Only read-only Cypher is allowed: MATCH … RETURN, with a LIMIT."}
    )
  ctx = multiprocessing.get_context("fork")
  parent_conn, child_conn = ctx.Pipe(duplex=False)
  proc = ctx.Process(
    target=_evaluate_in_child, args=(path, query, max_rows, child_conn)
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
        f"Cypher query timed out after {timeout_s:.0f}s — the pattern is too broad "
        "(an unbounded join or cross product). Anchor on one concept or one period, "
        "and add a LIMIT."
      )
    }
  )


def _evaluate_in_child(path: Path, query: str, max_rows: int, conn) -> None:
  try:
    conn.send(_evaluate(path, query, max_rows))
  except Exception as exc:  # pragma: no cover - surfaced to the model as a tool error
    conn.send(json.dumps({"error": f"Cypher error: {exc}"}))
  finally:
    conn.close()


def _evaluate(path: Path, query: str, max_rows: int) -> str:
  try:
    db, conn = _open(path)
  except Exception as exc:
    return json.dumps({"error": f"cannot open the graph: {exc}"})
  try:
    try:
      result = conn.execute(query)
    except Exception as exc:
      return json.dumps({"error": f"Cypher error: {exc}"})
    columns = list(result.get_column_names())
    rows: list[dict] = []
    total = 0
    while result.has_next():
      values = result.get_next()
      total += 1
      if len(rows) >= max_rows:
        continue
      rows.append({c: _plain(v) for c, v in zip(columns, values, strict=False)})
  finally:
    conn.close()
    db.close()
  payload: dict[str, Any] = {"columns": columns, "row_count": total, "rows": rows}
  if total > max_rows:
    payload["note"] = (
      f"showing {max_rows} of {total} rows; narrow the pattern or add a LIMIT"
    )
  if total == 0:
    payload["note"] = (
      "0 rows — the pattern matched nothing; check the qname, the period shape and the property names"
    )
  return clip(json.dumps(payload, separators=(",", ":"), default=str))


TOOL_DEFS: list[dict] = [
  {
    "name": "describe_graph",
    "description": (
      "Return the graph's schema computed from the database (node labels, relationship types, "
      "properties, row counts), how to read a fact, the concepts, periods and units present, "
      "and example queries. Call this first — never guess the schema."
    ),
    "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
  },
  {
    "name": "run_cypher",
    "description": (
      "Run a read-only Cypher query (MATCH … RETURN, always with a LIMIT) over this report "
      "and return the rows. Use the labels, properties and patterns from describe_graph."
    ),
    "input_schema": {
      "type": "object",
      "properties": {
        "query": {"type": "string", "description": "A read-only Cypher query."}
      },
      "required": ["query"],
      "additionalProperties": False,
    },
  },
]


def make_tool_runner(path: Path) -> Callable[[str, dict], str]:
  description = describe_graph(path)

  def run(name: str, args: dict) -> str:
    if name == "describe_graph":
      return description
    if name == "run_cypher":
      return run_cypher(path, str(args.get("query", "")))
    return json.dumps({"error": f"unknown tool {name}"})

  return run


# ---- describe_graph pieces ----------------------------------------------------


def _report(conn) -> str:
  rows = _rows(
    conn,
    "MATCH (en:Entity)-[:ENTITY_HAS_REPORT]->(r:Report) "
    "RETURN en.name, r.form, r.fiscal_year_focus, r.fiscal_period_focus, r.accession_number, r.filing_date LIMIT 1",
  )
  if not rows:
    return ""
  name, form, fy, fp, accession, filed = rows[0]
  return (
    f"Report: {name or '?'} — form {form or '?'}, fiscal year {fy or '?'} {fp or ''}, "
    f"accession {accession or '?'}, filed {filed or '?'}\n"
  )


def _schema(conn) -> str:
  tables = _rows(conn, "CALL show_tables() RETURN *")
  nodes = sorted(t[1] for t in tables if t[2] == "NODE")
  rels = sorted(t[1] for t in tables if t[2] == "REL")
  lines = []
  for name in nodes:
    props = _rows(conn, f"CALL table_info('{name}') RETURN *")
    count = _rows(conn, f"MATCH (n:{name}) RETURN count(n)")[0][0]
    if count == 0:
      continue
    inner = ", ".join(f"{p[1]} {p[2]}" for p in props)
    lines.append(f"  {name}: {inner} | {count:,} rows")
  lines.append("  relationships (FROM)-[TYPE]->(TO) | rows:")
  for name in rels:
    count = _rows(conn, f"MATCH ()-[r:{name}]->() RETURN count(r)")[0][0]
    if count == 0:
      continue
    ends = _rows(
      conn, f"MATCH (a)-[r:{name}]->(b) RETURN DISTINCT label(a), label(b) LIMIT 1"
    )
    if ends:
      lines.append(f"  ({ends[0][0]})-[:{name}]->({ends[0][1]}) | {count:,}")
    else:
      lines.append(f"  [:{name}] | {count:,}")
  return "\n".join(lines)


CONCEPTS_LISTED = 40


def _concepts_present(conn) -> str:
  rows = _rows(
    conn,
    "MATCH (e:Element)<-[:FACT_HAS_ELEMENT]-(f:Fact) "
    f"OPTIONAL MATCH (e)-[:ELEMENT_HAS_LABEL]->(l:Label {{type: '{STANDARD_LABEL}'}}) "
    "RETURN e.qname, min(l.value), count(f) AS n ORDER BY n DESC, e.qname",
  )
  shown = [f'  - {q} → "{label}" ({n} facts)' for q, label, n in rows[:CONCEPTS_LISTED]]
  if len(rows) > CONCEPTS_LISTED:
    shown.append(
      f"  … and {len(rows) - CONCEPTS_LISTED} more concepts — find one by label with example query 1."
    )
  return "\n".join(shown)


def _periods_present(conn) -> str:
  rows = _rows(
    conn,
    "MATCH (p:Period)<-[:FACT_HAS_PERIOD]-(f:Fact) "
    "RETURN p.period_type, p.start_date, p.end_date, p.duration_type, count(f) AS n "
    "ORDER BY p.end_date DESC, p.start_date DESC",
  )
  out = []
  for ptype, start, end, dtype, n in rows:
    when = (
      f"{end} (instant)"
      if ptype == "instant"
      else f"{start} → {end} ({dtype or 'duration'})"
    )
    out.append(f"  - {when}: {n} facts")
  return "\n".join(out)


def _units_present(conn) -> str:
  rows = _rows(
    conn,
    "MATCH (u:Unit)<-[:FACT_HAS_UNIT]-(f:Fact) RETURN u.measure, count(f) AS n ORDER BY n DESC",
  )
  return "\n".join(f"  - {measure}: {n} facts" for measure, n in rows)


def _plain(value: object) -> object:
  if isinstance(value, (int, float, bool, str)) or value is None:
    return value
  return str(value)
