from collections import Counter

from filing_ladder.questions import load_all, load_vals_public, manifest, validate


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
  assert m["questions"] >= 50 and any(k.endswith("public-50.csv") for k in m["files"])
  assert all(len(h) == 64 for h in m["files"].values())
