---
description: Open a pull request for the current branch, writing the description from the work actually done.
argument-hint: '[target-branch] [review]'
---

Create a GitHub pull request for the current branch, writing the title and description from the actual work done in this session — not reconstructed from the diff.

## Why this command exists

A description written from the diff alone can't know _why_ a change was made. **You author it here, where the full context is available.**

This is `filing-ladder` — a **public benchmark**: one SEC filing handed to one model in every representation, the same questions, scored with cost. PR text is public the moment it is pushed, and a benchmark with an interested author is judged on its process, so the description must be exact about what changed for the model or the score.

**Everything runs through `uv run`** — the `just` recipes already do.

## Instructions

### 1. Preflight

```bash
CURRENT=$(git branch --show-current)
TARGET=${1:-main}
```

- **Never PR from `main`.** Branches come from `just create-feature <type> <name>`, not `git switch -c`.
- **Uncommitted changes**: surface them and ask whether to commit (never on `main`; stage by name, no `git add -A`; never `.env`, `data/`, `results/`).
- **Existing PR**: `gh pr list --head "$CURRENT" --base "$TARGET" --json url,number` — offer `gh pr edit` rather than duplicating.
- **Push**: `git push -u origin "$CURRENT"`.

### 2. Gather the real change context

- **Primary source: this session.** What changed and why.
- Corroborate with `git log --oneline "$TARGET".."$CURRENT"`, `git diff --stat`, and the full `git diff`.
- **No confabulation.** Every claim must be supported by the diff; when session context and the diff disagree, the diff wins.

### 3. Compose the PR

- **Title** — conventional-commit style with a scope (e.g. `fix(judge): treat a comma as a thousands separator only before three digits`).
- **Body** — **match the headings in `.github/PULL_REQUEST_TEMPLATE.md`** (`--body-file` bypasses template prefill):
  - **Summary** — 1–3 sentences. `Closes #123` as the last line if there is an issue.
  - **Changes** — grouped by layer: `representations/` · `providers/` + `loop.py` · `judge.py` + `score.py` · `questions/` · `PROTOCOL.md`.
  - **Protocol impact** — the judgment that matters: **PROTOCOL** (what is measured or how it is scored changed → after a freeze, a new version and a re-run) · **RUNG FIDELITY** (what a rung hands the model changed → name the rungs, re-measure the token table) · **QUESTIONS** (a question or gold changed → the filing and where in the document the value sits) · **HARNESS** (internal).
  - **Testing** — the gate is `just test-all`. Name the filings materialized or run against (accession numbers) and any run directory. "Not run" is a valid answer.
- **Never bump `version` in `pyproject.toml`** — protocol versions are tags cut by a maintainer.
- **Attribution** — attribute to the user only; no Claude footer or trailer unless explicitly asked.

### 4. Create the PR

```bash
gh pr create --base "$TARGET" --head "$CURRENT" --title "<title>" --body-file /tmp/pr-body.md
```

### 5. Optional Claude review

Only if the user asks (`review` / `--review`): `gh pr comment <number> --body "@claude please review this PR"`.

## Output

1. PR URL. 2. Title. 3. Target ← source. 4. The Protocol impact classification. 5. Whether a review was requested.

$ARGUMENTS
