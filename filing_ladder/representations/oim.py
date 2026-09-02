"""Rung 5 — OIM: the instance as xBRL-JSON and xBRL-CSV, via Arelle's ``saveLoadableOIM``.

5a is the export as published. 5b removes text-block facts — the escaped-HTML narrative
that, on the reference filing, is about four fifths of every structured serialization —
so that the structured facts fit in context.

A fact is a text block when its concept is a ``TextBlock``, or its value is markup, or its
value is at least ``TEXT_BLOCK_MIN_CHARS`` long (policy text blocks are tagged on
``...Policy`` concepts, not ``...TextBlock``, and are markup all the same).
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

TEXT_BLOCK_MIN_CHARS = 300

# Text-block facts are escaped HTML far past csv's default 128 KiB field limit.
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


@dataclass(frozen=True)
class OimFiles:
  json: Path
  facts_csv: Path
  metadata_json: Path
  footnotes_csv: Path


def export_oim(instance: Path, out_dir: Path, stem: str = "oim") -> OimFiles:
  """Run Arelle twice (JSON, then CSV) on the instance document."""
  out_dir.mkdir(parents=True, exist_ok=True)
  json_out = out_dir / f"{stem}.json"
  csv_out = out_dir / f"{stem}.csv"
  if not json_out.exists():
    _arelle(instance, json_out)
  if not (out_dir / f"{stem}-facts.csv").exists():
    _arelle(instance, csv_out)
  files = OimFiles(
    json=json_out,
    facts_csv=out_dir / f"{stem}-facts.csv",
    metadata_json=out_dir / f"{stem}-metadata.json",
    footnotes_csv=out_dir / f"{stem}-footnotes.csv",
  )
  for path in (files.json, files.facts_csv, files.metadata_json):
    if not path.exists():
      raise RuntimeError(f"Arelle did not write {path}")
  return files


def _arelle(instance: Path, target: Path) -> None:
  cmd = [
    sys.executable,
    "-m",
    "arelle.CntlrCmdLine",
    "--file",
    str(instance),
    "--plugins",
    "saveLoadableOIM",
    "--saveLoadableOIM",
    str(target),
    "--logLevel",
    "error",
  ]
  proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
  if proc.returncode != 0:
    raise RuntimeError(f"Arelle failed on {instance.name}: {proc.stderr[-2000:]}")


def is_text_block(
  concept: str, value: object, min_chars: int = TEXT_BLOCK_MIN_CHARS
) -> bool:
  text = str(value) if value is not None else ""
  if concept.endswith("TextBlock"):
    return True
  stripped = text.lstrip()
  if stripped.startswith("<"):
    return True
  return len(text) >= min_chars


def strip_text_blocks_json(doc: dict) -> tuple[dict, int]:
  """Return a copy of an xBRL-JSON document without its text-block facts, and the count removed."""
  facts = doc.get("facts", {})
  kept: dict = {}
  removed = 0
  for fact_id, fact in facts.items():
    concept = str(fact.get("dimensions", {}).get("concept", ""))
    if is_text_block(concept, fact.get("value")):
      removed += 1
    else:
      kept[fact_id] = fact
  out = dict(doc)
  out["facts"] = kept
  return out, removed


def strip_text_blocks_csv(facts_csv: Path, out_csv: Path) -> int:
  """Write the xBRL-CSV facts table without text-block rows; return the count removed.

  Written to a temp file and renamed, so an interrupted run never leaves a partial table.
  """
  removed = 0
  tmp = out_csv.with_suffix(out_csv.suffix + ".tmp")
  with facts_csv.open(newline="", encoding="utf-8-sig") as src:
    reader = csv.DictReader(src)
    fields = list(reader.fieldnames or [])
    value_col = "value" if "value" in fields else fields[-1]
    concept_col = "concept" if "concept" in fields else fields[1]
    with tmp.open("w", newline="", encoding="utf-8") as dst:
      writer = csv.DictWriter(dst, fieldnames=fields)
      writer.writeheader()
      for row in reader:
        if is_text_block(row.get(concept_col, ""), row.get(value_col, "")):
          removed += 1
        else:
          writer.writerow(row)
  tmp.replace(out_csv)
  return removed


def minified(doc: dict) -> str:
  return json.dumps(doc, separators=(",", ":"), ensure_ascii=False)


def fact_stats(doc: dict) -> dict[str, int]:
  facts = doc.get("facts", {})
  text_blocks = sum(
    1
    for f in facts.values()
    if is_text_block(str(f.get("dimensions", {}).get("concept", "")), f.get("value"))
  )
  dimensional = sum(
    1
    for f in facts.values()
    if any(
      k not in ("concept", "entity", "period", "unit", "language")
      for k in f.get("dimensions", {})
    )
  )
  return {"facts": len(facts), "text_blocks": text_blocks, "dimensional": dimensional}
