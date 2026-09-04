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


def test_vals_contradiction_operators_are_kept_separate_from_points():
  qs = load_vals_public()
  assert sum(len(q.contradictions) for q in qs) > 0
  assert not any("contradict" in p.lower() for q in qs for p in q.rubric)
  assert all(q.rubric for q in qs)


def test_template_rubrics_carry_no_negatives_as_points():
  from filing_ladder.questions import load_templates

  for q in load_templates():
    assert not any(p.upper().startswith("CONTRADICTION") for p in q.rubric)
    if q.gold_type == "text":
      assert q.contradictions
