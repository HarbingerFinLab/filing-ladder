#!/usr/bin/env python
"""The 7b engine check for protocol v0.1.2 (PROTOCOL §11, principle 11).

LadybugDB 0.22.x can project a DOUBLE as 0.0 when a filtered scan's batch straddles a
compression segment boundary — the defect found on the hosted ``sec`` graph on 2026-11-08
(RoboSystems #2008; LadybugDB #1540). Rung 7b runs the same engine over each filing's own
graph, so this reads every consolidated numeric fact through two filtered projections — the
dimension flag alone, and the flag joined through the element — and compares the engine's
``numeric_value`` with the fact's own text ``value``. A 0.0 against non-zero text is the
defect; any other disagreement is reported too. Exit status 1 on either.

usage: uv run python bin/check_lbug_doubles.py [--data data] [--json out.json] [ACCESSION ...]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from importlib.metadata import version
from pathlib import Path

SHAPES = {
  "flag": (
    "MATCH (f:Fact) WHERE f.has_dimensions = false AND f.numeric_value IS NOT NULL "
    "RETURN f.value, f.numeric_value"
  ),
  "flag+element": (
    "MATCH (f:Fact {has_dimensions: false})-[:FACT_HAS_ELEMENT]->(e:Element) "
    "WHERE e.is_numeric = true AND f.numeric_value IS NOT NULL "
    "RETURN f.value, f.numeric_value"
  ),
}


def rows(conn, query: str) -> list[list]:
  result = conn.execute(query)
  out = []
  while result.has_next():
    out.append(result.get_next())
  return out


def compare(pairs: list[list]) -> tuple[int, int, int]:
  """(numeric facts compared, 0.0 against non-zero text, other disagreements)."""
  compared = zeros = other = 0
  for text, number in pairs:
    try:
      parsed = float(str(text).replace(",", ""))
    except ValueError:
      continue
    compared += 1
    if number == 0.0 and parsed != 0.0:
      zeros += 1
    elif not math.isclose(parsed, float(number), rel_tol=1e-9, abs_tol=1e-9):
      other += 1
  return compared, zeros, other


def check(path: Path) -> dict:
  import ladybug

  db = ladybug.Database(str(path), read_only=True)
  conn = ladybug.Connection(db)
  try:
    out: dict = {"accession": path.parent.name, "shapes": {}}
    for name, query in SHAPES.items():
      compared, zeros, other = compare(rows(conn, query))
      out["shapes"][name] = {
        "compared": compared,
        "zero_misreads": zeros,
        "other": other,
      }
    out["ok"] = all(
      s["zero_misreads"] == 0 and s["other"] == 0 for s in out["shapes"].values()
    )
    return out
  finally:
    conn.close()
    db.close()


def main() -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument("--data", default="data")
  ap.add_argument("--json", default="results/v0.1.2-sonnet-5/lbug-double-reads.json")
  ap.add_argument("accessions", nargs="*")
  args = ap.parse_args()
  data = Path(args.data)
  dirs = [data / a for a in args.accessions] or sorted(
    p.parent for p in data.glob("*/rung7b.filing.lbug")
  )
  results = []
  for d in dirs:
    r = check(d / "rung7b.filing.lbug")
    results.append(r)
    flag = r["shapes"]["flag"]
    print(
      f"{'ok  ' if r['ok'] else 'FAIL'} {r['accession']}  facts {flag['compared']:>5}  "
      f"zero-misreads {flag['zero_misreads']}  other {flag['other']}  "
      f"(joined: {r['shapes']['flag+element']['compared']})"
    )
  totals = {
    name: {
      k: sum(r["shapes"][name][k] for r in results)
      for k in ("compared", "zero_misreads", "other")
    }
    for name in SHAPES
  }
  report = {
    "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "ladybug": version("ladybug"),
    "shapes": SHAPES,
    "filings": results,
    "totals": totals,
    "ok": all(r["ok"] for r in results),
  }
  out = Path(args.json)
  out.parent.mkdir(parents=True, exist_ok=True)
  out.write_text(json.dumps(report, indent=2) + "\n")
  print(
    f"{sum(r['ok'] for r in results)}/{len(results)} graphs clean under ladybug "
    f"{report['ladybug']}; totals {json.dumps(totals)}; wrote {out}"
  )
  return 0 if report["ok"] else 1


if __name__ == "__main__":
  sys.exit(main())
