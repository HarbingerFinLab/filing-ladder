"""Question sets: loading, validation, and the hashes the pre-registered protocol publishes.

Two sets. (i) Vals AI's 50 public Finance Agent questions (CC BY 4.0), vendored as they
were published, with their gold answers and rubrics. (ii) FinanceBench-shaped templates
re-instantiated on current filings, authored here, across the five strata — numeric gold read
from the document by a person, never from a graph.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .ladder import Stratum, Tier

QUESTIONS_DIR = Path(__file__).resolve().parent.parent / "questions"
VALS_CSV = QUESTIONS_DIR / "vals-finance-agent-public-50.csv"
TEMPLATES_DIR = QUESTIONS_DIR / "templates"

VALS_TYPE_TO_TIER: dict[str, Tier] = {
  "Simple retrieval - Quantitative": Tier.T1_LOOKUP,
  "Simple retrieval - Qualitative": Tier.T1_LOOKUP,
  "Complex Retrieval": Tier.T2_DERIVED,
  "Numerical Reasoning": Tier.T2_DERIVED,
  "Beat or Miss": Tier.T2_DERIVED,
  "Financial Modeling  Projections": Tier.T2_DERIVED,
  "Adjustments": Tier.T2_DERIVED,
  "Market Analysis": Tier.T2_DERIVED,
  "Trends": Tier.T2_DERIVED,
}


@dataclass
class Filing:
  cik: str
  accession: str
  ticker: str | None = None
  fiscal_year: int | None = None
  form: str | None = None

  def hint(self) -> str:
    bits = [
      b
      for b in (
        self.ticker,
        self.form,
        f"FY{self.fiscal_year}" if self.fiscal_year else None,
      )
      if b
    ]
    return f"{' '.join(bits)} (CIK {self.cik}, accession {self.accession})"


@dataclass
class Question:
  id: str
  set: str
  question: str
  gold_type: str  # numeric | text
  gold: str
  tier: str
  stratum: str
  category: str = ""
  rubric: list[str] = field(default_factory=list)
  gold_unit: str | None = None
  gold_scale: str | None = None  # units | thousands | millions | billions | percent
  gold_source: str = ""
  filing: Filing | None = None
  expert_minutes: float | None = None
  notes: str = ""
  dropped: str = ""  # non-empty = excluded from the run, with the disclosed reason

  def as_dict(self) -> dict:
    return asdict(self)

  @classmethod
  def from_dict(cls, d: dict) -> Question:
    d = dict(d)
    filing = d.pop("filing", None)
    q = cls(**d)
    q.filing = Filing(**filing) if filing else None
    return q


def load_vals_public(path: Path = VALS_CSV) -> list[Question]:
  questions: list[Question] = []
  with path.open(newline="", encoding="utf-8-sig") as fh:
    for i, row in enumerate(csv.DictReader(fh), start=1):
      qtype = (row.get("Question Type") or "").strip()
      rubric: list[str] = []
      raw = row.get("Rubric") or ""
      if raw.strip():
        try:
          rubric = [str(r.get("criteria", r)) for r in json.loads(raw)]
        except json.JSONDecodeError:
          rubric = [raw]
      minutes = row.get("Expert time (mins)")
      questions.append(
        Question(
          id=f"vals-{i:02d}",
          set="vals-public-50",
          question=row["Question"].strip(),
          gold_type="text",
          gold=row["Answer"].strip(),
          tier=VALS_TYPE_TO_TIER.get(qtype, Tier.T2_DERIVED),
          stratum=Stratum.LOOKUP,
          category=qtype,
          rubric=rubric,
          gold_source="vals-expert",
          expert_minutes=float(minutes) if minutes and minutes.strip() else None,
        )
      )
  return questions


def load_templates(directory: Path = TEMPLATES_DIR) -> list[Question]:
  questions: list[Question] = []
  for path in sorted(directory.glob("*.jsonl")):
    with path.open(encoding="utf-8") as fh:
      for line in fh:
        line = line.strip()
        if line and not line.startswith("#"):
          questions.append(Question.from_dict(json.loads(line)))
  return questions


def load_overrides(directory: Path = QUESTIONS_DIR) -> dict[str, dict]:
  """Per-question filing resolutions for the Vals set live beside the CSV, never inside it."""
  path = directory / "vals-filing-resolution.jsonl"
  out: dict[str, dict] = {}
  if path.exists():
    for line in path.read_text(encoding="utf-8").splitlines():
      if line.strip() and not line.startswith("#"):
        row = json.loads(line)
        out[row["id"]] = row
  return out


def load_all() -> list[Question]:
  vals = load_vals_public()
  overrides = load_overrides()
  for q in vals:
    o = overrides.get(q.id)
    if o and o.get("filing"):
      q.filing = Filing(**o["filing"])
    if o and o.get("notes"):
      q.notes = o["notes"]
    if o and o.get("drop"):
      q.dropped = o["drop"]
  return vals + load_templates()


def runnable(questions: list[Question]) -> list[Question]:
  return [q for q in questions if not q.dropped]


def validate(questions: list[Question]) -> list[str]:
  problems: list[str] = []
  seen: set[str] = set()
  for q in questions:
    if q.id in seen:
      problems.append(f"{q.id}: duplicate id")
    seen.add(q.id)
    if q.tier not in set(Tier):
      problems.append(f"{q.id}: bad tier {q.tier}")
    if q.stratum not in set(Stratum):
      problems.append(f"{q.id}: bad stratum {q.stratum}")
    if q.gold_type not in ("numeric", "text"):
      problems.append(f"{q.id}: bad gold_type {q.gold_type}")
    if q.gold_type == "text" and not q.rubric:
      problems.append(f"{q.id}: text gold without a rubric")
    if not q.gold.strip():
      problems.append(f"{q.id}: empty gold")
  return problems


def sha256(path: Path) -> str:
  return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest() -> dict:
  """What the frozen protocol publishes: file hashes and counts per set."""
  files = [VALS_CSV, *sorted(TEMPLATES_DIR.glob("*.jsonl"))]
  for extra in ("vals-filing-resolution.jsonl", "filing-token-counts.json"):
    if (QUESTIONS_DIR / extra).exists():
      files.append(QUESTIONS_DIR / extra)
  questions = load_all()
  live = runnable(questions)
  by_set: dict[str, int] = {}
  for q in live:
    by_set[q.set] = by_set.get(q.set, 0) + 1
  return {
    "files": {
      p.relative_to(QUESTIONS_DIR.parent).as_posix(): sha256(p)
      for p in files
      if p.exists()
    },
    "questions": len(live),
    "by_set": by_set,
    "dropped": {q.id: q.dropped for q in questions if q.dropped},
    "unresolved_filings": [q.id for q in live if q.filing is None],
  }
