---
description: Run the full test and code-quality gate, fixing failures to green.
argument-hint: '[test-path]'
---

Run `just test-all` and fix every failure until the gate is green.

## What `just test-all` runs

```
just test → just lint → just typecheck
```

`just test` is `uv run pytest -q` — unit tests only; anything marked `network` (EDGAR, a model
provider, the `sec` MCP) is skipped by default and must stay that way. `just lint` is check-only
(`ruff check` + `ruff format --check`); `just format` is the auto-writer and **mutates the working
tree** — stage what it rewrote. Only the pytest stage prints a `passed`/`failed` count, so a green
test count alone is not proof the gate passed.

**Everything runs through `uv run`.** Bare `pytest`, `ruff`, `python` use the wrong environment.
Use `timeout: 600000` on the Bash call.

## Strategy

1. Run the full gate once, filtered: `just test-all 2>&1 | grep -E "passed|failed|error|FAILED|All checks|^= " | tail -20`
2. Fix in the order it runs; iterate on the failing layer only (`uv run pytest tests/test_x.py`).
3. Stop when green. Don't re-run to "confirm".

## Notes

- A judge or scorer change must come with a test that pins the case that motivated it (the
  numeric parser has bitten twice: "3M" as three million, "December 31," as 31).
- A change to what a rung hands the model (`representations/`) is a protocol change — re-run
  `filing-ladder tokens` on the reference filing and say so in the PR.
- Never edit a gold in `questions/` to make a test pass. Gold comes from the document, read by
  a person.
- Never bump `version` in `pyproject.toml`.

$ARGUMENTS
