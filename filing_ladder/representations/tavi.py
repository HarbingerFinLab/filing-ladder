"""Rung 5c — the filing as a Project Tavi compiled model, queried with jq (5d: in context).

Tavi (XBRL International, PWD 2026-09-01, previously "OIM Taxonomy") is one JSON document
carrying both the facts and the taxonomy that gives them meaning: labels, presentation and
calculation networks, cubes. It is the standards body's answer to the gap rung 5 measures —
xBRL-JSON carries no taxonomy — and the artifact the webinar claim in the protocol was made
about. The document is built by ``xbrlkit --format tavi`` from the filing.

Two tools, the same hand-off as rungs 7b and 7c: ``describe_model`` (how to read the
document, the entity, the periods, units, dimensions and concepts present, the groups, and
example queries) and ``run_jq`` (one read-only jq program over the document). 5d is the same
document with text-block facts removed, handed whole.
"""

from __future__ import annotations

import json
import multiprocessing
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Callable

import jq

from .companyfacts import clip
from .oim import is_text_block

CORE_DIMENSIONS = (
  "xbrl:concept",
  "xbrl:period",
  "xbrl:entity",
  "xbrl:unit",
  "xbrl:language",
)

EXAMPLE_QUERIES: list[tuple[str, str]] = [
  (
    "Find a concept by its label (the QName is what every other query needs). Labels are "
    "free-standing objects pointing at the concept through forObject; xbrl:label is the "
    "standard label.",
    """[.xbrlModel.labels[]
  | select(.labelType == "xbrl:label" and (.value | ascii_downcase | contains("property, plant")))
  | {concept: .forObject, label: .value}]""",
  ),
  (
    "Consolidated (undimensioned) values of one concept. A fact's factDimensions carries the "
    "core dimensions under xbrl:* keys and every taxonomy axis as a further key, so the "
    "consolidated total is the fact with no non-xbrl key. Values are strings: use tonumber.",
    """[.xbrlModel.facts[]
  | select(.factDimensions["xbrl:concept"] == "us-gaap:Revenues")
  | select([.factDimensions | keys[] | select(startswith("xbrl:") | not)] | length == 0)
  | {period: .factDimensions["xbrl:period"], unit: .factDimensions["xbrl:unit"],
     value: (.factValues[0].value | tonumber), decimals: .factValues[0].decimals}]
| sort_by(.period) | reverse""",
  ),
  (
    "The dimensional breakdown of a concept for one period: the non-core keys of "
    "factDimensions are the axes, their values the members.",
    """[.xbrlModel.facts[]
  | select(.factDimensions["xbrl:concept"] == "us-gaap:Revenues"
           and .factDimensions["xbrl:period"] == "2024-01-01T00:00:00/2025-01-01T00:00:00")
  | {axes: (.factDimensions | with_entries(select(.key | startswith("xbrl:") | not))),
     value: (.factValues[0].value | tonumber)}]""",
  ),
  (
    "What sums to a concept: its calculation children with weights. Networks hold "
    "relationships; xbrl:summation-item networks carry xbrl:weight as a relationship property; "
    "a relationship from xbrl:rootSource marks a root.",
    """[.xbrlModel.networks[]
  | select(.relationshipTypeName == "xbrl:summation-item")
  | .relationships[]
  | select(.source == "us-gaap:OperatingIncomeLoss")
  | {child: .target, order,
     weight: ([.properties[]? | select(.property == "xbrl:weight") | .value] | first)}]""",
  ),
  (
    "Which statements or notes a concept is presented on: presentation networks belong to "
    "groups (groupContents), and a group's readable name is its xbrl:label.",
    """(.xbrlModel.labels | map(select(.labelType == "xbrl:label")) | map({(.forObject): .value}) | add) as $lbl
| [.xbrlModel.networks[]
  | select(.relationshipTypeName == "xbrl:parent-child")
  | select(any(.relationships[]; .target == "us-gaap:Goodwill"))
  | .name] as $nets
| [.xbrlModel.groupContents[] | select(.forObject as $n | $nets | index($n)) | $lbl[.groupName]]""",
  ),
  (
    "The line items of one statement, in presentation order with the label the statement "
    "uses (xbrl:preferredLabel names a label type; fall back to the standard label).",
    """(.xbrlModel.labels | map({(.forObject + "|" + .labelType): .value}) | add) as $lbl
| (.xbrlModel.groups[] | select(.groupURI | test("ConsolidatedStatementofIncome")) | .name) as $g
| [.xbrlModel.groupContents[] | select(.groupName == $g) | .forObject] as $members
| .xbrlModel.networks[] | select((.name as $n | $members | index($n)) and .relationshipTypeName == "xbrl:parent-child")
| [.relationships[] | select(.source != "xbrl:rootSource")
   | {parent: .source, concept: .target, order,
      label: ($lbl[.target + "|" + (([.properties[]? | select(.property == "xbrl:preferredLabel") | .value] | first) // "xbrl:label")]
              // $lbl[.target + "|xbrl:label"])}]""",
  ),
]

# jq can read the process environment ($ENV, env), and the harness holds API keys in it.
_ENVIRONMENT = re.compile(r"\$ENV\b|(?<![\w$.])env\b")


def build_tavi(cik: str, accession: str, out: Path, user_agent: str) -> Path:
  """Build the compiled model with the xbrlkit CLI in a subprocess (Arelle keeps global state).

  ``xbrlkit`` writes the ``.tavi.gaps.json`` sidecar beside ``out``: what the filing carries
  that the draft has nowhere to put, and the draft ambiguities the emitter had to resolve.
  """
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
    "tavi",
    "-o",
    str(out),
  ]
  proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
  if proc.returncode != 0 or not out.exists():
    raise RuntimeError(f"tavi build failed: {proc.stderr[-2000:]}")
  return out


def load_tavi(path: Path) -> dict:
  return json.loads(path.read_text(encoding="utf-8"))


def minified(doc: dict) -> str:
  return json.dumps(doc, separators=(",", ":"), ensure_ascii=False)


def _facts(doc: dict) -> list[dict]:
  return doc.get("xbrlModel", {}).get("facts", []) or []


def _value(fact: dict) -> object:
  values = fact.get("factValues") or []
  return values[0].get("value") if values else None


def strip_text_blocks(doc: dict) -> tuple[dict, int]:
  """The document without its text-block facts, and the count removed — rung 5b's rule."""
  kept: list[dict] = []
  removed = 0
  for fact in _facts(doc):
    concept = str(fact.get("factDimensions", {}).get("xbrl:concept", ""))
    if is_text_block(concept, _value(fact)):
      removed += 1
    else:
      kept.append(fact)
  model = dict(doc.get("xbrlModel", {}))
  model["facts"] = kept
  out = dict(doc)
  out["xbrlModel"] = model
  return out, removed


def summary_note(doc: dict) -> str:
  model = doc.get("xbrlModel", {})
  return ", ".join(
    f"{len(model.get(key) or [])} {key}"
    for key in ("facts", "concepts", "networks", "cubes", "labels")
    if key in model
  )


# ---- describe_model ------------------------------------------------------------------

CONCEPTS_LISTED = 40
GROUPS_LISTED = 80
AXES_LISTED = 25


def describe_model(doc: dict) -> str:
  model = doc.get("xbrlModel", {})
  namespaces = doc.get("documentInfo", {}).get("namespaces", {})
  counts = ", ".join(
    f"{key} ×{len(value)}" for key, value in model.items() if isinstance(value, list)
  )
  prefixes = ", ".join(f"{p} → {u}" for p, u in namespaces.items())
  examples = "\n\n".join(f"# {why}\n{q}" for why, q in EXAMPLE_QUERIES)
  return f"""This is ONE financial report as a Project Tavi compiled model (XBRL International's OIM Taxonomy
Model): a single JSON document holding the facts AND the taxonomy that gives them meaning, queryable
with jq. Every object is addressed by a QName; the prefixes are:
{prefixes}

{_entity(model)}
Top-level collections under .xbrlModel ({counts}).

Reading a fact (.xbrlModel.facts[]): .factDimensions is a flat map — "xbrl:concept" (the concept
QName), "xbrl:period" (an ISO interval of dateTimes with an EXCLUSIVE end: the 2024 calendar year is
"2024-01-01T00:00:00/2025-01-01T00:00:00", an instant at the close of 2024-12-31 is
"2025-01-01T00:00:00"), "xbrl:entity", "xbrl:unit" (absent for a pure number), "xbrl:language" (text
facts only), plus one further key per taxonomy axis whose value is the member. A fact with any non-xbrl:
key is a breakdown (segment, member); the consolidated total is the fact with NONE — see example 2.
.factValues[0].value is the reported value as a STRING (use tonumber); .decimals is its precision
(-6 = millions; absent = exact). A fact the filing reports as nil has no factValues at all.

Reading the taxonomy: .concepts[] carry name, dataType, periodType and properties (xbrla:balance).
.headings[] are the abstract line items that organize a statement. .labels[] are free-standing:
{{forObject, labelType, language, value}}; "xbrl:label" is the standard label, "xbrl:terseLabel",
"xbrl:totalLabel", "xbrl:negatedLabel" etc. the others. .networks[] hold relationships
{{source, target, order, properties}}: relationshipTypeName "xbrl:parent-child" is presentation
(properties may carry xbrl:preferredLabel), "xbrl:summation-item" is calculation (xbrl:weight ±1);
a relationship from "xbrl:rootSource" marks a root. .groups[] are the statements and notes
(groupURI; readable name = the group's xbrl:label); .groupContents[] map a group to its networks and
cubes. .cubes[] / .dimensions[] / .domainNetworks[] / .members[] describe the dimensional tables.

Most-reported concepts (QName → standard label → fact count; the full set is found by example 1):
{_concepts_present(model)}

Periods present (facts):
{_periods_present(model)}

Units present:
{_units_present(model)}

Taxonomy axes present on facts (axis → distinct members → facts):
{_axes_present(model)}

Groups (statements and notes; group name → label):
{_groups_present(model)}

Example queries (working jq programs for this document — start from these; the input is the whole
document, so begin with .xbrlModel):

{examples}"""


def _entity(model: dict) -> str:
  entities = [e.get("name") for e in model.get("entities", []) or []]
  properties = {
    p.get("property"): p.get("value") for p in model.get("properties", []) or []
  }
  filed = properties.get("xbrl:reportFilingDate")
  return (
    f"Report: {model.get('name', '?')} — entity {', '.join(map(str, entities)) or '?'}"
    + (f", filed {filed}\n" if filed else "\n")
  )


def _standard_labels(model: dict) -> dict[str, str]:
  out: dict[str, str] = {}
  for label in model.get("labels", []) or []:
    if label.get("labelType") == "xbrl:label":
      out.setdefault(str(label.get("forObject")), str(label.get("value")))
  return out


def _concepts_present(model: dict) -> str:
  counts = Counter(
    str(f.get("factDimensions", {}).get("xbrl:concept"))
    for f in model.get("facts", []) or []
  )
  labels = _standard_labels(model)
  shown = [
    f'  - {qname} → "{labels.get(qname, "")}" ({n} facts)'
    for qname, n in counts.most_common(CONCEPTS_LISTED)
  ]
  if len(counts) > CONCEPTS_LISTED:
    shown.append(f"  … and {len(counts) - CONCEPTS_LISTED} more concepts.")
  return "\n".join(shown)


def _periods_present(model: dict) -> str:
  counts = Counter(
    str(f.get("factDimensions", {}).get("xbrl:period"))
    for f in model.get("facts", []) or []
  )
  ordered = sorted(
    counts.items(), key=lambda kv: (kv[0].rsplit("/", 1)[-1], kv[0]), reverse=True
  )
  return "\n".join(f"  - {period}: {n} facts" for period, n in ordered)


def _units_present(model: dict) -> str:
  counts = Counter(
    str(f.get("factDimensions", {}).get("xbrl:unit"))
    for f in model.get("facts", []) or []
    if f.get("factDimensions", {}).get("xbrl:unit")
  )
  return "\n".join(f"  - {unit}: {n} facts" for unit, n in counts.most_common())


def _axes_present(model: dict) -> str:
  facts_by_axis: Counter = Counter()
  members_by_axis: dict[str, set] = {}
  for fact in model.get("facts", []) or []:
    for key, value in fact.get("factDimensions", {}).items():
      if key not in CORE_DIMENSIONS:
        facts_by_axis[key] += 1
        members_by_axis.setdefault(key, set()).add(str(value))
  shown = [
    f"  - {axis}: {len(members_by_axis[axis])} members, {n} facts"
    for axis, n in facts_by_axis.most_common(AXES_LISTED)
  ]
  if len(facts_by_axis) > AXES_LISTED:
    shown.append(f"  … and {len(facts_by_axis) - AXES_LISTED} more axes.")
  return "\n".join(shown)


def _groups_present(model: dict) -> str:
  labels = _standard_labels(model)
  groups = model.get("groups", []) or []
  shown = [
    f"  - {g.get('name')}: {labels.get(str(g.get('name')), g.get('groupURI', ''))}"
    for g in groups[:GROUPS_LISTED]
  ]
  if len(groups) > GROUPS_LISTED:
    shown.append(
      f"  … and {len(groups) - GROUPS_LISTED} more groups — find one by its label in .labels[]."
    )
  return "\n".join(shown)


# ---- run_jq -----------------------------------------------------------------------------

JQ_TIMEOUT_S = 60.0
MAX_RESULTS = 200
HARD_RESULT_CAP = 100_000


def run_jq(
  doc: dict,
  program: str,
  max_results: int = MAX_RESULTS,
  timeout_s: float = JQ_TIMEOUT_S,
) -> str:
  """Evaluate a jq program over the document with a hard wall-clock limit.

  jq evaluates in-process through libjq and cannot be interrupted, and a program can loop
  forever (``repeat``, an unbounded ``range``). The program runs in a forked child; on
  timeout the child is killed and the model gets a tool error it can recover from — the
  same shape as the SPARQL rung. A program that reads the process environment is refused:
  the harness holds API keys there, and the environment is not part of the report.
  """
  if _ENVIRONMENT.search(program):
    return json.dumps(
      {
        "error": "$ENV / env are not available: the environment is not part of the report."
      }
    )
  ctx = multiprocessing.get_context("fork")
  parent_conn, child_conn = ctx.Pipe(duplex=False)
  proc = ctx.Process(
    target=_evaluate_in_child, args=(doc, program, max_results, child_conn)
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
        f"jq program timed out after {timeout_s:.0f}s — it is unbounded or walks the whole "
        "document repeatedly. Select on one concept, one period or one network first, and "
        "use limit(n; ...) or first(...)."
      )
    }
  )


def _evaluate_in_child(doc: dict, program: str, max_results: int, conn) -> None:
  try:
    conn.send(_evaluate(doc, program, max_results))
  except Exception as exc:  # pragma: no cover - surfaced to the model as a tool error
    conn.send(json.dumps({"error": f"jq error: {exc}"}))
  finally:
    conn.close()


def _evaluate(doc: dict, program: str, max_results: int) -> str:
  try:
    compiled = jq.compile(program)
  except ValueError as exc:
    return json.dumps({"error": f"jq error: {exc}"})
  results: list[object] = []
  total = 0
  try:
    for item in compiled.input_value(doc):
      total += 1
      if len(results) < max_results:
        results.append(item)
      if total >= HARD_RESULT_CAP:
        break
  except Exception as exc:  # jq raises ValueError for runtime errors
    return json.dumps({"error": f"jq error: {exc}"})
  payload: dict = {"result_count": total, "results": results}
  if total >= HARD_RESULT_CAP:
    payload["note"] = (
      f"stopped at {HARD_RESULT_CAP:,} results; the program is unbounded"
    )
  elif total > max_results:
    payload["note"] = f"showing {max_results} of {total} results; select more narrowly"
  elif total == 0 or (total == 1 and results and results[0] in ([], None)):
    payload["note"] = (
      "empty result — the selection matched nothing; check the QName (example 1), the "
      "period literal (an exclusive-end dateTime interval) and the collection you started from"
    )
  return clip(
    json.dumps(payload, separators=(",", ":"), ensure_ascii=False, default=str)
  )


TOOL_DEFS: list[dict] = [
  {
    "name": "describe_model",
    "description": (
      "Return how this report's Tavi compiled model is laid out (facts, dimensions, periods, "
      "the taxonomy objects), the concepts, periods, units, axes and groups present, and "
      "example jq programs. Call this first — never guess the shape."
    ),
    "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
  },
  {
    "name": "run_jq",
    "description": (
      "Run a read-only jq program over the whole compiled model and return its outputs. "
      "The input is the document, so start from .xbrlModel; use the patterns from describe_model."
    ),
    "input_schema": {
      "type": "object",
      "properties": {
        "program": {"type": "string", "description": "A jq program (jq 1.7 syntax)."}
      },
      "required": ["program"],
      "additionalProperties": False,
    },
  },
]


def make_tool_runner(doc: dict) -> Callable[[str, dict], str]:
  description = describe_model(doc)

  def run(name: str, args: dict) -> str:
    if name == "describe_model":
      return description
    if name == "run_jq":
      return run_jq(doc, str(args.get("program", "")))
    return json.dumps({"error": f"unknown tool {name}"})

  return run
