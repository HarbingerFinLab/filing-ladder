# Contributing to Filing Ladder

Three kinds of contribution matter here, in this order.

## 1. Gold corrections

A wrong gold answer is the worst bug this repository can have. If you believe a question's gold
is wrong, open a **Gold correction** issue with the question id, the filing (accession number),
where in the document the value sits (statement, note, page), and the value you read. Gold is
read from the document by a person — never from a graph, an API, or a model — and a correction
is accepted on document evidence only. Corrections after a protocol freeze are recorded in the
next protocol version, not applied to published numbers.

## 2. Replications

Run any rung on any model and send the result: open a **Replication** issue with the model,
the provider route, the rungs, `k`, the protocol version (tag), and the run's `summary.json`
and `run.json`. Deviations from the protocol are welcome as long as they are named — a
different rendering, a different context window, a different judge. Replications that
disagree with the published numbers are the most useful ones.

## 3. Harness fixes

Bugs in materialization, providers, the loop, the judge, or scoring. See the PR template's
*Protocol impact* section: a fix that changes what a model sees or how an answer is scored is a
protocol change, and after a freeze it means a new version and a re-run.

## Development setup

```bash
brew install uv just
just install          # deps, .env from the template, git hooks
just test-all         # pytest -> ruff -> basedpyright
```

Everything runs through `uv run`. Tests never touch the network; anything that needs EDGAR or
a model key is marked `network` and skipped by default. Filings materialize into `data/`
(gitignored); runs land in `results/` (gitignored). The published results live on Hugging Face.

## Branches, commits, PRs

GitHub flow: a branch from `main`, small commits, a PR back to `main`. Create branches with
`just create-feature <type> <name>` (types: feature, bugfix, chore, refactor). Conventional
commit subjects: `feat(judge): …`, `fix(oim): …`, `docs(protocol): …`, `chore(ci): …`. Never
bump the version in `pyproject.toml` in a PR; the protocol version is a tag cut by a maintainer.

## Security

Do not open a public issue for a leaked key or a vulnerability. Email security@harbinger.finance.
Never commit `.env`; the template is `.env.example`.
