"""Rungs 2 and 3 — the EDGAR primary document as text, with and without its inline XBRL.

Both transformations are mechanical and reproducible from the primary document alone:

* rung 3 keeps every ``ix:`` tag with its attributes and the ``ix:header`` (contexts and
  units — the ``contextRef`` on every fact and the ``continuedAt`` on every split note point
  at ids in there, so the ids on XBRL tags stay), and drops what carries nothing for a reader:
  ``<style>``, ``<script>``, ``style`` / ``class`` attributes, ``id`` attributes on HTML tags,
  and the inline scaffolding EDGAR renderers leave — ``<span>``, ``<div>``, ``<a>``, ``<hr>``
  tags (a ``<div>`` becomes a line break). Tables keep their markup.
* rung 2 starts from the styling strip alone, drops the ``ix:header``, then every tag,
  unescapes entities and collapses whitespace — the scaffold strip does not touch it.
"""

from __future__ import annotations

import html
import re

_STYLE = re.compile(r"<style\b.*?</style>", re.S | re.I)
_SCRIPT = re.compile(r"<script\b.*?</script>", re.S | re.I)
_STYLE_ATTRS = re.compile(r'\s(?:style|class)="[^"]*"', re.I)
# An id on an HTML tag (no namespace prefix) is a link target; an id on an ix:/xbrli:/xbrldi:
# tag is what a contextRef or continuedAt resolves to, and stays.
_HTML_ID = re.compile(
  r'(<[a-zA-Z][a-zA-Z0-9]*(?![:A-Za-z0-9])[^>]*?)\sid="[^"]*"', re.I
)
_IX_HEADER = re.compile(r"<ix:header\b.*?</ix:header>", re.S | re.I)
_SPAN_A_HR = re.compile(r"</?span\b[^>]*>|</?a\b[^>]*>|<hr\b[^>]*>", re.I)
_DIV = re.compile(r"</?div\b[^>]*>", re.I)
_BLANK_LINES = re.compile(r"\n[ \t]*(?:\n[ \t]*)+")
_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def _strip_styling(primary_html: str) -> str:
  stripped = _SCRIPT.sub("", _STYLE.sub("", primary_html))
  stripped = _STYLE_ATTRS.sub("", stripped)
  return _HTML_ID.sub(r"\1", stripped)


def _strip_scaffold(styled: str) -> str:
  out = _SPAN_A_HR.sub("", styled)
  out = _DIV.sub("\n", out)
  return _BLANK_LINES.sub("\n", out)


def to_ixbrl(primary_html: str) -> str:
  """Rung 3: styling and inline scaffolding stripped, inline XBRL kept whole."""
  return _strip_scaffold(_strip_styling(primary_html))


def drop_ix_header(ixbrl: str) -> str:
  return _IX_HEADER.sub("", ixbrl)


def to_plain_text(primary_html: str) -> str:
  """Rung 2: tags gone, entities unescaped, whitespace collapsed."""
  body = drop_ix_header(_strip_styling(primary_html))
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
