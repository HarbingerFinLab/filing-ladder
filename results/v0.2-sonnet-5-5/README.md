# Filing Ladder v0.2 — the model moves to Sonnet 5.5; the forms that are ours re-materialized; the document through xbrlkit (Claude Sonnet 5.5)

**Status: judge-scored; the pre-registered cross-filing rule applied to one row; human review open.**
The run happened once, on 2026-11-09, under tag `protocol-v0.2`, and will not be re-run. The human
review the protocol requires (§4: the disagreement log and a 20% random sample) is prepared in
[`review.md`](review.md); the reviewer's verdicts are added there when it closes. It annotates; it
does not change a score. The judge's own repeatability on that sample is reported at the end of
`review.md`.

This is the first row of the results table under a new model. PROTOCOL §8 says the model is the
column, so this run **opens the Sonnet 5.5 column** with the nine rows the funding covered — the
four forms that are ours (5c Tavi, 7a the `sec` graph's tools, 7b the filing's own property graph,
7c the holon), their three document-carrying controls, the new rung 4c, and rung 2 as the anchor —
and leaves the other thirteen rows open, pre-registered, to run when funded. Nothing carries forward
across a model change. The Sonnet 5 rows (v0.1, v0.1.1) stand beside every row below.

## The run

| | |
|---|---|
| Model | `claude-sonnet-5-5`, Anthropic direct, model-default sampling and thinking (the harness sends neither parameter; neither model returned a thinking block in any record), 1M window |
| Questions | the same 38 as v0.1, hashes unchanged: 32 from the Vals Finance Agent public set resolved to one filing each, 6 templates on the reference filing (3M FY2024 10-K) |
| Rows | 4c · 7a · 5c+doc · 7b+doc · 7c+doc · 5c · 7b · 7c · 2, in that order (the pre-registered cut order; no cut was needed) |
| Runs per row | k = 3 → 1,026 records |
| Turn budget | 12, as v0.1 |
| Judge | `claude-sonnet-5`, rubric decomposition + contradiction check; sees answer and gold only, never the row. Held across columns as a lock of the scoring |
| Started · finished | 2026-11-09T01:56:10Z · 2026-11-09T05:18Z |
| Versions | xbrlkit 0.21.4 (the library behind 4c, the document tools, and the 7b/7c artifacts) · LadybugDB 0.22.1 for 7b (the engine check in `lbug-double-reads.json`: 16,649 facts, 0 misreads) · Arelle 2.45.3 pinned, 5a/5b exports not regenerated · RoboSystems v1.22.2 for 7a, the hosted `sec` repository at `api.robosystems.ai`, reporting v1.22.2 at 01:56 and at 05:19 UTC |
| 7a's pace | 20 MCP calls a minute, 450 an hour, under the repository's plan caps; never engaged — 7a averaged 3.8 calls and 13 seconds a question |
| Cost | **$106.29 at list** for the run, against the pre-registered $118–130 (PROTOCOL §11); the two shakedowns $5.25 and $3.24; the judge is not metered by the harness |
| Errors | none: 1,026 of 1,026 records completed, no transport error, no 429, 15 turn caps (13 on 7b, 2 on 7a) |

T1 = lookup (20 questions, one fact from one filing). T2 = derived (18 questions: ratio, growth,
judgement). Per the protocol, tiers are never aggregated in a headline; the per-row totals in the
run table are shown for the cost curve only.

## What this run asked

Three things, pre-registered in PROTOCOL §11. **Does the model's move change the reading?** Rung 2
hands the whole plain text to the model with no tools, so its move from Sonnet 5 to Sonnet 5.5 is the
model's own gain on this document, and every tool row's move is read against it. **Do the forms that
are ours hold up under the tooling as it stands?** xbrlkit went from 0.4.1 to 0.21.4 since v0.1 (a
lossless holon, a single-file property graph, the serve tools), and 7a moved from a fresh local load
to the hosted repository. **Does the package match the platform?** Rung 4c is `xbrlkit serve` built
in-process over the filing's own XBRL package — the same shaped tools the `sec` server wraps, on the
reader's machine, no account, no network — placed beside 7a.

## The result, in one paragraph

**The model moved and the reading did not: rung 2 scored 93% on lookups and 63% on derived
questions, against 93% and 61% on Sonnet 5 — question for question identical on lookups.** Read
against that anchor, the four forms that are ours and the new 4c land where v0.1.1's
document-carrying controls landed: 90–93% on lookups and 59–63% on derived questions, inside one
another's error bars, at $0.06–0.08 per correct lookup — cheaper than the same rows cost on Sonnet 5.
The open-source package behind `xbrlkit serve` (4c) matches the hosted platform's tools (7a) on both
tiers at the same cost per correct lookup: the parent spec's sentence applies, *retrieval does the
work, not the platform*. The bare forms stay in the structured middle (45–53% on lookups, 50% on
derived), 7b lowest with 13 turn caps. The one row that looked like a model gain — 7a's derived
questions at 70% by the judge — was five records answered from a filing other than the question's,
which §11 pre-registered as confident-wrong of the form; scored as written, 7a lands at 61%, beside
the others.

## Accuracy — T1 lookup (n = 60 records per row)

| Row | Representation | Sonnet 5.5 (v0.2) | abstain | confident-wrong | Sonnet 5 (v0.1 / v0.1.1) | Δ |
|---|---|---|---|---|---|---|
| 4c | xbrlkit serve: the package behind shaped tools + the document | **90%** | 0% | 10% | — (new row) | — |
| 7a | `sec` graph, 13 shaped tools, hosted | **90%** | 0% | 10% | 85% | +5 pp |
| 5c+doc | Tavi + jq + the document | **90%** | 0% | 10% | 88% | +2 pp |
| 7b+doc | property graph, Cypher + the document | **93%** | 0% | 7% | 87% | +7 pp |
| 7c+doc | holon, SPARQL + the document | **93%** | 0% | 7% | 92% | +2 pp |
| 5c | Tavi + jq | **53%** | 35% | 12% | 45% | +8 pp |
| 7b | property graph (LadybugDB), Cypher | **45%** | 35% | 20% | 42% | +3 pp |
| 7c | holon (RDF), SPARQL | **53%** | 35% | 12% | 42% | +12 pp |
| 2 | plain text, whole, in context | **93%** | 0% | 7% | 93% | +0 pp |

## Accuracy — T2 derived (n = 54 records per row)

| Row | Representation | Sonnet 5.5 (v0.2) | abstain | confident-wrong | Sonnet 5 (v0.1 / v0.1.1) | Δ |
|---|---|---|---|---|---|---|
| 4c | xbrlkit serve: the package behind shaped tools + the document | **63%** | 13% | 24% | — (new row) | — |
| 7a | `sec` graph, 13 shaped tools, hosted | **61%** (judge 70%; five records form-scored, see below) | 2% | 37% | 59% | +2 pp |
| 5c+doc | Tavi + jq + the document | **61%** | 11% | 28% | 56% | +6 pp |
| 7b+doc | property graph, Cypher + the document | **61%** | 11% | 28% | 59% | +2 pp |
| 7c+doc | holon, SPARQL + the document | **59%** | 11% | 30% | 56% | +4 pp |
| 5c | Tavi + jq | **50%** | 28% | 22% | 44% | +6 pp |
| 7b | property graph (LadybugDB), Cypher | **50%** | 28% | 22% | 43% | +7 pp |
| 7c | holon (RDF), SPARQL | **50%** | 24% | 26% | 48% | +2 pp |
| 2 | plain text, whole, in context | **63%** | 11% | 26% | 61% | +2 pp |

## Cost per question and per correct answer, at list, with the cache reads the run had

| Row | T1 $/question | T1 $/correct | T2 $/question | T2 $/correct | Sonnet 5: T1 $/correct | Sonnet 5: T2 $/correct |
|---|---|---|---|---|---|---|
| 4c | $0.054 | **$0.061** | $0.100 | **$0.159** | — | — |
| 7a | $0.056 | **$0.062** | $0.105 | **$0.172** (judge-scored $0.150) | $0.091 | $0.204 |
| 5c+doc | $0.074 | **$0.082** | $0.115 | **$0.188** | $0.085 | $0.217 |
| 7b+doc | $0.055 | **$0.059** | $0.093 | **$0.152** | $0.061 | $0.163 |
| 7c+doc | $0.059 | **$0.063** | $0.099 | **$0.167** | $0.072 | $0.182 |
| 5c | $0.150 | **$0.280** | $0.156 | **$0.313** | $0.398 | $0.469 |
| 7b | $0.125 | **$0.278** | $0.108 | **$0.217** | $0.316 | $0.401 |
| 7c | $0.140 | **$0.263** | $0.125 | **$0.250** | $0.564 | $0.379 |
| 2 | $0.116 | **$0.124** | $0.145 | **$0.231** | $0.139 | $0.267 |

## Every row, both columns, ranked — T1 lookup

The Sonnet 5 column is v0.1 for the rungs and v0.1.1 for the controls. *open* marks a row of the Sonnet 5.5 column pre-registered but not run in this funding.

| Row | Representation | Sonnet 5.5 (v0.2) | $/correct | Sonnet 5 | $/correct |
|---|---|---|---|---|---|
| 2 | plain text, whole, in context | **93%** | $0.124 | 93% | $0.139 |
| 7b+doc | property graph, Cypher + the document | **93%** | $0.059 | 87% | $0.061 |
| 7c+doc | holon, SPARQL + the document | **93%** | $0.063 | 92% | $0.072 |
| 1 | PDF, whole, in context | *open* | — | 90% | $0.360 |
| 4c | xbrlkit serve: the package behind shaped tools + the document | **90%** | $0.061 | — | — |
| 5c+doc | Tavi + jq + the document | **90%** | $0.082 | 88% | $0.085 |
| 6+doc | companyfacts + the document | *open* | — | 90% | $0.031 |
| 7a | `sec` graph, 13 shaped tools, hosted | **90%** | $0.062 | 85% | $0.091 |
| 7a-facts+doc | `sec` graph fact tools + the document | *open* | — | 90% | $0.051 |
| 2t | plain text behind two search tools | *open* | — | 88% | $0.025 |
| 7a+doc | `sec` graph (v0.1 tools) + the document | *open* | — | 88% | $0.044 |
| 3 | inline XBRL, whole, in context | *open* | — | 85% | $0.447 |
| 5a+doc | OIM + the document | *open* | — | 85% | $0.046 |
| 5c | Tavi + jq | **53%** | $0.280 | 45% | $0.398 |
| 7c | holon (RDF), SPARQL | **53%** | $0.263 | 42% | $0.564 |
| 7a-tagged | `sec` graph, index restricted to tagged disclosures | *open* | — | 48% | $0.403 |
| 7b | property graph (LadybugDB), Cypher | **45%** | $0.278 | 42% | $0.316 |
| 5a | OIM JSON, in context | *open* | — | 37% | $0.352 |
| 5b | OIM, no text, in context | *open* | — | 37% | $0.572 |
| 6+efts | companyfacts + EDGAR full-text search | *open* | — | 22% | $0.400 |
| 6 | companyfacts, describe + query | *open* | — | 15% | $0.369 |

## Every row, both columns, ranked — T2 derived

The Sonnet 5 column is v0.1 for the rungs and v0.1.1 for the controls. *open* marks a row of the Sonnet 5.5 column pre-registered but not run in this funding.

| Row | Representation | Sonnet 5.5 (v0.2) | $/correct | Sonnet 5 | $/correct |
|---|---|---|---|---|---|
| 2 | plain text, whole, in context | **63%** | $0.231 | 61% | $0.267 |
| 4c | xbrlkit serve: the package behind shaped tools + the document | **63%** | $0.159 | — | — |
| 2t | plain text behind two search tools | *open* | — | 61% | $0.077 |
| 5a+doc | OIM + the document | *open* | — | 61% | $0.118 |
| 5c+doc | Tavi + jq + the document | **61%** | $0.188 | 56% | $0.217 |
| 7a | `sec` graph, 13 shaped tools, hosted | **61%** | $0.172 | 59% | $0.204 |
| 7b+doc | property graph, Cypher + the document | **61%** | $0.152 | 59% | $0.163 |
| 6+doc | companyfacts + the document | *open* | — | 59% | $0.105 |
| 7c+doc | holon, SPARQL + the document | **59%** | $0.167 | 56% | $0.182 |
| 7a-facts+doc | `sec` graph fact tools + the document | *open* | — | 57% | $0.140 |
| 1 | PDF, whole, in context | *open* | — | 56% | $0.639 |
| 3 | inline XBRL, whole, in context | *open* | — | 56% | $0.722 |
| 7a+doc | `sec` graph (v0.1 tools) + the document | *open* | — | 54% | $0.150 |
| 5c | Tavi + jq | **50%** | $0.313 | 44% | $0.469 |
| 7a-tagged | `sec` graph, index restricted to tagged disclosures | *open* | — | 50% | $0.541 |
| 7b | property graph (LadybugDB), Cypher | **50%** | $0.217 | 43% | $0.401 |
| 7c | holon (RDF), SPARQL | **50%** | $0.250 | 48% | $0.379 |
| 5b | OIM, no text, in context | *open* | — | 48% | $0.503 |
| 5a | OIM JSON, in context | *open* | — | 44% | $0.344 |
| 6+efts | companyfacts + EDGAR full-text search | *open* | — | 41% | $0.210 |
| 6 | companyfacts, describe + query | *open* | — | 33% | $0.170 |

## How much of the spread is real

The unit is the question, not the record: three runs of one question are not three independent
observations. Twenty lookup questions and eighteen derived ones give error bars wide enough to
swallow most of the table, and every paired change below is read with that in mind. **No row's move
from its Sonnet 5 value is distinguishable at 95%** — the largest is 7c on lookups, +11.7 ± 6.5
points (t = 1.79) — and the anchor's move is zero on lookups and +1.9 ± 1.9 points on derived
questions. What did change, uniformly, is how the model used the tools: fewer turns, fewer tool
errors, and a lower cost per correct answer on every tool row. 7a's derived row is shown
form-scored (the five cross-filing records as confident-wrong).

### T1 lookup: question-level mean ± standard error, and the paired change against the Sonnet 5 row

| Row | Sonnet 5.5, question-level | 95% interval | Δ vs Sonnet 5, paired by question | t |
|---|---|---|---|---|
| 4c | 90% ± 7pp | 77–100% | — (new row) | — |
| 7a | 90% ± 7pp | 77–100% | +5.0 ± 7.0pp | 0.72 |
| 5c+doc | 90% ± 7pp | 77–100% | +1.7 ± 4.5pp | 0.37 |
| 7b+doc | 93% ± 5pp | 83–100% | +6.7 ± 3.9pp | 1.71 |
| 7c+doc | 93% ± 5pp | 83–100% | +1.7 ± 2.9pp | 0.57 |
| 5c | 53% ± 11pp | 32–75% | +8.3 ± 5.3pp | 1.56 |
| 7b | 45% ± 11pp | 23–67% | +3.3 ± 5.9pp | 0.57 |
| 7c | 53% ± 11pp | 32–75% | +11.7 ± 6.5pp | 1.79 |
| 2 | 93% ± 5pp | 83–100% | +0.0 ± 0.0pp | identical |

### T2 derived: question-level mean ± standard error, and the paired change against the Sonnet 5 row

| Row | Sonnet 5.5, question-level | 95% interval | Δ vs Sonnet 5, paired by question | t |
|---|---|---|---|---|
| 4c | 63% ± 11pp | 41–85% | — (new row) | — |
| 7a | 61% ± 12pp | 38–84% | +1.9 ± 1.9pp | 1.00 |
| 5c+doc | 61% ± 12pp | 38–84% | +5.6 ± 4.0pp | 1.37 |
| 7b+doc | 61% ± 12pp | 38–84% | +1.9 ± 1.9pp | 1.00 |
| 7c+doc | 59% ± 11pp | 37–81% | +3.7 ± 2.5pp | 1.46 |
| 5c | 50% ± 12pp | 26–74% | +5.6 ± 4.0pp | 1.37 |
| 7b | 50% ± 12pp | 26–74% | +7.4 ± 5.8pp | 1.29 |
| 7c | 50% ± 12pp | 26–74% | +1.9 ± 1.9pp | 1.00 |
| 2 | 63% ± 11pp | 41–85% | +1.9 ± 1.9pp | 1.00 |

## The cross-filing rule, applied

PROTOCOL §11 says of 7a on the hosted repository: *the corpus is every processed filing, not 26 …
an answer read from a filing other than the question's is a confident-wrong of the form and is
scored as such.* Before publication every 7a tool result was scanned for an SEC accession number
other than the question's filing's. **Six of 114 records read another filing**, all on Airbnb's
FY2024 10-K: vals-17 (three runs) and vals-22 (three runs) each need the FY2022 gross booking value,
which that filing does not carry — rung 2 said so and abstained, and every file-based row scored 0
of 3 — and the model fetched it from the FY2023 or FY2022 10-K through `search-text`'s `fiscal_year`
argument or a corpus-wide `search-documents`. The judge, which sees answer and gold only, marked
five of the six correct. Those five are scored here as confident-wrong of the form: 7a's derived row
moves from 70% to **61%**, its confident-wrong rate from 28% to 37%, its cost per correct derived
answer from $0.150 to $0.172. `judgments.jsonl` and `summary.json` are the judge's output, unchanged;
the record list and the accessions read are in [`form-scoring.json`](form-scoring.json). Two things
follow. The rule had something to apply to for the first time, and the hosted corpus is exactly the
reach the single-filing tier must refuse. And the gold's own notes on both questions say the FY2024
10-K carries three years of the metric; it carries two — a gold-provenance finding for the review.

## What the model did against the tools

Recorded, not acted on (fairness rule 3): these are the model against the tools as shipped.

- **4c's argument names.** 37 of 4c's 44 tool errors are 33 calls to `fact_grid` with `concepts`
  where the library's argument is `elements`, and 4 calls to `resolve_element` with `phrase` where it
  is `query`; each was refused by the library's schema and corrected on the next turn. It cost 4c
  about one extra turn in three questions and is the whole of its cost gap to 7a on derived
  questions. *Corrected 2026-11-09:* the model had no argument schema to read on this row — the
  harness handed every served tool `{"type": "object"}` — so these are the nouns of the tool
  descriptions, guessed without a schema, not names guessed against one. See "What the served tools'
  schemas contained" below.
- **7b's regex loop.** 13 of 7b's 114 records hit the 12-turn cap and ended without an answer, all
  on narrative questions. 64 of its 95 tool errors are one Cypher pattern: `regexp_extract` over a
  text block with a group index the engine refuses, retried in variants until the turns ran out.
  Both shakedowns showed it on one question; v0.1's 7b on Sonnet 5 was the weakest form for the
  same reason. Raw Cypher over a filing's graph has no text tool, and the model keeps trying to
  build one.
- **7a reached for raw Cypher 13 times in 114 records and for `search-documents` twice**; the rest
  was the shaped tools and the two text tools, with no tool errors. Its two turn caps were derived
  questions.

## What the served tools' schemas contained (added 2026-11-09)

Found after publication, while a guard for v0.2.1 was tested against the real server; recorded as
PROTOCOL §9's erratum of the same date. §11 says the tools on 4c, and the `search_text` /
`read_text` instrument on 5c+doc, 7b+doc and 7c+doc, come from xbrlkit's own server — "the tools,
their descriptions, their argument schemas and their answers are the library's and not the
harness's". The descriptions and the answers were; the argument schemas were not. The harness read
each tool's schema off the server's listing under the wire name `inputSchema`, which the mcp 2.x
`Tool` object does not carry as an attribute, and fell back to `{"type": "object"}`. Every tool
served from xbrlkit therefore reached the model with no argument names, types, bounds or required
list; the model had the tool descriptions alone to go on. The 7a path reads the attribute by its
right name, and 7a's schemas were whole (0 validation errors in 429 calls).

| Row | Served-tool calls | Schema-validation refusals | Records with one (of 114) |
|---|---|---|---|
| 4c (all nine tools) | 419 | 44 | 38 |
| 5c+doc (`search_text` / `read_text`) | 259 | 1 | 1 |
| 7b+doc (same) | 255 | 2 | 2 |
| 7c+doc (same) | 267 | 3 | 3 |

Every one of 4c's 44 errors is of this kind: `fact_grid` 36 (33 of them `concepts` for `elements`),
`resolve_element` 5 (4 of them `phrase` for `query`), `search_text` 2, `read_text` 1 — the names the
model chose are the nouns of the tool descriptions, which is what a model does with a description
and no schema. The six on the +doc rows are a number where `pattern` wants a string, and a `window`
or `length` outside a bound the schema would have stated.

**What changes and what does not.** No score changes: the judge scores answers, and no §11 lock
names the schema. What changes is the reading of 4c's figures above: the 44 refusals and the extra
turn in each of 38 records are the harness's, not the model's and not the library's, so 4c's $0.076
per question and $0.061 / $0.159 per correct answer carry a handicap, and "4c matches 7a at the same
cost" was reached by a row the harness had hobbled. The direction of the error is against 4c. On the
three +doc rows the instrument was handed the same way; its footprint is 6 refusals in 781 calls,
and nothing in their figures turns on it. The capture is fixed in the harness the same day
(`filing_ladder/representations/xbrlkit_serve.py` reads the schema under its attribute name and
refuses a listing without one), tested against the real server, and v0.2.1's row 4c.1 (PROTOCOL
§12) is 4c with the schemas handed over, run beside this row rather than in its place.

## The column's open rows

Rungs 1, 3, 5a, 5b and 6, the v0.1.1 controls 2t, 5a+doc, 6+doc, 6+efts, 7a-tagged, 7a+doc and
7a-facts+doc, and the appendix ablation 7b-mcp are pre-registered rows of the Sonnet 5.5 column that
this funding did not run. They are marked *open* in the ranked tables above, with their Sonnet 5
values beside. Nothing carries forward across a model change; the SHA-256 of every artifact they
read is in [`artifact-hashes.json`](artifact-hashes.json), so a later run reads the same bytes.
Until rungs 1 and 3 run, the column has no in-context row above rung 2.

## What the run did

| Row | Records | Turn caps | Mean turns | Mean tool calls | Tool errors | Cost | Pre-registered estimate |
|---|---|---|---|---|---|---|---|
| 4c | 114 | 0 | 3.6 | 3.7 | 44 | $8.66 | $17–25 |
| 7a | 114 | 2 | 3.6 | 3.8 | 0 | $9.03 | $7–8 |
| 5c+doc | 114 | 0 | 3.8 | 3.8 | 2 | $10.65 | $9 |
| 7b+doc | 114 | 0 | 3.8 | 3.8 | 2 | $8.35 | $6 |
| 7c+doc | 114 | 0 | 3.9 | 3.8 | 3 | $8.87 | $4 |
| 5c | 114 | 0 | 4.6 | 4.1 | 18 | $17.41 | $20 |
| 7b | 114 | 13 | 5.2 | 5.4 | 95 | $13.35 | $12 |
| 7c | 114 | 0 | 4.4 | 3.9 | 12 | $15.16 | $8–9 |
| 2 | 114 | 0 | 1.0 | 0.0 | 0 | $14.81 | $17 |
| **Total** | 1026 | 15 | | | 176 | **$106.29** | $118–130 |

Turn caps score as misses with their cost, per the protocol. Actuals landed under the estimate on
4c (the shakedown's three retried calls did not scale), over on 7c+doc and 7c (the six template
questions understated the Vals questions on SPARQL), and on the estimate elsewhere; the midpoint cut
check passed with the five headline rows at $45.57 against $43–52.

## Expectations, scored

Stated in PROTOCOL §11 before the run (principle 2); a result that contradicts one is the finding.

- **(a) 7a's lookups move up toward the plain-text row.** Held: 85% → 90% (+5.0 ± 7.0 points),
  against plain text's 93%. Within the error bars.
- **(b) 4c lands near 7a, not near 5c.** Held on both tiers: 90% / 63% against 7a's 90% / 61%
  (5c: 53% / 50%). The parent spec's sentence is published as such: retrieval does the work, not
  the platform.
- **(c) 4c costs less per correct answer than 7a.** Held, narrowly: $0.061 against $0.062 on lookups,
  $0.159 against $0.172 on derived questions (form-scored; $0.150 judge-scored, where 4c would be the
  dearer). The gap is 4c's retried `fact_grid` calls, not the transport.
- **(d) 7b and 7c move little on lookups and more on narrative questions through their +doc
  controls.** Contradicted in part. The bare rows moved most — 7c +11.7 ± 6.5 on lookups, 7b +7.4 ±
  5.8 on derived — and the +doc rows least (7b+doc +6.7 ± 3.9 on lookups, otherwise ≤ +3.7). The
  re-materialization was a fidelity change; what moved the bare rows was the model finishing in
  fewer turns.
- **(e) 5c is unchanged within error bars.** Held: +8.3 ± 5.3 on lookups, +5.6 ± 4.0 on derived
  questions, neither distinguishable.
- **(f) Rung 2 moves by the model's gain alone, small on lookups.** Held, and more sharply than
  stated: zero on lookups (the same 20 questions right and wrong, run for run), +1.9 ± 1.9 on
  derived. Every tool row's move is therefore the model's use of the tools, not its reading; none of
  those moves is distinguishable at 95%.
- **(g) Cost per correct answer stays in the v0.1.1 band ($0.08–0.15), with 7a's native text reads
  dearer than the file-beside controls.** Contradicted in the good direction: on lookups four of the
  five rows sit **below** the band ($0.059–0.063; 5c+doc $0.082), and 7a at $0.062 is not dearer than
  the file-beside controls ($0.059–0.082). On derived questions the five sit at $0.152–0.188, 7a in
  the middle.

## What this does and does not say

- **It does not say Sonnet 5.5 reads filings better.** It says that on this document set, read
  whole, it reads them the same: rung 2 is the measurement, and it did not move.
- **It does say the model uses tools more economically.** Every tool row cost less per correct
  answer than it did on Sonnet 5, by a quarter to a half on the bare forms, with fewer turns and
  fewer errors — and none of that moved accuracy outside the error bars.
- **It does say the package matches the platform** on a single filing: 4c and 7a are the same
  functions over the same document, and they score the same at the same cost. The platform's case
  on this tier is not the tools; it is the corpus, which is precisely what this tier forbids.
- **It does say the hosted corpus is a hazard for a single-filing benchmark.** Five correct answers
  came from the wrong filing. The pre-registered rule caught them because the tool results name the
  filing they read; a graph that did not would have passed them.
- **Derived questions did not move.** Nothing in this column exceeds 63% on derived questions, and
  confident-wrong answers run 22–37% across every row. Retrieval solved lookups on Sonnet 5; a better
  model did not solve analysis.
- **The thirteen open rows are open.** The column's PDF and inline-XBRL rows, the in-context forms
  above rung 2, wait on funding; no claim about them is made here.

## Files

| File | What |
|---|---|
| `README.md` | this file |
| `review.md` | the human-review sheet: the four unanswered questions, the vals-17 case, the twelve mixed cells, the 205-record sample with the judge's repeatability on it |
| `judgments.jsonl` | 1,026 judgments: the extracted answer, rubric points, contradiction check — the judge's output, unchanged |
| `form-scoring.json` | the cross-filing rule applied to 7a: the six records, the accessions they read, the five re-scored |
| `transcripts.jsonl.gz` | every record's full message trail, tool calls and usage (5.87 MB, SHA-256 `d96670c8e4e24f310434b9b7da03b3af9808241dc7a362f3a604bd638d52b8de`) |
| `run.json` | the run's parameters as recorded at start, including the MCP pace |
| `summary.md` / `summary.json` | per row × tier × stratum aggregates, judge-scored |
| `text-layer-gate.json` | the document gate: xbrlkit's readable text against rung 2's plain text, 26 of 26 |
| `lbug-double-reads.json` | the 7b engine check: 16,649 consolidated numeric facts read through two filtered projections, 0 misreads |
| `artifact-hashes.json` | the SHA-256 of every artifact a row reads, per filing — the pin for the open rows |
