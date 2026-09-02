from filing_ladder.representations.text import (
  count_ix_tags,
  drop_ix_header,
  to_ixbrl,
  to_plain_text,
)

SAMPLE = """<html><head><style>p{color:red}</style><script>x=1</script></head>
<body><div style="a:b" class="c" id="d"><ix:header><ix:hidden>h</ix:hidden></ix:header>
<p>Net&nbsp;sales <ix:nonFraction name="us-gaap:Revenues" contextRef="c1" unitRef="usd">24,575</ix:nonFraction>&#8217;</p>
<ix:nonNumeric name="dei:DocumentType">10-K</ix:nonNumeric></div></body></html>"""


def test_ixbrl_keeps_tags_and_header_and_drops_styling():
  out = to_ixbrl(SAMPLE)
  assert "<style>" not in out and "<script>" not in out
  assert 'style="' not in out and 'class="' not in out and 'id="' not in out
  assert "<ix:header>" in out and 'name="us-gaap:Revenues"' in out


def test_drop_header():
  assert "<ix:header>" not in drop_ix_header(to_ixbrl(SAMPLE))


def test_plain_text_unescapes_and_collapses():
  out = to_plain_text(SAMPLE)
  assert "Net sales 24,575" in out
  assert "’" in out
  assert "<" not in out and "  " not in out
  assert "h" not in out.split()  # the hidden header content is gone


def test_counts():
  assert count_ix_tags(SAMPLE) == {"ix:nonFraction": 1, "ix:nonNumeric": 1}
