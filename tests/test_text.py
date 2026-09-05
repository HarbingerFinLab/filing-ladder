from filing_ladder.representations.text import (
  count_ix_tags,
  drop_ix_header,
  to_ixbrl,
  to_plain_text,
)

SAMPLE = """<html><head><style>p{color:red}</style><script>x=1</script></head>
<body><div style="a:b" class="c" id="d"><ix:header><ix:hidden>h</ix:hidden><ix:resources>
<xbrli:context id="c1"><xbrli:period><xbrli:instant>2024-12-31</xbrli:instant></xbrli:period></xbrli:context>
</ix:resources></ix:header>
<hr/><a name="toc"></a><p id="p1"><span style="x:y">Net&nbsp;sales</span> <ix:nonFraction name="us-gaap:Revenues" contextRef="c1" unitRef="usd" id="f1">24,575</ix:nonFraction>&#8217;</p>
<ix:nonNumeric name="us-gaap:DebtDisclosureTextBlock" contextRef="c1" id="f2" continuedAt="k1">Debt</ix:nonNumeric>
<table><tr><td>Cell</td></tr></table>
<ix:continuation id="k1"><span>and the rest of the note</span></ix:continuation>
<ix:nonNumeric name="dei:DocumentType">10-K</ix:nonNumeric></div></body></html>"""


def test_ixbrl_keeps_tags_header_and_xbrl_ids_and_drops_styling():
  out = to_ixbrl(SAMPLE)
  assert "<style>" not in out and "<script>" not in out
  assert 'style="' not in out and 'class="' not in out
  assert "<ix:header>" in out and 'name="us-gaap:Revenues"' in out
  # the ids a contextRef or continuedAt resolves to stay; ids on HTML tags go
  assert '<xbrli:context id="c1">' in out
  assert '<ix:continuation id="k1">' in out and 'id="f1"' in out and 'id="f2"' in out
  assert 'id="d"' not in out and 'id="p1"' not in out


def test_ixbrl_drops_inline_scaffolding_but_keeps_tables():
  out = to_ixbrl(SAMPLE)
  assert (
    "<span" not in out and "<div" not in out and "<a " not in out and "<hr" not in out
  )
  assert "Net&nbsp;sales" in out  # the span's text survives its tag
  assert "and the rest of the note" in out
  assert "<table><tr><td>Cell</td></tr></table>" in out


def test_drop_header():
  assert "<ix:header>" not in drop_ix_header(to_ixbrl(SAMPLE))


def test_plain_text_unescapes_and_collapses():
  out = to_plain_text(SAMPLE)
  assert "Net sales 24,575" in out
  assert "’" in out
  assert "<" not in out and "  " not in out
  assert "h" not in out.split()  # the hidden header content is gone


def test_plain_text_is_not_touched_by_the_scaffold_strip():
  # rung 2 derives from the styling strip alone and turns every tag into a
  # space, as it always did — the scaffold strip that removes span/div tags
  # from rung 3 never reaches it, so the text is byte-for-byte what it was
  html = "<p><span>reve</span><span>nue</span></p><div>a</div><div>b</div>"
  assert to_plain_text(html) == "reve nue a b"


def test_counts():
  assert count_ix_tags(SAMPLE) == {"ix:nonFraction": 1, "ix:nonNumeric": 2}
