"""Run directories and the JSONL files a run leaves behind (published later as a dataset)."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


@dataclass(frozen=True)
class RunDir:
  path: Path

  @property
  def transcripts(self) -> Path:
    return self.path / "transcripts.jsonl"

  @property
  def judgments(self) -> Path:
    return self.path / "judgments.jsonl"

  @property
  def config(self) -> Path:
    return self.path / "run.json"

  @property
  def summary_json(self) -> Path:
    return self.path / "summary.json"

  @property
  def summary_md(self) -> Path:
    return self.path / "summary.md"


def new_run(results_dir: Path, label: str) -> RunDir:
  stamp = time.strftime("%Y%m%d-%H%M%S")
  safe = "".join(ch if ch.isalnum() or ch in "-._" else "-" for ch in label)[:60]
  run = RunDir(results_dir / f"{stamp}-{safe}")
  run.path.mkdir(parents=True, exist_ok=False)
  return run


def append_jsonl(path: Path, record: dict) -> None:
  with path.open("a", encoding="utf-8") as fh:
    fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def read_jsonl(path: Path) -> Iterator[dict]:
  if not path.exists():
    return iter(())
  return (
    json.loads(line)
    for line in path.read_text(encoding="utf-8").splitlines()
    if line.strip()
  )


def write_json(path: Path, payload: dict | list) -> None:
  path.write_text(
    json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
  )


def latest_run(results_dir: Path) -> RunDir | None:
  runs = (
    sorted(p for p in results_dir.iterdir() if p.is_dir())
    if results_dir.exists()
    else []
  )
  return RunDir(runs[-1]) if runs else None


def done_keys(run: RunDir, drop_errors: bool = False) -> set[tuple[str, str, int]]:
  """(rung, question_id, run_index) already in the transcripts — lets a run resume.

  With ``drop_errors`` the records that ended in a transport error are removed from the
  file (so they are re-run) and not returned.
  """
  records = list(read_jsonl(run.transcripts))
  if drop_errors:
    kept = [r for r in records if r.get("stop_reason") != "error"]
    if len(kept) != len(records):
      run.transcripts.write_text(
        "".join(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in kept),
        encoding="utf-8",
      )
    records = kept
  return {(r["rung"], r["question_id"], int(r["run_index"])) for r in records}


def iter_pairs(
  transcripts: Iterable[dict], judgments: Iterable[dict]
) -> Iterator[tuple[dict, dict | None]]:
  by_key = {(j["rung"], j["question_id"], int(j["run_index"])): j for j in judgments}
  for t in transcripts:
    yield t, by_key.get((t["rung"], t["question_id"], int(t["run_index"])))
