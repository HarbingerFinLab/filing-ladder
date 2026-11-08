#!/usr/bin/env python
"""The document-as-a-constant gate for protocol v0.1.2 (PROTOCOL §11, principle 11).

v0.1.1 delivered the document to every tool rung as rung 2's plain text behind two harness
tools. v0.1.2 delivers it through xbrlkit's own ``search_text`` / ``read_text`` over the filing
loaded from its package — the text layer every xbrlkit user gets, and the one the ``sec``
server's text tools run. The two must read the same document: this checks, for every
materialized filing, that xbrlkit's readable text and rung 2's plain text carry the same
content — compared on alphanumerics, since the two renderers differ in whitespace and
entity handling — by length ratio and by probes taken from each and looked for in the other.
A probe is matched with every space removed as well as on alphanumerics: the two renderers
split a table cell or a footnote marker differently ("brokerages17" against "brokerages 17"),
and that is not a difference in what the document says.

usage: uv run python bin/check_readable_text.py [--data data] [--json out.json] [ACCESSION ...]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

RATIO_LOW, RATIO_HIGH = 0.97, 1.03
PROBES, WIDTH = 12, 80


def key(text: str) -> str:
  return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def squash(text: str) -> str:
  return text.replace(" ", "")


def probes(text: str, n: int = PROBES, width: int = WIDTH) -> list[str]:
  out = []
  for i in range(1, n + 1):
    pos = int(len(text) * i / (n + 1))
    # start on a word boundary so a probe never begins mid-token
    start = text.find(" ", pos) + 1
    out.append(text[start : start + width].strip())
  return [p for p in out if p]


def check_filing(folder: Path) -> dict | None:
  from filing_ladder.representations.xbrlkit_serve import ServedFiling

  package, rung2 = folder / "package", folder / "rung2.text.txt"
  if not package.is_dir() or not rung2.exists():
    return None
  t0 = time.monotonic()
  sf = ServedFiling(package)
  readable, sections = sf.filing.readable(True)
  k_x, k_2 = key(readable), key(rung2.read_text(encoding="utf-8", errors="replace"))
  sq_x, sq_2 = squash(k_x), squash(k_2)
  missed_in_xbrlkit = [p for p in probes(k_2) if squash(p) not in sq_x]
  missed_in_rung2 = [p for p in probes(k_x) if squash(p) not in sq_2]
  ratio = len(k_x) / len(k_2) if k_2 else 0.0
  ok = (
    sf.filing.has_document
    and RATIO_LOW <= ratio <= RATIO_HIGH
    and not missed_in_xbrlkit
    and not missed_in_rung2
  )
  return {
    "accession": folder.name,
    "has_document": sf.filing.has_document,
    "read_from": sf.filing.read_from,
    "facts": len(sf.filing.model.facts),
    "sections": len(sections),
    "xbrlkit_chars": len(readable),
    "rung2_chars": rung2.stat().st_size,
    "alnum_ratio": round(ratio, 4),
    "probes_missing_in_xbrlkit": missed_in_xbrlkit,
    "probes_missing_in_rung2": missed_in_rung2,
    "load_s": round(time.monotonic() - t0, 1),
    "ok": ok,
  }


def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
  ap.add_argument("--data", default="data")
  ap.add_argument("--json")
  ap.add_argument("accessions", nargs="*")
  args = ap.parse_args()
  folders = sorted(
    p
    for p in Path(args.data).iterdir()
    if p.is_dir() and (not args.accessions or p.name in args.accessions)
  )
  rows = []
  for folder in folders:
    row = check_filing(folder)
    if row is None:
      continue
    rows.append(row)
    flag = "ok  " if row["ok"] else "FAIL"
    print(
      f"{flag} {row['accession']}  ratio {row['alnum_ratio']:.4f}  "
      f"xbrlkit {row['xbrlkit_chars']:>9,}  rung2 {row['rung2_chars']:>9,}  "
      f"sections {row['sections']:>3}  missed {len(row['probes_missing_in_xbrlkit'])}/"
      f"{len(row['probes_missing_in_rung2'])}  {row['load_s']}s",
      flush=True,
    )
  failed = [r["accession"] for r in rows if not r["ok"]]
  print(f"\n{len(rows) - len(failed)}/{len(rows)} filings read the same document")
  if args.json:
    Path(args.json).write_text(json.dumps(rows, indent=1), encoding="utf-8")
  return 1 if failed else 0


if __name__ == "__main__":
  sys.exit(main())
