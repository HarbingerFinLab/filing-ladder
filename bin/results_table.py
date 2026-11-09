#!/usr/bin/env python3
"""Every published row in one table, regenerated from the published runs.

Reads each ``results/v*/`` directory's ``summary.json`` (the judge-scored report), ``run.json`` (the
model) and, where present, ``form-scoring.json`` (the §11 cross-filing rule applied to a row's T2),
and rewrites the block between the markers in ``results/README.md``. Two tables: every row of every
version, ranked within its version by cost per correct lookup; and the rows that recur across
versions, which is the cost curve the ladder exists to measure.

    uv run python bin/results_table.py            # rewrite results/README.md
    uv run python bin/results_table.py --print    # print the markdown only
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
START, END = "<!-- results-table:start -->", "<!-- results-table:end -->"
FORM_SCORED = "‡"


def version_of(dirname: str) -> str:
  return dirname.split("-")[0]


def version_key(v: str) -> tuple[int, ...]:
  return tuple(int(p) for p in v.lstrip("v").split("."))


def family(label: str) -> str:
  """The row a later version re-ran with one change: ``7a.1`` belongs with ``7a``."""
  return re.sub(r"\.\d+$", "", label)


def load_runs() -> list[dict]:
  sys.path.insert(0, str(ROOT))
  from filing_ladder.ladder import BY_RUNG, Rung

  runs = []
  for d in sorted(RESULTS.glob("v*"), key=lambda p: version_key(version_of(p.name))):
    if not (d / "summary.json").exists():
      continue
    summary = json.loads((d / "summary.json").read_text())
    model = json.loads((d / "run.json").read_text())["model"]
    form = (
      json.loads((d / "form-scoring.json").read_text())
      if (d / "form-scoring.json").exists()
      else {}
    )
    rows: dict[str, dict] = {}
    for e in summary["by_rung_tier"]:
      if e.get("stratum", "all") != "all":
        continue
      row = rows.setdefault(
        e["rung"], {"label": e["rung"], "name": BY_RUNG[Rung(e["rung"])].name}
      )
      tier = dict(e)
      key = f"{e['rung']}_{e['tier']}"
      if (
        key in form
      ):  # the cross-filing rule, applied: accuracy and $/correct re-scored
        f = form[key]["form_scored"]
        tier["accuracy"] = f["accuracy"]
        tier["cost_per_correct"] = f["cost_per_correct"]
        tier["confident_wrong"] = 1 - f["accuracy"] - e["abstention"]
        tier["form_scored"] = True
      row[e["tier"]] = tier
    runs.append(
      {"dir": d.name, "version": version_of(d.name), "model": model, "rows": rows}
    )
  return runs


def pct(x: float) -> str:
  return f"{100 * x:.0f}%"


def usd(x: float) -> str:
  return f"${x:.3f}"


def cell(t: dict | None, field: str, fmt) -> str:
  if not t:
    return "—"
  mark = (
    FORM_SCORED
    if t.get("form_scored")
    and field in ("accuracy", "cost_per_correct", "confident_wrong")
    else ""
  )
  return fmt(t[field]) + mark


def per_question(row: dict) -> str:
  tiers = [row[t] for t in ("T1", "T2") if t in row]
  n = sum(t["n"] for t in tiers)
  return usd(sum(t["cost_per_question"] * t["n"] for t in tiers) / n) if n else "—"


def render(runs: list[dict]) -> str:
  out = []
  out.append("### Every published row\n")
  out.append(
    "Judge-scored, as each run's `summary.json` reports it, except where marked "
    f"{FORM_SCORED}: the §11 cross-filing rule applied (an answer read from a filing other than the "
    "question's is a confident-wrong of the form; `form-scoring.json` in that run). Ranked within "
    "each version by cost per correct lookup. T1 is 60 records a row, T2 is 54 (k = 3). "
    "Confident-wrong is every answer that is neither correct nor an abstention. Each run's README "
    "carries its errata: v0.1's 7a is read with PROTOCOL §9 (2026-09-06, what its index contained); "
    "v0.2's 4c and \"+doc\" rows with §9 (2026-11-09, the served tools' empty schemas). Neither "
    "changed a score.\n"
  )
  out.append(
    "| Version | Model | Row | Form | T1 acc | T1 conf-wrong | T1 $/correct | T2 acc | T2 conf-wrong | T2 $/correct | $/question |"
  )
  out.append("|---|---|---|---|---|---|---|---|---|---|---|")
  for run in runs:
    rows = sorted(
      run["rows"].values(),
      key=lambda r: r.get("T1", {}).get("cost_per_correct", float("inf")),
    )
    for r in rows:
      t1, t2 = r.get("T1"), r.get("T2")
      out.append(
        f"| {run['version']} | `{run['model']}` | **{r['label']}** | {r['name']} | "
        f"{cell(t1, 'accuracy', pct)} | {cell(t1, 'confident_wrong', pct)} | {cell(t1, 'cost_per_correct', usd)} | "
        f"{cell(t2, 'accuracy', pct)} | {cell(t2, 'confident_wrong', pct)} | {cell(t2, 'cost_per_correct', usd)} | {per_question(r)} |"
      )
  out.append("")
  out.append("### The rows that recur — the cost curve\n")
  out.append(
    "The same row across versions. The model changed between v0.1.1 and v0.2 (rung 2, the plain text "
    "read whole, is the anchor that separates the model's move from the tools'); the \"+doc\" "
    "instrument changed from the harness's two text tools (v0.1.1) to xbrlkit's (v0.2); `.1` rows "
    "are their base with one friction removed (PROTOCOL §12).\n"
  )
  out.append(
    "| Row | Version | Model | T1 acc | T1 $/correct | T2 acc | T2 $/correct |"
  )
  out.append("|---|---|---|---|---|---|---|")
  seen: dict[str, list[tuple[dict, dict]]] = {}
  for run in runs:
    for r in run["rows"].values():
      seen.setdefault(family(r["label"]), []).append((run, r))
  for fam in sorted(seen, key=lambda f: (len(f), f)):
    entries = seen[fam]
    if len(entries) < 2:
      continue
    for run, r in entries:
      t1, t2 = r.get("T1"), r.get("T2")
      out.append(
        f"| **{r['label']}** | {run['version']} | `{run['model']}` | {cell(t1, 'accuracy', pct)} | {cell(t1, 'cost_per_correct', usd)} | "
        f"{cell(t2, 'accuracy', pct)} | {cell(t2, 'cost_per_correct', usd)} |"
      )
  out.append("")
  out.append(
    f"*Generated by `bin/results_table.py` from {len(runs)} published runs; regenerate with `just results-table`.*"
  )
  return "\n".join(out) + "\n"


def main() -> None:
  md = render(load_runs())
  if "--print" in sys.argv:
    print(md, end="")
    return
  readme = RESULTS / "README.md"
  text = readme.read_text()
  if START not in text or END not in text:
    raise SystemExit(f"{readme} has no {START} … {END} block")
  head, rest = text.split(START, 1)
  _, tail = rest.split(END, 1)
  readme.write_text(f"{head}{START}\n{md}{END}{tail}")
  print(f"wrote {readme.relative_to(ROOT)}")


if __name__ == "__main__":
  main()
