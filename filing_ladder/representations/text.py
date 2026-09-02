"""Rungs 2 and 3 — the EDGAR primary document as text, with and without its inline XBRL.

Both transformations are mechanical and reproducible from the primary document alone:

* rung 3 keeps the document structure, every ``ix:`` tag and the ``ix:header`` (contexts and
  units — without it the context ids the facts reference are meaningless), and drops only
  styling: ``<style>``, ``<script>``, and ``style`` / ``class`` / ``id`` attributes.
* rung 2 starts from rung 3, drops the ``ix:header``, then every tag, unescapes entities and
  collapses whitespace.
"""

from __future__ import annotations

import html
import re

_STYLE = re.compile(r"<style\b.*?</style>", re.S | re.I)
_SCRIPT = re.compile(r"<script\b.*?</script>", re.S | re.I)
_ATTRS = re.compile(r'\s(?:style|class|id)="[^"]*"', re.I)
_IX_HEADER = re.compile(r"<ix:header\b.*?</ix:header>", re.S | re.I)
_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def to_ixbrl(primary_html: str) -> str:
  """Rung 3: styling stripped, inline XBRL kept."""
  stripped = _SCRIPT.sub("", _STYLE.sub("", primary_html))
  return _ATTRS.sub("", stripped)


def drop_ix_header(ixbrl: str) -> str:
  return _IX_HEADER.sub("", ixbrl)


def to_plain_text(primary_html: str) -> str:
  """Rung 2: tags gone, entities unescaped, whitespace collapsed."""
  body = drop_ix_header(to_ixbrl(primary_html))
  text = html.unescape(_TAG.sub(" ", body)).replace("\xa0", " ")
  return _WS.sub(" ", text).strip()


def count_ix_tags(primary_html: str) -> dict[str, int]:
  """Tag counts the protocol reports for a filing."""
  return {
    "ix:nonFraction": len(re.findall(r"<ix:nonFraction\b", primary_html)),
    "ix:nonNumeric": len(re.findall(r"<ix:nonNumeric\b", primary_html)),
  }


def estimate_tokens(n_bytes: int) -> int:
  """The bytes/4 estimate used for the token table; ``tokens --exact`` replaces it."""
  return n_bytes // 4
