"""How much of each filing's text a representation keeps.

For every materialized filing: the plain text (rung 2) is the denominator; the tagged text-block
facts (what every XBRL-derived form carries) and the narrative sections xbrlkit extracts from the
primary document (what rung 7a's search index holds beside the text blocks) are the numerators,
in characters of clean text. The two overlap where a tagged note sits inside an extracted Item,
so their sum is an upper bound, not a union.

    uv run --no-sync python bin/document_coverage.py
"""

from __future__ import annotations

import html
import json
import re
import statistics
from pathlib import Path

from xbrlkit.text import NarrativeExtractor

DATA = Path(__file__).resolve().parent.parent / "data"


def clean(fragment: str) -> str:
  return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def text_block_chars(oim: dict) -> int:
  facts = oim.get("facts", {})
  values = facts.values() if isinstance(facts, dict) else facts
  return sum(
    len(clean(f["value"]))
    for f in values
    if isinstance(f.get("value"), str) and "<" in f["value"] and len(f["value"]) > 500
  )


def main() -> None:
  rows: list[tuple[str, str, str, int, float, float, str]] = []
  for filing in sorted(DATA.iterdir()):
    plain_path = filing / "rung2.text.txt"
    oim_path = filing / "oim" / "oim.json"
    if not plain_path.exists() or not oim_path.exists():
      continue
    meta = json.loads((filing / "meta.json").read_text())
    form = meta.get("form_type") or meta.get("form") or "10-K"
    primary = (filing / "package" / meta["primary_document"]).read_text(
      encoding="utf-8", errors="ignore"
    )
    plain = len(plain_path.read_text())
    tagged = text_block_chars(json.loads(oim_path.read_text()))
    sections = NarrativeExtractor().extract(primary, form)
    section_chars = sum(len(s.content) for s in sections)
    items = ",".join(sorted({s.section_id.replace("item_", "") for s in sections}))
    rows.append(
      (
        filing.name,
        meta.get("ticker") or "",
        form,
        plain,
        tagged / plain,
        section_chars / plain,
        items,
      )
    )
  print(f"{'accession':22} {'ticker':6} form   plain chars   tagged   sections  items")
  for acc, ticker, form, plain, tagged, secs, items in rows:
    print(
      f"{acc:22} {ticker:6} {form:5} {plain:>11,}   {tagged:6.0%}   {secs:6.0%}   {items}"
    )
  tagged_share = [r[4] for r in rows]
  section_share = [r[5] for r in rows]
  print(f"\n{len(rows)} filings")
  print(
    f"tagged text blocks / plain text:  median {statistics.median(tagged_share):.0%}"
    f"  range {min(tagged_share):.0%}-{max(tagged_share):.0%}"
  )
  print(
    f"narrative sections / plain text:  median {statistics.median(section_share):.0%}"
    f"  range {min(section_share):.0%}-{max(section_share):.0%}"
  )
  print(
    "both, overlaps not removed (upper bound): median "
    f"{statistics.median(a + b for a, b in zip(tagged_share, section_share)):.0%}"
  )


if __name__ == "__main__":
  main()
