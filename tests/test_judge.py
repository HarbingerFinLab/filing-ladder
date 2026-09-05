from filing_ladder.judge import parse_final, parse_number, score_numeric

ANSWER = """Working: capex from the cash flow statement.

ANSWER: $1,398 million
PROVENANCE: Consolidated Statement of Cash Flows, "Purchases of property, plant and equipment"
CONFIDENCE: high"""


def test_parse_final():
  f = parse_final(ANSWER)
  assert f.answer == "$1,398 million" and f.confidence == "high" and not f.abstained
  assert "Cash Flows" in f.provenance


def test_parse_final_abstain():
  f = parse_final(
    "ANSWER: Cannot determine from the provided source\nPROVENANCE: none\nCONFIDENCE: abstain"
  )
  assert f.abstained


def test_parse_number_scales_and_signs():
  assert parse_number("$1,398 million") == (1_398_000_000.0, "million")
  assert parse_number("24.6 billion")[0] == 24_600_000_000.0
  assert parse_number("(1,234)")[0] == -1234.0
  assert parse_number("18.78%") == (18.78, "%")
  assert parse_number("no digits") is None


def test_score_numeric_tolerance_and_scale():
  assert score_numeric(ANSWER, "1,398", "millions")["correct"]
  assert score_numeric(ANSWER, "1,410", "millions")["correct"]  # within 1%
  assert not score_numeric(ANSWER, "1,500", "millions")["correct"]
  unscaled = ANSWER.replace("$1,398 million", "1398")
  assert score_numeric(unscaled, "1,398", "millions")[
    "correct"
  ]  # gold's scale allowed for a bare number
  abstain = "ANSWER: Cannot determine from the provided source\nPROVENANCE: -\nCONFIDENCE: abstain"
  s = score_numeric(abstain, "1,398", "millions")
  assert s["abstained"] and not s["correct"]


def test_parse_number_skips_names_quarters_and_years():
  assert parse_number(
    "3M's Q4 2024 net sales were USD 6.01 billion (USD 6,010,000,000)"
  ) == (6_010_000_000.0, "billion")
  assert parse_number("In FY2024 3M reported 24,575 million") == (
    24_575_000_000.0,
    "million",
  )
  assert parse_number("Q4 2024: 6,010") == (6010.0, None)
  assert (
    parse_number("about 2024 units")[0] == 2024.0
  )  # not a year when it is the only number


def test_score_numeric_company_name_case():
  text = "ANSWER: 3M's Q4 2024 net sales were USD 6.01 billion (USD 6,010,000,000)\nPROVENANCE: x\nCONFIDENCE: high"
  assert score_numeric(text, "6,010", "millions")["correct"]


def test_parse_number_ignores_list_commas_and_dates():
  text = "3M's Q4 FY2024 (October 1 – December 31, 2024) net sales were $6.010 billion USD (6,010,000,000 USD)"
  assert parse_number(text) == (6_010_000_000.0, "billion")
  assert parse_number("December 31, 2024: 1,085") == (1085.0, None)


def test_parse_final_reads_the_last_block_not_a_heading_in_the_reasoning():
  """A bold "Answer:" heading in the reasoning is not the answer; the final block is."""
  text = (
    "Let me locate the figure directly.\n\n**Answer:**\n\n3M's total purchases were "
    "$1,181 million.\n\nANSWER: $1,181 million (USD)\nPROVENANCE: fact f-413 in facts.csv\n"
    "CONFIDENCE: high"
  )
  f = parse_final(text)
  assert f.answer == "$1,181 million (USD)"
  assert f.provenance == "fact f-413 in facts.csv"
  assert f.confidence == "high"


def test_parse_final_prefers_a_later_revised_block():
  text = (
    "ANSWER: $1,100 million\nPROVENANCE: the narrative\nCONFIDENCE: medium\n\n"
    "Checking the statement instead.\n\n"
    "ANSWER: $1,085 million\nPROVENANCE: the income statement\nCONFIDENCE: high"
  )
  f = parse_final(text)
  assert f.answer == "$1,085 million"
  assert f.confidence == "high"


def test_parse_final_strips_markdown_emphasis_from_the_block():
  text = "**ANSWER:** **$5 billion**\n**PROVENANCE:** _Note 6_\n**CONFIDENCE:** *high*"
  f = parse_final(text)
  assert f.answer == "$5 billion"
  assert f.provenance == "Note 6"
  assert f.confidence == "high"


def test_parse_final_falls_back_to_an_earlier_complete_block():
  """A trailing ANSWER with no PROVENANCE/CONFIDENCE after it does not shadow a full block."""
  text = (
    "ANSWER: $1,085 million\nPROVENANCE: the income statement\nCONFIDENCE: high\n\n"
    "ANSWER: (draft, cut off"
  )
  assert parse_final(text).answer == "$1,085 million"
