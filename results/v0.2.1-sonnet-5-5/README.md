# Filing Ladder v0.2.1 — two rows added beside 4c and 7a, each its base with one friction removed (Sonnet 5.5, 2026-11-09)

The protocol these rows ran under is [PROTOCOL §12](../../PROTOCOL.md#12-v021--two-rows-added-beside-4c-and-7a-each-with-one-friction-the-v02-transcripts-showed-removed-pre-registered-2026-11-09),
tagged `protocol-v0.2.1` before the run. The rows are *added* to the Sonnet 5.5 column under §8's
last-number rule: every v0.2 row carries forward by identity and nothing in
[`results/v0.2-sonnet-5-5/`](../v0.2-sonnet-5-5/README.md) changes. Each new row is read beside
its base, never in its place.

## The run

| | |
|---|---|
| Model under test | `claude-sonnet-5-5`, Anthropic direct, model defaults (no thinking, sampling or tool_choice parameter sent) |
| Judge | `claude-sonnet-5`, rubric decomposition + contradiction check — the v0.1 judge, unchanged |
| Rows | `4c.1` (4c with the server's argument schemas handed to the model, on xbrlkit 0.21.5) · `7a.1` (7a with workflow steps 1 and 2 pointed at its shaped tools) |
| Questions | the 38 of v0.1 (`questions/manifest.json`, hashes unchanged), k = 3, 12-turn budget, 16,384 max tokens |
| Records | 228 of 228; 225 `end_turn`, 3 `max_turns` (all on 7a.1); 0 transport errors, 0 `cannot_attempt`, 0 rate-limit refusals |
| Judgments | 228, 0 judge errors; `filing-ladder report` → `summary.json` / `summary.md` |
| Cost at list | **$17.61** (4c.1 $9.54 · 7a.1 $8.07) against §12's $15–18; about $2 of judging; the sub-dollar shakedown is below |
| Tokens | 7.09 M input, 0.25 M output, 9.16 M cache read, 17 K cache write |
| Wall | 18:05 → 18:46 UTC, 2026-11-09, sequential |
| Hosted side | `api.robosystems.ai` healthy on RoboSystems 1.22.2 at 18:05:11 UTC and 18:46:27 UTC (`status-start.json`, `status-end.json`); the pacer never engaged |
| xbrlkit | 0.21.5 (`run.json`), the release carrying the two argument aliases (xbrlkit PR #105) |

**The shakedown first** (`results/20261109-120218-shakedown-v0-2-1/`, local, never published, never
scored): the six 3M template questions on both rows at k = 1, 12 of 12 `end_turn`, 0 tool errors,
$0.37. 4c.1 produced no `concepts` or `phrase` refusal and 7a.1 made no `get-example-queries` call,
so the recorded run followed on Joey's go.

## What the two rows removed

*4c.1.* In v0.2 every tool served from xbrlkit reached the model with an empty argument schema —
the harness defect disclosed in PROTOCOL §9 (2026-11-09) and in the v0.2 README. 4c.1 hands the
model the server's own schemas, read from the listing under their attribute name and refused when
absent, and runs on xbrlkit 0.21.5, whose `fact_grid` and `resolve_element` also take `concepts`
and `phrase` beside `elements` and `query`. Same nine tools, same prompt word for word.

*7a.1.* 7a's workflow step 1 had told the model since 2026-09-02 to fetch the Cypher example queries
and the graph schema first; in v0.2, 46 of 114 records opened with a 6,718-character fetch that led
to Cypher in 9. 7a.1's step 1 names the shaped tool the question calls for and step 2 puts the
example queries behind the Cypher fallback. Same thirteen tools from the same hosted server at the
same pace.

## The result, in one paragraph

Both rows landed where their bases did on accuracy, every paired change inside one standard error.
7a.1 did what §12 said it would: no schema or example fetch in 114 records, 14% fewer tool calls,
and a lower cost per correct answer on both tiers ($0.054 and $0.158 against 7a's $0.062 and
$0.172). 4c.1 did half of it: the refusals fell from 44 to 4 and the two argument names the model
had guessed stopped costing anything, but the turns per record did not fall — the model spent the
turns it no longer lost on more reading — and the schemas now ride along as cached tokens on every
turn, so 4c.1 cost *more* per correct lookup than 4c ($0.076 against $0.061) and the same on derived
questions. Given both argument names, the model used `elements` 22 times and `concepts` 22 times.
7a.1 read Airbnb's other 10-Ks on the same two questions 7a had, and the §11 rule scored those six
answers as before. The §9 erratum's reading that the schema defect had worked *against* 4c's cost was
wrong: with the schemas, the open-source row got slightly more accurate and dearer, not cheaper.

## Accuracy, each row beside its v0.2 base

Form-scored: the §11 cross-filing rule applied to 7a and 7a.1 alike (the judge's figure beside it
where they differ). Abstention is "Cannot determine"; confident-wrong is everything else that is not
correct.

**T1 lookup** (n = 60 records per row, 20 questions × 3)

| Row | Accuracy | Abstained | Confident-wrong | $/question | $/correct |
|---|---|---|---|---|---|
| 4c (v0.2) | 90% | 0% | 10% | $0.054 | $0.061 |
| **4c.1** | **92%** | 0% | 8% | $0.070 | $0.076 |
| 7a (v0.2) | 90% | 0% | 10% | $0.056 | $0.062 |
| **7a.1** | **88%** | 2% | 10% | $0.048 | $0.054 |

**T2 derived** (n = 54 records per row, 18 questions × 3)

| Row | Accuracy | Abstained | Confident-wrong | $/question | $/correct |
|---|---|---|---|---|---|
| 4c (v0.2) | 63% | 13% | 24% | $0.100 | $0.159 |
| **4c.1** | **63%** | 13% | 24% | $0.099 | $0.157 |
| 7a (v0.2) | 61% (judge 70%) | 2% | 37% | $0.105 | $0.172 (judge $0.150) |
| **7a.1** | **61%** (judge 72%) | 0% | 39% | $0.097 | $0.158 (judge $0.134) |

Repeatability (the share of questions whose three runs agree): 4c.1 95% / 89%, 7a.1 95% / 100% on
T1 / T2 (`summary.md`).

## How much of the change is real

The paired per-question difference against the base, mean of k = 3 per question, with the standard
error of the paired difference.

| Row | Tier | Δ accuracy (pp) | SE | t | questions |
|---|---|---|---|---|---|
| 4c.1 vs 4c | T1 | +1.7 | 1.7 | 1.00 | 20 |
| 4c.1 vs 4c | T2 | +0.0 | 0.0 | 0.00 | 18 |
| 7a.1 vs 7a | T1 | −1.7 | 1.7 | −1.00 | 20 |
| 7a.1 vs 7a | T2 | +0.0 | 0.0 | 0.00 | 18 |

Nothing here is distinguishable from zero. On T2 both rows reproduced their base question for
question in aggregate; on T1 each moved by one record in sixty. These are the §12 expectation (d)
outcomes, and nothing in this file claims an accuracy gain.

## The cross-filing rule, applied

Every 7a.1 tool result was scanned for an SEC accession number other than the question's filing
(`form-scoring.json`). Eight records carried one. Two carried it only inside a search listing —
vals-16 run 2 (`search-documents` hits across the filer's 10-Qs; the record hit the turn cap with no
answer) and vals-34 run 2 (a list of the filer's 8-Ks in a `search-text` result; the record
abstained) — so neither is an answer read from another filing. The six that are: **vals-17 runs 1–3
and vals-22 runs 1–3**, the same two Airbnb questions the v0.2 scan found, whose FY2022 gross booking
value the FY2024 10-K does not carry. 7a.1 read it from the FY2023 10-K (`0001559720-24-000006`) in
five records and the FY2022 10-K (`0001559720-23-000003`) in one, and the judge marked all six
correct. The rule scores them as confident-wrong of the form: 7a.1's T2 goes from 39/54 = 72.2% by
the judge to 33/54 = 61.1%, cost per correct answer from $0.134 to $0.158. 7a had the same six
records with five judged correct (70.4% → 61.1%). Expectation (e) held exactly.

The gold-provenance defect behind it (the two questions' notes claim three years of these metrics
in the FY2024 10-K; it carries two) is recorded in the v0.2 review sheet, Part B′. The questions are
unchanged here by rule; a question change moves the first number and waits for v0.3.

## What the model did against the tools

Recorded, not acted on (fairness rule 3).

**4c.1 against 4c.** 422 calls against 419; 4 tool errors against 44; 3.64 turns a record against
3.63. The four errors are three `fact_grid` calls on vals-08 that named no concept at all (an axis
or a period alone — the library's own "elements is required") and one on vals-17 that passed
`concepts` as a string where the schema says a list. None is the name refusal v0.2 had. Of the 47
`fact_grid` calls that named concepts, 22 used `elements` and 22 used `concepts`; all 26
`resolve_element` calls used `query`. With the schema in front of it, the model still chose the
description's noun half the time, so the alias earned its place beside the schema fix. The model
called `describe_filing` first in 73 records against 68, `search_text` 171 times against 155,
`information_block` 22 against 18, `fact_grid` 47 against 60.

Why 4c.1 cost more, by tier:

| | 4c T1 | 4c.1 T1 | 4c T2 | 4c.1 T2 |
|---|---|---|---|---|
| Cost | $3.27 | $4.19 | $5.39 | $5.35 |
| Turns / record | 3.28 | 3.40 | 4.02 | 3.91 |
| Tool calls / record | 2.95 | 3.23 | 4.48 | 4.22 |
| `describe_filing` as the first call (of 60 / 54) | 29 | 34 | 39 | 39 |
| Tool-result characters re-sent on later turns, per record | 48,242 | 62,192 | 89,345 | 86,935 |
| Cache-read tokens / record (the tools + system prefix, every turn) | 8,320 | 18,697 | 10,136 | 21,487 |
| Uncached input tokens / record | 22,938 | 29,877 | 43,383 | 42,316 |

The whole difference is on lookups. The schemas added about 3,000 tokens to the cached prefix, read
on every turn at $0.10 per million — about $0.12 across the row. The rest is reading: on T1 the
model, no longer losing a turn to a refusal, opened with the 16,500-character `describe_filing`
more often and made more calls, and every result rides along as uncached input on each later turn
(+29% re-sent characters). On T2 the pattern reversed slightly and the cost was flat. Fewer
refusals did not mean fewer turns; it meant the turns were spent elsewhere.

**7a.1 against 7a.** 373 calls against 429 (3.27 a record against 3.76); 0 tool errors in both;
3.56 turns a record against 3.65; 3 turn caps against 2. No `get-example-queries` and no
`get-graph-schema` call in 114 records, against 46 and 10. `read-graph-cypher` 3 times against 13,
written without the examples. `search-text` 218 against 185, and the first call in 81 records
against 55; `read-text` 59 against 81; `financial-statement-analysis` 53 against 48;
`build-fact-grid` 10 against 1; `disclosures` 10 against 16; `information-block` 9 against 13;
`describe-filing` 7 against 4; `search-documents` 2 and 2. Pointed at its tools, the row read the
document more and the statements a little more, and left Cypher alone.

## Expectations, scored (PROTOCOL §12)

| | Pre-registered | Outcome |
|---|---|---|
| (a) | 4c.1's schema-validation refusals fall from 44 to fewer than 5; its `concepts`-for-`elements` and `phrase`-for-`query` calls from 37 to 0; the row reports how many calls named each argument | **Held.** 4 refusals, none a name refusal; `elements` 22 · `concepts` 22 · `query` 26 · `phrase` 0 |
| (b) | 4c.1's turns per record fall toward 3.24 and its cost per question falls below 4c's $0.076 | **Contradicted.** 3.64 turns against 3.63; $0.084 a question against $0.076 — the lookups dearer, the derived questions flat (table above) |
| (c) | 7a.1 fetches `get-example-queries` in fewer than 10 of 114 records and only ahead of Cypher; cost per question at or below 7a's $0.079 | **Held.** 0 fetches; $0.071 a question |
| (d) | Accuracy on both tiers for both rows inside one SE of the base; no gain claimed | **Held.** +1.7 ± 1.7, 0.0, −1.7 ± 1.7, 0.0 |
| (e) | 7a.1 reads Airbnb's other 10-K on vals-17 and vals-22 again and the rule scores it as it scored 7a | **Held.** Six records, six judged correct, six re-scored |
| (f) | Cost per correct answer falls on both rows at the same accuracy | **Held for 7a.1** ($0.062 → $0.054, $0.172 → $0.158); **contradicted for 4c.1 on T1** ($0.061 → $0.076; T2 $0.159 → $0.157) |

Two of six contradicted, both on 4c.1's cost, both in the same direction. The §9 erratum said the
v0.2 schema defect had worked against 4c; on cost, it had not.

## What this does and does not say

It says the hosted row's prompt was carrying a two-month-old instruction that cost it about 10% per
correct answer and nothing in accuracy, and that removing it worked as pre-registered. It says the
open-source row, handed the schemas it was owed, answered one more lookup in sixty and cost 25% more
per correct lookup doing it, because a model that is not spending turns on refusals spends them on
reading, and because a schema is tokens on every turn. It says the one place corpus access
answered what no single filing could is still the same two Airbnb questions, and the form still
scores it wrong by rule. It does not say either row is better or worse than its base on accuracy —
no paired change clears one standard error — and it does not change a v0.2 number. The cost-per-
correct curve across versions is the figure these rows exist to move; on 7a it moved down again,
and on 4c it did not.

## Files

| File | What |
|---|---|
| `transcripts.jsonl.gz` | the 228 records: messages, tool events, usage, cost — SHA-256 `b4877cb6dce4811892c7cf720fa49f404f4899c387121d7c03737827c450c948` (1,260,561 bytes) |
| `judgments.jsonl` | 228 judgments by `claude-sonnet-5`: correct, abstained, contradiction, points met and total, the judge's reasoning |
| `form-scoring.json` | the cross-filing scan on 7a.1 and the six re-scored records, with the T2 figures before and after |
| `summary.json`, `summary.md` | `filing-ladder report` over the judgments, judge-scored (the form-scored 7a.1 T2 is in this README and `form-scoring.json`) |
| `run.json` | the run's configuration: rows, model, k, turn budget, xbrlkit version, MCP endpoint and pace, question ids |
| `status-start.json`, `status-end.json` | `api.robosystems.ai/v1/status` at 18:05:11 and 18:46:27 UTC |

No human-review sample was pre-registered for these two rows; the v0.2 sheet
(`../v0.2-sonnet-5-5/review.md`) remains the open review of the column.
