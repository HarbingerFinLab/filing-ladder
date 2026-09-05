#!/usr/bin/env python
"""Check the text layer on every materialized filing under ``data/``.

Rung 7a's search index and rung 7b's text blocks are built by ``xbrlkit.text``,
so a parser defect is a product defect the ladder would otherwise measure as a
model failure (PROTOCOL principle 11). This runs both parsers on each filing's
primary document and checks:

- every inline-XBRL disclosure section against the filing's OIM text-block
  facts (``oim/oim.json`` — Arelle's resolved values, the ground truth): the
  section must contain five substrings probed from the middle of each fact,
  compared on alphanumerics because Arelle decodes entities the parser maps
  to spaces; a concept tagged more than once is compared to its longest fact.
  Two missed probes, or a section under 98% of the fact's length, is lost
  text; a section over 101% of a single fact is content that is not the
  fact's (page furniture inside the block, a hijacked continuation);
- every 10-K / 10-Q Item the extractor targets: present, not headed by a
  table-of-contents row, carrying its expected words, free of other Items'
  headings (an overrun), and its share of the document.

usage: uv run python bin/check_text_layer.py [--data data] [--json out.json] [ACCESSION ...]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from xbrlkit.text import (
  MIN_SECTION_WORDS,
  SECTIONS_10K,
  SECTIONS_10Q,
  NarrativeExtractor,
  iXBRLParser,
)

# The parsers' own normalisation, so the gold is compared the way a section is built.
from xbrlkit.text.ixbrl import _strip_html
from xbrlkit.text.narrative import _clean_text, _html_to_text, _is_toc_row

PART_SIZE = 25_000  # the index's part size

KEYWORDS = {
  "Business": ["business"],
  "Risk Factors": ["risk"],
  "Cybersecurity": ["cybersecurity", "cyber"],
  "Properties": ["propert", "facilit", "office", "lease", "square feet"],
  "MD&A": ["results of operations", "liquidity"],
  "Market Risk": ["market risk", "interest rate", "foreign currency", "exchange rate"],
}
ITEM_HEAD_RE = re.compile(
  r"^[ \t|]*(?:PART\s+[IV]+\s*[,.\-–—]?\s*)?ITEM\s+(\d+[A-C]?)\s*[.:\-–—|]",
  re.I | re.M,
)


def key(text: str) -> str:
  """Alphanumeric words only."""
  return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def probes(gold: str, n: int = 5, width: int = 60) -> list[str]:
  """``n`` substrings of ``width`` characters at even positions in ``gold``."""
  length = len(gold)
  if length < width * 2:
    return [gold] if gold else []
  out = []
  for i in range(1, n + 1):
    pos = int(length * i / (n + 1))
    space = gold.find(" ", pos)
    if space == -1:
      space = pos
    out.append(gold[space + 1 : space + 1 + width].strip())
  return [p for p in out if p]


def check_disclosures(html: str, oim: dict | None) -> tuple[list[dict], int, int]:
  """Rows per gold concept; the number of sections and parts the parser made."""
  sections = iXBRLParser(part_size=PART_SIZE).parse(html)
  by_id: dict[str, list] = defaultdict(list)
  for s in sections:
    by_id[s.section_id].append(s)
  if oim is None:
    return [], len(by_id), len(sections)

  gold: dict[str, list[str]] = defaultdict(list)
  for fact in oim["facts"].values():
    concept = fact["dimensions"].get("concept", "")
    if "TextBlock" not in concept or concept.startswith(("dei:", "ecd:")):
      continue
    gold[concept].append(fact.get("value") or "")

  rows = []
  for concept, values in gold.items():
    parts = sorted(by_id.get(concept, []), key=lambda p: p.part)
    content = key(" ".join(p.content for p in parts))
    distinct = {key(_strip_html(v)) for v in values}
    best = max(distinct, key=len) if distinct else ""
    ps = probes(best)
    hit = None
    ratio = None
    if not parts:
      status = "short" if len(best.split()) < MIN_SECTION_WORDS else "MISSING"
    else:
      ratio = len(content) / max(1, len(best))
      hit = sum(1 for p in ps if p in content)
      misses = len(ps) - hit
      flags = []
      # One missed probe at the fact's own length is a table cell rendered in a
      # different order, not lost text; two, or a shorter section, is loss.
      if misses >= 2 or ratio < 0.98:
        flags.append("INCOMPLETE")
      if ratio < 0.9:
        flags.append("SHORTER")
      # Longer than its one fact: content that is not the fact's (ix:exclude
      # page furniture, a hijacked continuation). A concept tagged more than
      # once holds every occurrence, so it is longer than its longest fact.
      if ratio > 1.01 and len(distinct) == 1:
        flags.append("EXTRA")
      status = "+".join(flags) or "ok"
    rows.append(
      dict(
        concept=concept,
        facts=len(values),
        distinct=len(distinct),
        gold_chars=len(best),
        got_chars=len(content),
        ratio=None if ratio is None else round(ratio, 3),
        probes=[hit, len(ps)],
        parts=len(parts),
        status=status,
      )
    )
  return rows, len(by_id), len(sections)


def check_items(html: str, form: str) -> tuple[list[dict], int, int, int]:
  """Rows per expected Item; document chars, covered chars, part count."""
  sections = NarrativeExtractor(part_size=PART_SIZE).extract(html, form)
  by_id: dict[str, list] = defaultdict(list)
  for s in sections:
    by_id[s.section_id].append(s)
  total = max(1, len(_clean_text(_html_to_text(html))))
  expected = SECTIONS_10K if form.upper().startswith("10-K") else SECTIONS_10Q
  rows = []
  for number, (section_id, label, _part) in expected.items():
    parts = sorted(by_id.get(section_id, []), key=lambda p: p.part)
    if not parts:
      rows.append(dict(item=section_id, label=label, status="MISSING"))
      continue
    content = "\n".join(p.content for p in parts)
    first_line = content.split("\n", 1)[0]
    flags = []
    if first_line.lstrip().startswith("|") or _is_toc_row(first_line):
      flags.append("TOC-HEAD")
    lowered = content.lower()
    if not any(k in lowered for k in KEYWORDS[label]):
      flags.append("NO-KEYWORD")
    foreign = [
      m.group(1).upper()
      for m in ITEM_HEAD_RE.finditer(content)
      if m.group(1).upper() != number.upper()
    ]
    if foreign:
      flags.append("FOREIGN-ITEMS:" + ",".join(dict.fromkeys(foreign)))
    if len(content) < 1500:
      flags.append("tiny")  # lower case: short by nature, not a defect
    rows.append(
      dict(
        item=section_id,
        label=label,
        chars=len(content),
        parts=len(parts),
        share=round(len(content) / total, 3),
        head=" ".join(content[:110].split()),
        status=" ".join(flags) or "ok",
      )
    )
  covered = sum(len(p.content) for p in sections)
  return rows, total, covered, len(sections)


def check_filing(folder: Path) -> dict | None:
  meta_path = folder / "meta.json"
  if not meta_path.exists():
    return None
  meta = json.loads(meta_path.read_text())
  html_path = folder / "package" / meta["primary_document"]
  if not html_path.exists():
    return dict(accession=folder.name, error="no primary document")
  html = html_path.read_text(encoding="utf-8", errors="replace")
  oim_path = folder / "oim" / "oim.json"
  oim = json.loads(oim_path.read_text()) if oim_path.exists() else None
  disclosure_rows, n_sections, n_parts = check_disclosures(html, oim)
  item_rows, total, covered, item_parts = check_items(html, meta["form"])
  return dict(
    accession=folder.name,
    ticker=meta.get("ticker") or meta["cik"],
    form=meta["form"],
    disclosures=dict(
      rows=disclosure_rows, sections=n_sections, parts=n_parts, gold=oim is not None
    ),
    items=dict(
      rows=item_rows, document_chars=total, covered_chars=covered, parts=item_parts
    ),
  )


def main() -> int:
  ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
  ap.add_argument("accessions", nargs="*", help="limit to these accession numbers")
  ap.add_argument(
    "--data", default="data", help="the materialized filings (default: data)"
  )
  ap.add_argument("--json", help="write every row to this file")
  args = ap.parse_args()

  folders = sorted(Path(args.data).glob("0*"))
  if args.accessions:
    wanted = set(args.accessions)
    folders = [f for f in folders if f.name in wanted]
  results = []
  defects = 0
  for folder in folders:
    result = check_filing(folder)
    if result is None:
      continue
    results.append(result)
    if "error" in result:
      print(f"{result['accession']}: {result['error']}")
      defects += 1
      continue
    counts = Counter(r["status"] for r in result["disclosures"]["rows"])
    bad_items = [
      r for r in result["items"]["rows"] if r["status"].isupper() or " " in r["status"]
    ]
    bad_items = [r for r in bad_items if r["status"] != "tiny"]
    covered = result["items"]["covered_chars"] / result["items"]["document_chars"]
    print(
      f"{result['ticker']:10} {result['form']:5} {result['accession']} | disclosures "
      f"gold={sum(counts.values()):3} "
      + " ".join(f"{k}={v}" for k, v in sorted(counts.items()))
      + (" (no OIM gold)" if not result["disclosures"]["gold"] else "")
      + f" | items={len(result['items']['rows'])} flagged={len(bad_items)} cover={covered:.0%}"
    )
    for r in result["disclosures"]["rows"]:
      if r["status"] not in ("ok", "short"):
        defects += 1
        print(
          f"    {r['status']:12} {r['concept']} gold={r['gold_chars']} got={r['got_chars']} "
          f"ratio={r['ratio']} probes={r['probes']} facts={r['facts']}"
        )
    for r in bad_items:
      defects += 1
      print(
        f"    {r['item']:8} {r['status']}"
        + (f"  head: {r['head']}" if "head" in r else "")
      )
  if args.json:
    Path(args.json).write_text(json.dumps(results, indent=1))
  print(f"{len(results)} filings, {defects} flagged rows")
  return 1 if defects else 0


if __name__ == "__main__":
  sys.exit(main())
