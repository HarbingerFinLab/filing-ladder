# Filing Ladder v0.1.1 — the document as a constant (Claude Sonnet 5)

**Disclosure.** Harbinger FinLab is the implementation-and-training practice for RoboSystems, the
platform under test; its founder built the graph rungs. Every transcript, judgment and token count
of this run is in this directory. The headline result below is worse for that platform's story than
v0.1's was, which is why it is the headline.

**Status: judge-scored.** Run 2026-09-06/07 under [`protocol-v0.1.1`](../../PROTOCOL.md) §10,
pre-registered and tagged before it started. Ten controls, 38 questions, k = 3, 1,140 records,
**$93.73 at list price**, zero transport errors. The v0.1 rows are unchanged and carried forward
by identity; nothing here re-scores them.

## What this run asked

v0.1 measured ten representations of one filing and found the document rungs at the top, a
"structured middle" at 37–48%, and the knowledge graph with shaped tools alone reaching the
document rungs' accuracy. After publication we found that comparison was not clean: rung 7a's
search index also held the **untagged body** of the 10-K (Items 1, 1A, 1C, 2, 7, 7A), which no
XBRL-derived form carries, because those sections are not tagged. So 7a had more of the filing
than the forms it beat.

v0.1.1 removes that difference. Every tool rung gets the **same document** — rung 2's plain text,
the whole primary document, tags stripped — behind the **same two tools**: `search_text` (a regular
expression, returning offsets and windows) and `read_text` (a span at an offset). Nothing else
changes: same questions, same model, same locks, same turn budget, same prompt skeleton. Plus three
controls that isolate the retrieval mechanism: the graph's index with the untagged body removed
(`7a-tagged`), the graph's fact tools with the constant document tool instead of its index
(`7a-facts+doc`), and the SEC's own EDGAR full-text search (`6+efts`).

## The result, in one paragraph

**Given the whole document behind a search tool, every representation performs about the same.**
On lookups the ten controls land between 85% and 92%, against the PDF's 90% and the plain text's
93% read whole — and at a tenth to a twentieth of the cost per correct answer. On derived questions
they land between 54% and 61%, the same band the document rungs occupied in v0.1. Meanwhile the
knowledge graph with the untagged body taken out of its index falls from 85% to **48%**, into the
structured middle exactly where every other tagged-only form sits. The tagged data was never the
thing that worked. The document was, and the form it arrived in barely mattered.

## Accuracy — T1 lookup (n = 60 records per control)

| Control | What the model had | Accuracy | Abstained | Confident-wrong | $/question | $/correct | The same rung in v0.1 |
|---|---|---|---|---|---|---|---|
| 2t | plain text, search tool only | 88% | 3% | 3% | $0.022 | $0.025 | 2 at 93% |
| 5a+doc | OIM as published + the document | 85% | 5% | 5% | $0.039 | $0.046 | 5a at 37% |
| 5c+doc | Tavi compiled model, jq + the document | 88% | 3% | 5% | $0.075 | $0.085 | 5c at 45% |
| 6+doc | SEC companyfacts + the document | 90% | 3% | 3% | $0.027 | $0.031 | 6 at 15% |
| 6+efts | SEC companyfacts + the SEC's full-text search | 22% | 42% | 10% | $0.087 | $0.400 | 6 at 15% |
| 7a-tagged | knowledge graph, shaped tools, tagged text only | 48% | 35% | 13% | $0.195 | $0.403 | 7a at 85% |
| 7a+doc | knowledge graph, shaped tools + the document | 88% | 5% | 2% | $0.038 | $0.044 | 7a at 85% |
| 7a-facts+doc | knowledge graph, fact tools only + the document | 90% | 3% | 3% | $0.046 | $0.051 | 7a at 85% |
| 7b+doc | property graph, raw Cypher + the document | 87% | 2% | 7% | $0.053 | $0.061 | 7b at 42% |
| 7c+doc | holon (RDF), SPARQL + the document | 92% | 2% | 3% | $0.066 | $0.072 | 7c at 42% |

## Accuracy — T2 derived (n = 54 records per control)

| Control | What the model had | Accuracy | Abstained | Confident-wrong | $/question | $/correct | The same rung in v0.1 |
|---|---|---|---|---|---|---|---|
| 2t | plain text, search tool only | 61% | 11% | 19% | $0.047 | $0.077 | 2 at 61% |
| 5a+doc | OIM as published + the document | 61% | 13% | 17% | $0.072 | $0.118 | 5a at 44% |
| 5c+doc | Tavi compiled model, jq + the document | 56% | 13% | 19% | $0.120 | $0.217 | 5c at 44% |
| 6+doc | SEC companyfacts + the document | 59% | 13% | 19% | $0.062 | $0.105 | 6 at 33% |
| 6+efts | SEC companyfacts + the SEC's full-text search | 41% | 30% | 19% | $0.085 | $0.210 | 6 at 33% |
| 7a-tagged | knowledge graph, shaped tools, tagged text only | 50% | 24% | 13% | $0.270 | $0.541 | 7a at 59% |
| 7a+doc | knowledge graph, shaped tools + the document | 54% | 11% | 15% | $0.081 | $0.150 | 7a at 59% |
| 7a-facts+doc | knowledge graph, fact tools only + the document | 57% | 17% | 19% | $0.081 | $0.140 | 7a at 59% |
| 7b+doc | property graph, raw Cypher + the document | 59% | 13% | 19% | $0.097 | $0.163 | 7b at 43% |
| 7c+doc | holon (RDF), SPARQL + the document | 56% | 13% | 20% | $0.101 | $0.182 | 7c at 48% |

## Every form, both versions, ranked — T1 lookup

| Form | Accuracy | Version |
|---|---|---|
| 2 — plain text, in context | 93% | v0.1 |
| 7c+doc — holon (RDF), SPARQL + the document | 92% | v0.1.1 |
| 1 — PDF, in context | 90% | v0.1 |
| 6+doc — SEC companyfacts + the document | 90% | v0.1.1 |
| 7a-facts+doc — knowledge graph, fact tools only + the document | 90% | v0.1.1 |
| 2t — plain text, search tool only | 88% | v0.1.1 |
| 5c+doc — Tavi compiled model, jq + the document | 88% | v0.1.1 |
| 7a+doc — knowledge graph, shaped tools + the document | 88% | v0.1.1 |
| 7b+doc — property graph, raw Cypher + the document | 87% | v0.1.1 |
| 3 — inline XBRL, in context | 85% | v0.1 |
| 7a — graph + document index, shaped tools | 85% | v0.1 |
| 5a+doc — OIM as published + the document | 85% | v0.1.1 |
| 7a-tagged — knowledge graph, shaped tools, tagged text only | 48% | v0.1.1 |
| 5c — Tavi compiled model, jq | 45% | v0.1 |
| 7b — property graph, raw Cypher | 42% | v0.1 |
| 7c — holon (RDF), SPARQL | 42% | v0.1 |
| 5a — OIM as published, file tools | 37% | v0.1 |
| 5b — OIM in context, text blocks removed | 37% | v0.1 |
| 6+efts — SEC companyfacts + the SEC's full-text search | 22% | v0.1.1 |
| 6 — SEC companyfacts, search | 15% | v0.1 |

## Every form, both versions, ranked — T2 derived

| Form | Accuracy | Version |
|---|---|---|
| 2 — plain text, in context | 61% | v0.1 |
| 2t — plain text, search tool only | 61% | v0.1.1 |
| 5a+doc — OIM as published + the document | 61% | v0.1.1 |
| 7a — graph + document index, shaped tools | 59% | v0.1 |
| 6+doc — SEC companyfacts + the document | 59% | v0.1.1 |
| 7b+doc — property graph, raw Cypher + the document | 59% | v0.1.1 |
| 7a-facts+doc — knowledge graph, fact tools only + the document | 57% | v0.1.1 |
| 1 — PDF, in context | 56% | v0.1 |
| 3 — inline XBRL, in context | 56% | v0.1 |
| 5c+doc — Tavi compiled model, jq + the document | 56% | v0.1.1 |
| 7c+doc — holon (RDF), SPARQL + the document | 56% | v0.1.1 |
| 7a+doc — knowledge graph, shaped tools + the document | 54% | v0.1.1 |
| 7a-tagged — knowledge graph, shaped tools, tagged text only | 50% | v0.1.1 |
| 5b — OIM in context, text blocks removed | 48% | v0.1 |
| 7c — holon (RDF), SPARQL | 48% | v0.1 |
| 5a — OIM as published, file tools | 44% | v0.1 |
| 5c — Tavi compiled model, jq | 44% | v0.1 |
| 7b — property graph, raw Cypher | 43% | v0.1 |
| 6+efts — SEC companyfacts + the SEC's full-text search | 41% | v0.1.1 |
| 6 — SEC companyfacts, search | 33% | v0.1 |

## The three retrieval controls

- **7a-tagged (the subtraction).** The product's index with every untagged section removed and no
  other change: **85% → 48%** on lookups, **59% → 50%** on derived questions, abstention up from 5%
  to 35%. That is the measurement of how much of v0.1's rung-7a result was the untagged body of the
  filing. It also cost the most of any control, $26.28, because the model searched harder and found
  less.
- **7a-facts+doc (the substitution).** The graph's fact tools with the constant document tool in
  place of its index: **90% / 57%** at $0.051 per correct lookup, against 7a-tagged's $0.403. Same
  graph, same facts, a different way to reach the text.
- **6+efts (the publisher's own search).** EDGAR full-text search returns which *files* contain a
  phrase and no text. Against plain rung 6 it moves lookups from 15% to **22%** while adding 22 turn
  caps, 41 tool errors and 12.5 tool calls a question. It says a phrase is in a filing; it never
  says what the filing says. Nine of its 268 calls failed with 500s from the SEC's servers.

## What the run did

| Control | Records | Turn caps | Mean turns | Mean tool calls | Tool errors | Cost |
|---|---|---|---|---|---|---|
| 2t | 114 | 0 | 3.6 | 3.7 | 0 | $3.83 |
| 5a+doc | 114 | 0 | 4.4 | 5.0 | 0 | $6.25 |
| 5c+doc | 114 | 1 | 4.5 | 4.8 | 2 | $10.99 |
| 6+doc | 114 | 0 | 4.2 | 4.6 | 6 | $5.01 |
| 6+efts | 114 | 22 | 6.5 | 12.5 | 41 | $9.81 |
| 7a-tagged | 114 | 8 | 5.3 | 7.0 | 2 | $26.28 |
| 7a+doc | 114 | 2 | 3.6 | 3.7 | 0 | $6.67 |
| 7a-facts+doc | 114 | 1 | 4.1 | 4.3 | 0 | $7.10 |
| 7b+doc | 114 | 1 | 4.2 | 4.3 | 0 | $8.40 |
| 7c+doc | 114 | 1 | 4.4 | 4.4 | 0 | $9.40 |

Turn caps score as misses with their cost, per the protocol. The 41 tool errors on 6+efts are
9 transient SEC server errors and 32 companyfacts concept misses; every other control ran clean.

## What this does and does not say

- **It does not say the graph is useless.** It says that on a **single filing**, with the whole
  document searchable, structure adds little to a lookup and nothing reliable to a derived
  question. Every claim about cross-filing and corpus-scale work (tiers 3 and 4) is untested here
  and remains untested.
- **It does say the published serializations lose their case on this tier.** OIM as published went
  from 37% to 85% when handed the untagged document. What was missing was never the tags.
- **Derived questions did not move.** Nothing in either version exceeds 61%, and confident-wrong
  answers run 15–20% across every control. Retrieval solved lookups. It did not solve analysis.
- **The cheapest correct answer in the benchmark** is plain text behind a search tool: $0.025 a
  lookup, against $1.21 for the PDF read whole in v0.1, uncached.

## Files

| File | What |
|---|---|
| `judgments.jsonl` | 1,140 judgments: the extracted answer, rubric points, contradiction check |
| `transcripts.jsonl.gz` | every record's full message trail, tool calls and usage (5.19 MB, SHA-256 `88fec9b178fda657bea5824115b9a5d75531b9f6fd596305dcbb2ce6c769a4f3`) |
| `run.json` | the run's parameters as recorded at start |
| `summary.md` / `summary.json` | per control × tier × stratum aggregates |
