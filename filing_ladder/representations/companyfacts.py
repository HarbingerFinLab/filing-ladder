"""Rung 6 — the SEC's own structured API (``data.sec.gov``) through three thin tools.

No presentation, calculation or label structure, no dimensional facts, no text blocks —
what the SEC ships for free, with its own normalization. The tools are deliberately thin:
search the concepts a company has reported, read one concept's facts, read one frame across
companies. The model does the rest.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Callable

import httpx

MAX_TOOL_CHARS = 60_000


class CompanyFacts:
  def __init__(
    self, user_agent: str, cache_dir: Path, min_interval: float = 0.12
  ) -> None:
    self._client = httpx.Client(
      base_url="https://data.sec.gov",
      headers={"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"},
      timeout=60,
    )
    self._cache_dir = cache_dir
    self._min_interval = min_interval
    self._last = 0.0

  def _get_json(self, path: str) -> Any:
    wait = self._min_interval - (time.monotonic() - self._last)
    if wait > 0:
      time.sleep(wait)
    resp = self._client.get(path)
    self._last = time.monotonic()
    resp.raise_for_status()
    return resp.json()

  def company_facts(self, cik: str) -> dict:
    padded = f"{int(cik):010d}"
    cached = self._cache_dir / f"CIK{padded}.json"
    if cached.exists():
      return json.loads(cached.read_text())
    doc = self._get_json(f"/api/xbrl/companyfacts/CIK{padded}.json")
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_text(json.dumps(doc))
    return doc

  # ---- the three tools -------------------------------------------------------

  def search_concepts(self, cik: str, query: str, limit: int = 25) -> list[dict]:
    doc = self.company_facts(cik)
    pattern = re.compile(re.escape(query), re.I)
    hits: list[dict] = []
    for taxonomy, concepts in doc.get("facts", {}).items():
      for name, body in concepts.items():
        label = body.get("label") or ""
        description = body.get("description") or ""
        if pattern.search(name) or pattern.search(label) or pattern.search(description):
          n_facts = sum(len(v) for v in body.get("units", {}).values())
          hits.append(
            {
              "taxonomy": taxonomy,
              "concept": name,
              "label": label,
              "units": list(body.get("units", {}).keys()),
              "facts": n_facts,
            }
          )
    hits.sort(key=lambda h: (-h["facts"], h["concept"]))
    return hits[:limit]

  def get_concept_facts(
    self,
    cik: str,
    taxonomy: str,
    concept: str,
    fy: int | None = None,
    fp: str | None = None,
    form: str | None = None,
    limit: int = 60,
  ) -> dict:
    doc = self.company_facts(cik)
    body = doc.get("facts", {}).get(taxonomy, {}).get(concept)
    if body is None:
      return {"error": f"{taxonomy}:{concept} not reported by CIK {cik}"}
    rows: list[dict] = []
    for unit, facts in body.get("units", {}).items():
      for f in facts:
        if fy is not None and f.get("fy") != fy:
          continue
        if fp is not None and f.get("fp") != fp:
          continue
        if form is not None and f.get("form") != form:
          continue
        rows.append({"unit": unit, **f})
    rows.sort(key=lambda r: (r.get("end") or "", r.get("filed") or ""), reverse=True)
    return {
      "concept": f"{taxonomy}:{concept}",
      "label": body.get("label"),
      "description": body.get("description"),
      "count": len(rows),
      "facts": rows[:limit],
    }

  def get_frame(self, taxonomy: str, concept: str, unit: str, period: str) -> dict:
    """One concept across every filer for a calendar period, e.g. CY2024 or CY2024Q4I."""
    return self._get_json(f"/api/xbrl/frames/{taxonomy}/{concept}/{unit}/{period}.json")


TOOL_DEFS: list[dict] = [
  {
    "name": "search_concepts",
    "description": (
      "Search the XBRL concepts a company has ever reported to the SEC (by concept name, "
      "label or description). Returns taxonomy, concept, label, units and fact counts. "
      "Call this first to find the exact concept name."
    ),
    "input_schema": {
      "type": "object",
      "properties": {
        "cik": {"type": "string", "description": "The company's CIK."},
        "query": {"type": "string", "description": "A word or phrase, e.g. 'revenue'."},
      },
      "required": ["cik", "query"],
    },
  },
  {
    "name": "get_concept_facts",
    "description": (
      "All reported values of one concept for one company, newest first, with fiscal year "
      "(fy), fiscal period (fp), form, period start/end, filing date and accession. Filter by "
      "fy, fp (FY, Q1, Q2, Q3) or form (10-K, 10-Q) to narrow."
    ),
    "input_schema": {
      "type": "object",
      "properties": {
        "cik": {"type": "string"},
        "taxonomy": {"type": "string", "description": "us-gaap, dei, ifrs-full, ..."},
        "concept": {"type": "string", "description": "e.g. Revenues"},
        "fy": {"type": "integer"},
        "fp": {"type": "string"},
        "form": {"type": "string"},
      },
      "required": ["cik", "taxonomy", "concept"],
    },
  },
  {
    "name": "get_frame",
    "description": (
      "One concept for every filer in one calendar period: taxonomy, concept, unit (USD, "
      "USD-per-shares, shares, pure) and period (CY2024 for a year, CY2024Q4 for a quarter, "
      "CY2024Q4I for an instant). Use for cross-company questions."
    ),
    "input_schema": {
      "type": "object",
      "properties": {
        "taxonomy": {"type": "string"},
        "concept": {"type": "string"},
        "unit": {"type": "string"},
        "period": {"type": "string"},
      },
      "required": ["taxonomy", "concept", "unit", "period"],
    },
  },
]


def make_tool_runner(cf: CompanyFacts) -> Callable[[str, dict], str]:
  def run(name: str, args: dict) -> str:
    if name == "search_concepts":
      result: Any = cf.search_concepts(args["cik"], args["query"])
    elif name == "get_concept_facts":
      result = cf.get_concept_facts(
        args["cik"],
        args["taxonomy"],
        args["concept"],
        fy=args.get("fy"),
        fp=args.get("fp"),
        form=args.get("form"),
      )
    elif name == "get_frame":
      result = cf.get_frame(
        args["taxonomy"], args["concept"], args["unit"], args["period"]
      )
    else:
      return json.dumps({"error": f"unknown tool {name}"})
    return clip(json.dumps(result, separators=(",", ":")))

  return run


def clip(text: str, limit: int = MAX_TOOL_CHARS) -> str:
  if len(text) <= limit:
    return text
  return (
    text[:limit]
    + f"... [truncated: {len(text) - limit} more characters; narrow the request]"
  )
