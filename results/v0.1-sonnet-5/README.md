# Filing Ladder v0.1 — Claude Sonnet 5, 38 questions, every v0 rung, k = 3

**Disclosure.** Harbinger FinLab is the implementation-and-training practice for RoboSystems, the
platform under test; its founder built the graph rungs (7a–7d). Every transcript, judgment and
token count of this run is in this directory so a reader can weigh that interest and check the
numbers.

**Status: judge-scored; human review in progress.** The run happened once, on 2026-09-05/06, under
[`protocol-v0.1`](../../PROTOCOL.md) (tag `protocol-v0.1`). These numbers are final and will not
be re-run. The human review the protocol requires (§4: the disagreement log over the questions
every rung missed and the questions where the graph trailed the documents) is added to this
directory as `review.md` when it closes; it annotates, it does not change a score.

## How to read this if you do not evaluate language models

The model is not the subject here. It is a standardized reader with no rules and no judgment,
sent to read the same filing in ten forms and answer the same 38 analyst questions. What is
being measured is the forms.

- **A rung** is one form of the filing: the PDF, the plain text, the inline XBRL, the XBRL data
  exactly as published, the same data through a structured store, and so on. Same filing, same
  facts, different shape.
- **T1 lookup** is one reported number from one filing. **T2 derived** is a ratio, a trend or a
  judgment built from several. They are never averaged together.
- **Accuracy** is the share of answers that matched what a person reading the filing would say.
  **Abstained** is the reader saying it could not find it. **Confident-wrong** is the reader
  asserting an answer the filing contradicts, the outcome that matters most.
- **Cannot attempt** means the form is too large for the reader to take in at once. It is scored
  as a miss, because a form nobody can read is not a usable form.
- **Repeatability** is how often three readings of the same question agreed.
- **$/correct** is what one right answer costs at list price; *uncached* is a single cold question,
  *cached* is a batch of questions on one filing.

The reading for a standards or policy audience: the tagged data as published did not help the
reader, the same data behind a structured query layer matched reading the document at a sixth of
the cost, and reading the document itself is 90% right on lookups and 56% on analysis, with 28%
of the analysis answers confidently wrong.

## The run

| | |
|---|---|
| Model | `claude-sonnet-5`, Anthropic direct, model-default sampling, 1M window |
| Questions | 38: 32 from the Vals Finance Agent public set resolved to one filing each, 6 templates on the reference filing (3M FY2024 10-K) |
| Rungs | 1 · 2 · 3 · 5a · 5b · 5c · 6 · 7a · 7b · 7c |
| Runs per question | k = 3 → 1,140 records |
| Judge | `claude-sonnet-5`, rubric decomposition + contradiction check; sees answer and gold only, never the rung |
| Started | 2026-09-06T09:41:17Z |
| Versions | xbrlkit 0.4.1 · Arelle 2.44.6 · Chrome 152.0.7977.83 · RoboSystems v1.11.16 (local stack, fresh load of the 26 corpus filings) |
| Cost | **$221.90 at list price** against the pre-registered ≈ $165 (PROTOCOL §7.2); the tool rungs ran longer than priced |

T1 = lookup (20 questions, one fact from one filing). T2 = derived (18 questions: ratio, growth,
judgement). Per the protocol, tiers are never aggregated in a headline; the per-rung totals in the
cost table below are shown for the cost curve only.

## Accuracy — T1 lookup (n = 60 records per rung)

| Rung | Representation | Accuracy | Abstained | Confident-wrong | Cannot attempt | Repeatability | $/question | $/correct |
|---|---|---|---|---|---|---|---|---|
| 1 | PDF, in context | 90% | 2% | 10% | 0% | 95% | $0.324 | $0.360 |
| 2 | plain text, in context | 93% | 2% | 7% | 0% | 90% | $0.130 | $0.139 |
| 3 | inline XBRL, in context | 85% | 2% | 10% | 5% | 95% | $0.380 | $0.447 |
| 5a | OIM as published, file tools | 37% | 40% | 23% | 0% | 90% | $0.129 | $0.352 |
| 5b | OIM in context, text blocks removed | 37% | 40% | 23% | 0% | 80% | $0.210 | $0.572 |
| 5c | Tavi compiled model, jq | 45% | 37% | 18% | 0% | 85% | $0.179 | $0.398 |
| 6 | SEC companyfacts, search | 15% | 62% | 23% | 0% | 95% | $0.055 | $0.369 |
| 7a | property graph, shaped tools (MCP) | 85% | 5% | 10% | 0% | 90% | $0.077 | $0.091 |
| 7b | property graph, raw Cypher | 42% | 35% | 23% | 0% | 75% | $0.132 | $0.316 |
| 7c | holon (RDF), SPARQL | 42% | 33% | 25% | 0% | 80% | $0.235 | $0.564 |

## Accuracy — T2 derived (n = 54 records per rung)

| Rung | Representation | Accuracy | Abstained | Confident-wrong | Cannot attempt | Repeatability | $/question | $/correct |
|---|---|---|---|---|---|---|---|---|
| 1 | PDF, in context | 56% | 11% | 28% | 6% | 100% | $0.355 | $0.639 |
| 2 | plain text, in context | 61% | 13% | 28% | 0% | 94% | $0.163 | $0.267 |
| 3 | inline XBRL, in context | 56% | 11% | 22% | 11% | 100% | $0.401 | $0.722 |
| 5a | OIM as published, file tools | 44% | 30% | 26% | 0% | 83% | $0.153 | $0.344 |
| 5b | OIM in context, text blocks removed | 48% | 30% | 22% | 0% | 89% | $0.242 | $0.503 |
| 5c | Tavi compiled model, jq | 44% | 28% | 28% | 0% | 89% | $0.209 | $0.469 |
| 6 | SEC companyfacts, search | 33% | 50% | 17% | 0% | 100% | $0.057 | $0.170 |
| 7a | property graph, shaped tools (MCP) | 59% | 19% | 24% | 0% | 89% | $0.121 | $0.204 |
| 7b | property graph, raw Cypher | 43% | 28% | 30% | 0% | 94% | $0.171 | $0.401 |
| 7c | holon (RDF), SPARQL | 48% | 33% | 20% | 0% | 83% | $0.183 | $0.379 |

## Cost per question and per correct answer, cached and uncached

*Cached* is the run as billed: k = 3 and per-filing ordering write each document to the prompt
cache once and read it for the remaining runs (Sonnet 5 list: $2 / $10 per million input / output,
cache write $2.50, cache read $0.20). *Uncached* re-prices every prompt token at the input price —
what one cold question costs. Dollars are model tokens at list price and exclude the platform that
serves rung 7a, the same way the document rungs exclude the reader.

| Rung | Representation | Accuracy (all) | $/q cached | $/q uncached | $/correct cached | $/correct uncached |
|---|---|---|---|---|---|---|
| 1 | PDF, in context | 74% | $0.339 | $0.888 | $0.459 | $1.205 |
| 2 | plain text, in context | 78% | $0.145 | $0.380 | $0.186 | $0.486 |
| 3 | inline XBRL, in context | 71% | $0.390 | $1.127 | $0.549 | $1.586 |
| 5a | OIM as published, file tools | 40% | $0.140 | $0.140 | $0.348 | $0.348 |
| 5b | OIM in context, text blocks removed | 42% | $0.225 | $0.592 | $0.535 | $1.406 |
| 5c | Tavi compiled model, jq | 45% | $0.193 | $0.204 | $0.431 | $0.456 |
| 6 | SEC companyfacts, search | 24% | $0.056 | $0.068 | $0.236 | $0.287 |
| 7a | property graph, shaped tools (MCP) | 73% | $0.098 | $0.148 | $0.135 | $0.204 |
| 7b | property graph, raw Cypher | 42% | $0.150 | $0.161 | $0.357 | $0.383 |
| 7c | holon (RDF), SPARQL | 45% | $0.210 | $0.221 | $0.470 | $0.493 |

## What the run did

| Rung | Records | Completed | Cannot attempt | Turn cap (12) | Cost | Wall |
|---|---|---|---|---|---|---|
| 1 | 114 | 111 | 3 | 0 | $38.59 | 44 min |
| 2 | 114 | 114 | 0 | 0 | $16.58 | 24 min |
| 3 | 114 | 105 | 9 | 0 | $44.46 | 27 min |
| 5a | 114 | 101 | 0 | 13 | $16.00 | 51 min |
| 5b | 114 | 114 | 0 | 0 | $25.66 | 28 min |
| 5c | 114 | 106 | 0 | 8 | $22.00 | 58 min |
| 6 | 114 | 104 | 0 | 10 | $6.37 | 39 min |
| 7a | 114 | 114 | 0 | 0 | $11.17 | 35 min |
| 7b | 114 | 100 | 0 | 14 | $17.12 | 49 min |
| 7c | 114 | 105 | 0 | 9 | $23.96 | 70 min |

Every cannot-attempt is pre-registered in PROTOCOL §7: rung 1 on Dutch Bros (a 28 MB PDF over the
API's request cap) and rung 3 on U.S. Steel, Allstate and KKR (inline XBRL over the 1M window). A
turn cap is scored as a miss with its cost. One record (rung 1, Spirit Airlines, run 3) ended in
a transient API error ("Could not process PDF") and was re-run with `--resume --retry-errors`;
its retry is the record here.

## Files

| File | What |
|---|---|
| `summary.md` / `summary.json` | the report: every metric by rung × tier and by rung × tier × stratum |
| `judgments.jsonl` | one judgment per record: rubric points met, contradiction, abstention, provenance, judge usage |
| `transcripts.jsonl.gz` | one record per run: every message, tool call and result, usage, cost (117 MB uncompressed; SHA-256 `dacadd761ed503256933cb927cbfe93cfa9a3f5a9d0eb03ed9ec4dc4e5ca6bb3`) |
| `run.json` | the run parameters as recorded by the harness |

Regenerate the report from the judgments: `gunzip -k transcripts.jsonl.gz && filing-ladder report --run .`
