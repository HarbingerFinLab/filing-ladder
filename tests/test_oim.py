from filing_ladder.representations.oim import (
  fact_stats,
  is_text_block,
  strip_text_blocks_json,
)


def test_is_text_block_rules():
  assert is_text_block("us-gaap:AccountingPoliciesTextBlock", "short")
  assert is_text_block("us-gaap:EnvironmentalCostsPolicy", "<p>markup</p>")
  assert is_text_block("us-gaap:Revenues", "x" * 300)
  assert not is_text_block("us-gaap:Revenues", "24575000000")


def test_strip_json():
  doc = {
    "documentInfo": {"documentType": "https://xbrl.org/2021/xbrl-json"},
    "facts": {
      "f1": {
        "value": "1",
        "dimensions": {
          "concept": "us-gaap:Revenues",
          "entity": "cik:1",
          "period": "2024-01-01/2025-01-01",
        },
      },
      "f2": {
        "value": "<div>long</div>",
        "dimensions": {
          "concept": "us-gaap:NotesTextBlock",
          "entity": "cik:1",
          "period": "2024-01-01/2025-01-01",
        },
      },
      "f3": {
        "value": "2",
        "dimensions": {
          "concept": "us-gaap:Revenues",
          "entity": "cik:1",
          "period": "2024-01-01/2025-01-01",
          "srt:ProductOrServiceAxis": "mmm:Foo",
        },
      },
    },
  }
  stripped, removed = strip_text_blocks_json(doc)
  assert removed == 1 and set(stripped["facts"]) == {"f1", "f3"}
  assert doc["facts"]  # original untouched
  assert fact_stats(doc) == {"facts": 3, "text_blocks": 1, "dimensional": 1}
