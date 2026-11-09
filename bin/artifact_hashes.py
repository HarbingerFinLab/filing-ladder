#!/usr/bin/env python
"""SHA-256 of every artifact a row of the ladder reads, per filing (PROTOCOL §11, v0.2).

v0.2 opens a new model column, and nothing carries forward by identity across a model change. The
hashes pin the corpus as it stood at the pre-registration, so the rows run now and the rows that
wait on funding are known to read the same bytes: the PDF (rung 1), the plain text (rung 2, and the
v0.1.1 document tools), the inline document (rung 3), the OIM exports (5a, 5b) and the companyfacts
file (6), held unchanged since the v0.1 freeze; and the re-materialized forms (the Tavi, the holon,
the property graph), the bytes the rows of ours read.

usage: uv run python bin/artifact_hashes.py [--data data] [--json out.json]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HELD = (
  "rung1.filing.pdf",
  "rung2.text.txt",
  "rung3.ixbrl.htm",
  "rung5b.oim-notext.json",
  "rung5b.oim-notext-facts.csv",
)
REMATERIALIZED = ("rung5c.tavi.json", "rung7b.filing.lbug", "rung7c.holon.jsonld")


def sha256(path: Path) -> str:
  h = hashlib.sha256()
  with path.open("rb") as fh:
    for chunk in iter(lambda: fh.read(1 << 20), b""):
      h.update(chunk)
  return h.hexdigest()


def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
  ap.add_argument("--data", default="data")
  ap.add_argument("--json")
  args = ap.parse_args()
  data = Path(args.data)
  out: dict[str, dict] = {}
  for folder in sorted(
    p for p in data.iterdir() if p.is_dir() and p.name != "companyfacts"
  ):
    meta = (
      json.loads((folder / "meta.json").read_text())
      if (folder / "meta.json").exists()
      else {}
    )
    files: dict[str, str] = {}
    for name in HELD + REMATERIALIZED:
      path = folder / name
      if path.exists():
        files[name] = sha256(path)
    for path in sorted((folder / "oim").glob("*")) if (folder / "oim").is_dir() else []:
      if path.is_file():
        files[f"oim/{path.name}"] = sha256(path)
    cik = str(meta.get("cik", "")).lstrip("0")
    for cf in sorted((data / "companyfacts").glob("*.json")):
      if cik and cf.stem.lstrip("0").lstrip("CIK") == cik:
        files[f"companyfacts/{cf.name}"] = sha256(cf)
    out[folder.name] = {
      "ticker": meta.get("ticker"),
      "form": meta.get("form"),
      "held": {k: v for k, v in files.items() if not k.startswith(REMATERIALIZED)},
      "re_materialized": {
        k: v for k, v in files.items() if k.startswith(REMATERIALIZED)
      },
    }
    print(f"{folder.name}  {len(files)} files hashed", flush=True)
  if args.json:
    Path(args.json).write_text(json.dumps(out, indent=1), encoding="utf-8")
  return 0


if __name__ == "__main__":
  sys.exit(main())
