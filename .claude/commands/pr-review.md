---
description: Review a pull request — gather metadata, diff, and existing feedback, then give a verdict.
argument-hint: '[pr-number-or-url]'
---

Review a pull request by gathering its metadata, diff and existing feedback, then give your own verdict.

## 1. Identify the PR

URL → repo + number; number → this repo; nothing → `gh pr view --json number,url` on the current branch, else ask.

## 2. Gather

```bash
gh pr view <NUMBER> --json number,url,title,body,author,state,isDraft,labels,comments,reviews,reviewDecision,statusCheckRollup,headRefName,baseRefName,additions,deletions,changedFiles,files,closingIssuesReferences
gh pr diff <NUMBER>
gh api repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/pulls/<NUMBER>/comments --paginate
```

Formal `reviews` are usually empty here; AI review findings arrive as a bot's conversation comment. In `statusCheckRollup`, `NEUTRAL`/`SKIPPED` is not a failure.

## 3. Review the diff — what matters in this repo

- **Protocol impact, honestly classified.** Does the diff change what a model sees (`representations/`, `prompts.py`, a tool set, the describe tool) or how an answer is scored (`judge.py`, `score.py`, tolerances)? If yes, the PR must say PROTOCOL or RUNG FIDELITY, and after a freeze that means a new version and a re-run — never a quiet patch to published numbers.
- **Fairness rules** (`PROTOCOL.md` §5). Does the change advantage one rung? The Cypher and SPARQL hand-offs must stay parallel in shape and size; the shakedown endpoint never produces a published rung; gold never comes from a graph.
- **Gold provenance.** Any change under `questions/` names the filing and where in the document the value sits, read by a person. A gold "fixed" to match a model's answer is the worst bug this repo can have.
- **Silent failures.** An empty query result answered as a fact, a tool error swallowed instead of returned to the model, a `cannot attempt` scored as a wrong answer instead of reported separately — flag each.
- **Cost lines.** Tokens by kind, turns, tool calls, tool errors and wall-clock must survive the change; the invoice is the exhibit.
- **Tests.** Read the test, don't trust that it's green — a test that asserts the buggy behavior passes just as happily. Parser changes need the case that motivated them.
- **Public-repo hygiene.** No keys, no `.env`, no `data/` or `results/` content; no internal infrastructure detail. Filing content is public and fine.
- **Reuse over reimplementation.** Filing acquisition and the holon come from `xbrlkit`; the OIM export is Arelle; nothing in the platform is built for the benchmark.
- Never a `version` bump in `pyproject.toml`.

## 4. Output

1. **Protocol impact** as you judge it (agree or disagree with the PR's own label, and why).
2. **Issues** that must be fixed before merge.
3. **Suggestions** that are not blocking.
4. **Questions.**
5. **Verdict**: approve / request changes / needs discussion.

Anchor findings to `file:line`. If the diff is clean, say so plainly.

$ARGUMENTS
