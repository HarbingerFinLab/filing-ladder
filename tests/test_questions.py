from collections import Counter

from filing_ladder.questions import (
  load_all,
  load_vals_public,
  manifest,
  runnable,
  validate,
)


def test_vals_public_loads_50():
  qs = load_vals_public()
  assert len(qs) == 50
  assert all(q.set == "vals-public-50" and q.gold and q.rubric for q in qs)
  cats = Counter(q.category for q in qs)
  assert cats["Simple retrieval - Quantitative"] == 9 and len(cats) == 9


def test_validate_and_manifest():
  qs = load_all()
  assert validate(qs) == []
  m = manifest()
  assert any(k.endswith("public-50.csv") for k in m["files"])
  assert all(len(h) == 64 for h in m["files"].values())
  # The manifest counts what runs; every dropped question is listed with its reason.
  assert m["questions"] == len(runnable(qs))
  assert m["questions"] + len(m["dropped"]) == len(qs)
  assert m["unresolved_filings"] == []


def test_dropped_questions_carry_a_reason_and_stay_out_of_the_run():
  qs = load_all()
  dropped = [q for q in qs if q.dropped]
  assert dropped and all(q.set == "vals-public-50" for q in dropped)
  assert all(len(q.dropped) > 20 for q in dropped)
  assert not any(q.dropped for q in runnable(qs))
  assert all(q.filing is not None for q in runnable(qs))
