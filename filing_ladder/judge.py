"""Scoring: numeric answers mechanically, text answers by rubric decomposition plus a
contradiction check (the Vals design), abstention detected from the output contract.

The judge sees the question, the gold and the candidate answer only — never the rung.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .providers.base import Provider

_FINAL = re.compile(
  r"ANSWER:\s*(?P<answer>.+?)\s*(?:\n|$).*?PROVENANCE:\s*(?P<prov>.+?)\s*(?:\n|$).*?CONFIDENCE:\s*(?P<conf>\w+)",
  re.S | re.I,
)
_ABSTAIN_PHRASES = (
  "cannot determine",
  "cannot be determined",
  "not available in",
  "does not contain",
  "not provided in",
  "unable to determine",
  "insufficient information",
)
_NUMBER = re.compile(
  r"(?P<cur>\$|USD\s*|US\$\s*)?(?P<neg>\()?(?P<sign>-)?(?P<num>(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)(?P<close>\))?"
  r"\s*(?P<unit>%|percent|billions?|millions?|thousands?|bn|mn|mm|k|m|b)?(?=$|[^A-Za-z'’])",
  re.I,
)
_LETTER_UNITS = {"k", "m", "b", "mm", "mn", "bn"}
SCALE = {
  "thousand": 1e3,
  "thousands": 1e3,
  "k": 1e3,
  "million": 1e6,
  "millions": 1e6,
  "mn": 1e6,
  "mm": 1e6,
  "m": 1e6,
  "billion": 1e9,
  "billions": 1e9,
  "bn": 1e9,
  "b": 1e9,
}


@dataclass
class Final:
  answer: str
  provenance: str
  confidence: str
  abstained: bool


def parse_final(text: str) -> Final:
  m = _FINAL.search(text or "")
  if m:
    answer, prov, conf = (
      m.group("answer").strip(),
      m.group("prov").strip(),
      m.group("conf").strip().lower(),
    )
  else:
    answer, prov, conf = (text or "").strip()[-600:], "", "unknown"
  abstained = conf == "abstain" or any(p in answer.lower() for p in _ABSTAIN_PHRASES)
  return Final(answer, prov, conf, abstained)


def candidates(text: str) -> list[tuple[float, str | None, str]]:
  """Every number in the text as (value, unit, kind): kind is "figure" when it carried a
  currency sign, a scale word, a percent sign, a decimal point or a thousands separator;
  "year" for a bare 1900-2100 integer; "bare" otherwise. Digits glued to a letter (Q4,
  FY2024, K2) or a name (3M's) are not numbers."""
  out: list[tuple[float, str | None, str]] = []
  for m in _NUMBER.finditer(text or ""):
    i = m.start("num")
    if i > 0 and (text[i - 1].isalpha() or text[i - 1] in "'’"):
      continue
    raw = m.group("num")
    unit = (m.group("unit") or "").lower() or None
    if unit in ("%", "percent"):
      unit = "%"

    if unit in _LETTER_UNITS and not (m.group("cur") or "." in raw or "," in raw):
      continue  # "3M" the company, not three million; "$3M" and "3.5B" still count
    negative = bool(m.group("sign")) or (
      bool(m.group("neg")) and bool(m.group("close"))
    )
    try:
      value = float(raw.replace(",", ""))
    except ValueError:
      continue
    if unit in SCALE:
      value *= SCALE[unit]
    if negative:
      value = -value
    if m.group("cur") or unit is not None or "." in raw or "," in raw:
      kind = "figure"
    elif raw.isdigit() and len(raw) == 4 and 1900 <= int(raw) <= 2100:
      kind = "year"
    else:
      kind = "bare"
    out.append((value, unit, kind))
  return out


def parse_number(text: str) -> tuple[float, str | None] | None:
  """The figure an answer states: the first figure, else the first bare number, else a year."""
  found = candidates(text)
  for wanted in ("figure", "bare", "year"):
    for value, unit, kind in found:
      if kind == wanted:
        return value, unit
  return None


def scale_factor(scale: str | None) -> float:
  return {"thousands": 1e3, "millions": 1e6, "billions": 1e9}.get(
    (scale or "").lower(), 1.0
  )


def score_numeric(
  answer_text: str, gold: str, gold_scale: str | None, tolerance: float = 0.01
) -> dict:
  final = parse_final(answer_text)
  parsed = parse_number(final.answer)
  gold_parsed = parse_number(gold)
  if gold_parsed is None:
    return {"correct": False, "abstained": final.abstained, "error": "gold not numeric"}
  gold_value = gold_parsed[0] * (
    scale_factor(gold_scale) if gold_parsed[1] is None else 1.0
  )
  if final.abstained or parsed is None:
    return {
      "correct": False,
      "abstained": final.abstained,
      "extracted": None,
      "gold": gold_value,
    }
  value = parsed[0]
  candidates = [value]
  if parsed[1] is None:  # unscaled number: allow the gold's scale
    candidates += [value * f for f in (1e3, 1e6, 1e9)]
  correct = any(
    abs(c - gold_value) <= tolerance * max(abs(gold_value), 1e-9) for c in candidates
  )
  return {
    "correct": correct,
    "abstained": False,
    "extracted": value,
    "gold": gold_value,
  }


JUDGE_SYSTEM = """You are grading an analyst's answer to a financial question against an expert gold answer, one rubric point at a time.

Return ONLY JSON of this shape:
{"points": [{"criteria": "<rubric point verbatim>", "met": true|false, "evidence": "<quote from the answer or 'absent'>"}],
 "contradiction": true|false,
 "contradiction_evidence": "<the conflicting statement, or ''>",
 "abstained": true|false,
 "provenance_present": true|false}

Rules: judge each point separately and literally; numbers match if within 1% after unit and scale normalization. "contradiction" is true only if some statement in the answer conflicts with the gold (a wrong figure, a wrong direction, a wrong period) — an incomplete answer is not a contradiction. "abstained" is true if the answer declines to give a figure or conclusion. "provenance_present" is true if the answer cites where its figures came from."""


def judge_rubric(
  judge: Provider, question: str, gold: str, rubric: list[str], answer_text: str
) -> dict:
  user = json.dumps(
    {
      "question": question,
      "gold_answer": gold,
      "rubric": rubric,
      "candidate_answer": answer_text,
    },
    ensure_ascii=False,
  )
  conversation = judge.start(JUDGE_SYSTEM, user, [], [])
  turn = judge.step(conversation)
  payload = _extract_json(turn.text)
  payload["judge_usage"] = turn.usage.as_dict()
  payload["judge_model"] = judge.model
  return payload


def _extract_json(text: str) -> dict:
  text = text.strip()
  if text.startswith("```"):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.S)
  try:
    return json.loads(text)
  except json.JSONDecodeError:
    m = re.search(r"\{.*\}", text, re.S)
    if m:
      try:
        return json.loads(m.group(0))
      except json.JSONDecodeError:
        pass
  return {
    "points": [],
    "contradiction": False,
    "abstained": False,
    "provenance_present": False,
    "judge_error": text[:500],
  }
