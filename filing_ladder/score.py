"""Aggregation — per rung × tier × stratum, never across tiers.

Inputs are transcript records joined with their judgments; outputs are the rows of the
results table: accuracy, abstention, confident-wrong, cannot-attempt, provenance,
repeatability, empty-result-answered, and cost per question and per correct answer.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from statistics import mean


@dataclass
class Record:
  rung: str
  question_id: str
  run_index: int
  tier: str
  stratum: str
  category: str
  correct: bool
  abstained: bool
  contradiction: bool
  cannot_attempt: bool
  error: bool
  provenance_present: bool
  empty_result_answered: bool
  cost_usd: float | None
  input_tokens: int
  output_tokens: int
  cache_read_tokens: int
  cache_write_tokens: int
  turns: int
  tool_calls: int
  tool_errors: int
  wall_s: float
  extracted: float | str | None = None


@dataclass
class Cell:
  rung: str
  tier: str
  stratum: str
  n: int = 0
  questions: int = 0
  accuracy: float = 0.0
  abstention: float = 0.0
  confident_wrong: float = 0.0
  cannot_attempt: float = 0.0
  errors: float = 0.0
  provenance: float = 0.0
  repeatability: float | None = None
  empty_result_answered: float = 0.0
  cost_per_question: float | None = None
  cost_per_correct: float | None = None
  input_tokens_mean: float = 0.0
  output_tokens_mean: float = 0.0
  turns_mean: float = 0.0
  tool_calls_mean: float = 0.0
  tool_errors_mean: float = 0.0
  wall_s_mean: float = 0.0
  notes: list[str] = field(default_factory=list)


def aggregate(records: list[Record], by_stratum: bool = True) -> list[Cell]:
  groups: dict[tuple[str, str, str], list[Record]] = defaultdict(list)
  for r in records:
    key = (r.rung, r.tier, r.stratum if by_stratum else "all")
    groups[key].append(r)
  cells: list[Cell] = []
  for (rung, tier, stratum), rows in sorted(groups.items()):
    n = len(rows)
    cell = Cell(rung, tier, stratum, n=n, questions=len({r.question_id for r in rows}))
    cell.accuracy = _rate(rows, lambda r: r.correct)
    cell.abstention = _rate(rows, lambda r: r.abstained)
    cell.confident_wrong = _rate(
      rows,
      lambda r: (
        (not r.correct)
        and (not r.abstained)
        and (not r.cannot_attempt)
        and (not r.error)
      ),
    )
    cell.cannot_attempt = _rate(rows, lambda r: r.cannot_attempt)
    cell.errors = _rate(rows, lambda r: r.error)
    cell.provenance = _rate(rows, lambda r: r.provenance_present and r.correct)
    cell.empty_result_answered = _rate(rows, lambda r: r.empty_result_answered)
    costs = [r.cost_usd for r in rows if r.cost_usd is not None]
    if costs and len(costs) == n:
      cell.cost_per_question = round(mean(costs), 6)
      correct = sum(1 for r in rows if r.correct)
      cell.cost_per_correct = round(sum(costs) / correct, 6) if correct else None
    else:
      cell.notes.append("cost unavailable: no list price for the model")
    cell.input_tokens_mean = mean(r.input_tokens for r in rows)
    cell.output_tokens_mean = mean(r.output_tokens for r in rows)
    cell.turns_mean = mean(r.turns for r in rows)
    cell.tool_calls_mean = mean(r.tool_calls for r in rows)
    cell.tool_errors_mean = mean(r.tool_errors for r in rows)
    cell.wall_s_mean = mean(r.wall_s for r in rows)
    cell.repeatability = _repeatability(rows)
    cells.append(cell)
  return cells


def _rate(rows: list[Record], pred) -> float:
  return round(sum(1 for r in rows if pred(r)) / len(rows), 4) if rows else 0.0


def _repeatability(rows: list[Record]) -> float | None:
  """Share of questions whose k runs agree (same correctness and same extracted value)."""
  by_q: dict[str, list[Record]] = defaultdict(list)
  for r in rows:
    by_q[r.question_id].append(r)
  multi = [rs for rs in by_q.values() if len(rs) > 1]
  if not multi:
    return None
  agree = 0
  for rs in multi:
    outcomes = {(r.correct, r.abstained, _norm(r.extracted)) for r in rs}
    agree += int(len(outcomes) == 1)
  return round(agree / len(multi), 4)


def _norm(value: float | str | None) -> str:
  if isinstance(value, float):
    return f"{value:.4g}"
  return str(value)


def markdown_table(cells: list[Cell]) -> str:
  head = "| rung | tier | stratum | n | accuracy | abstain | confident-wrong | cannot attempt | error | provenance | repeat | empty→answered | $/q | $/correct | turns | tool calls | tool errors | in tok | out tok |"
  sep = "|" + "---|" * 19
  lines = [head, sep]
  for c in cells:
    lines.append(
      f"| {c.rung} | {c.tier} | {c.stratum} | {c.n} | {c.accuracy:.0%} | {c.abstention:.0%} | {c.confident_wrong:.0%} | "
      f"{c.cannot_attempt:.0%} | {c.errors:.0%} | {c.provenance:.0%} | {_pct(c.repeatability)} | {c.empty_result_answered:.0%} | "
      f"{_usd(c.cost_per_question)} | {_usd(c.cost_per_correct)} | {c.turns_mean:.1f} | {c.tool_calls_mean:.1f} | "
      f"{c.tool_errors_mean:.1f} | {c.input_tokens_mean:,.0f} | {c.output_tokens_mean:,.0f} |"
    )
  return "\n".join(lines)


def _pct(v: float | None) -> str:
  return "—" if v is None else f"{v:.0%}"


def _usd(v: float | None) -> str:
  return "—" if v is None else f"${v:,.4f}"
