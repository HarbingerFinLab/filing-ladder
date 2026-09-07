"""6+efts — the SEC's own EDGAR full-text search, pinned to one filing.

EFTS indexes files, not passages: a hit is one file of a filing (its ``_id`` is
``accession:filename``) with metadata and a score, and no text. The request is pinned by CIK
and form, and the response to the resolved accession, so the model never sees a later filing.
"""

from __future__ import annotations

import json
import time
from typing import Callable

import httpx

from ..providers.base import ToolDef
from .companyfacts import clip

EFTS_URL = "https://efts.sec.gov/LATEST/search-index"
MAX_HITS = 20
MIN_INTERVAL_S = 0.15  # SEC fair-access guidance: at most ten requests a second
TOOL_NAME = "search_filings"


class FilingSearch:
  def __init__(
    self,
    user_agent: str,
    cik: str,
    accession: str,
    form: str | None = None,
    transport: httpx.BaseTransport | None = None,
  ) -> None:
    self.cik = cik.zfill(10)
    self.accession = accession
    self.form = form
    self._client = httpx.Client(
      headers={"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"},
      timeout=30.0,
      transport=transport,
    )
    self._last = 0.0

  def search(self, phrase: str) -> dict:
    phrase = phrase.strip().strip('"')
    params = {"q": f'"{phrase}"', "ciks": self.cik}
    if self.form:
      params["forms"] = self.form
    wait = MIN_INTERVAL_S - (time.monotonic() - self._last)
    if wait > 0:
      time.sleep(wait)
    resp = self._client.get(EFTS_URL, params=params)
    self._last = time.monotonic()
    resp.raise_for_status()
    raw = (resp.json().get("hits") or {}).get("hits") or []
    hits: list[dict] = []
    for h in raw:
      accession, _, filename = str(h.get("_id", "")).partition(":")
      if accession != self.accession:
        continue
      source = h.get("_source") or {}
      hits.append(
        {
          "file": filename,
          "file_type": source.get("file_type"),
          "description": source.get("file_description"),
          "score": h.get("_score"),
        }
      )
    hits.sort(key=lambda x: -(x["score"] or 0))
    return {
      "phrase": phrase,
      "filing": self.accession,
      "files_matching": len(hits),
      "hits": hits[:MAX_HITS],
    }


TOOL_DEFS: list[ToolDef] = [
  ToolDef(
    TOOL_NAME,
    "The SEC's EDGAR full-text search, restricted to this filing. Returns which files of the "
    "filing (the main document and its exhibits) contain the phrase, with a score each. It "
    "carries no text and no position: it says a phrase is in a file, not where.",
    {
      "type": "object",
      "properties": {"phrase": {"type": "string"}},
      "required": ["phrase"],
    },
  ),
]


def beside(
  tools: list[ToolDef],
  runner: Callable[[str, dict], str] | None,
  search: FilingSearch,
) -> tuple[list[ToolDef], Callable[[str, dict], str]]:
  def run(name: str, args: dict) -> str:
    if name == TOOL_NAME:
      try:
        return clip(json.dumps(search.search(args["phrase"])))
      except httpx.HTTPError as exc:
        return json.dumps({"error": f"EDGAR full-text search failed: {exc}"})
    if runner is None:
      return json.dumps({"error": f"unknown tool {name}"})
    return runner(name, args)

  return [*tools, *TOOL_DEFS], run
