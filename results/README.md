# results/

Local run outputs land here and are gitignored. A published run is committed under
`results/<protocol version>-<model>/` — the report, every judgment, every transcript (gzipped),
the run parameters and a README with the tables — and the commit is tagged, so a result is cited
by an immutable commit and never re-run in place. Runs happen once (PROTOCOL principle 6).

| Run | What |
|---|---|
| [`v0.1-sonnet-5/`](v0.1-sonnet-5/README.md) | protocol v0.1, Claude Sonnet 5, 38 questions, every v0 rung, k = 3 — 2026-09-05/06 |
| [`v0.1.1-sonnet-5/`](v0.1.1-sonnet-5/README.md) | protocol v0.1.1, the same model and questions, ten controls holding the document constant, k = 3 — 2026-09-06/07 |
| [`v0.2-sonnet-5-5/`](v0.2-sonnet-5-5/README.md) | protocol v0.2, Claude Sonnet 5.5 (a new column), the four forms that are ours re-materialized, `4c` added, the document through xbrlkit, rung 2 as the anchor, k = 3 — 2026-11-09 |
| [`v0.2.1-sonnet-5-5/`](v0.2.1-sonnet-5-5/README.md) | protocol v0.2.1, two rows added beside 4c and 7a, each its base with one friction removed, k = 3 — 2026-11-09 |

## Every row, every version, one table

<!-- results-table:start -->
### Every published row

Judge-scored, as each run's `summary.json` reports it, except where marked ‡: the §11 cross-filing rule applied (an answer read from a filing other than the question's is a confident-wrong of the form; `form-scoring.json` in that run). Ranked within each version by cost per correct lookup. T1 is 60 records a row, T2 is 54 (k = 3). Confident-wrong is every answer that is neither correct nor an abstention. Each run's README carries its errata: v0.1's 7a is read with PROTOCOL §9 (2026-09-06, what its index contained); v0.2's 4c and "+doc" rows with §9 (2026-11-09, the served tools' empty schemas). Neither changed a score.

| Version | Model | Row | Form | T1 acc | T1 conf-wrong | T1 $/correct | T2 acc | T2 conf-wrong | T2 $/correct | $/question |
|---|---|---|---|---|---|---|---|---|---|---|
| v0.1 | `claude-sonnet-5` | **7a** | property graph, shaped tools | 85% | 10% | $0.091 | 59% | 24% | $0.204 | $0.098 |
| v0.1 | `claude-sonnet-5` | **2** | HTML text | 93% | 7% | $0.139 | 61% | 28% | $0.267 | $0.145 |
| v0.1 | `claude-sonnet-5` | **7b** | property graph, raw Cypher | 42% | 23% | $0.316 | 43% | 30% | $0.401 | $0.150 |
| v0.1 | `claude-sonnet-5` | **5a** | OIM as published | 37% | 23% | $0.352 | 44% | 26% | $0.344 | $0.140 |
| v0.1 | `claude-sonnet-5` | **1** | PDF | 90% | 10% | $0.360 | 56% | 28% | $0.639 | $0.339 |
| v0.1 | `claude-sonnet-5` | **6** | companyfacts | 15% | 23% | $0.369 | 33% | 17% | $0.170 | $0.056 |
| v0.1 | `claude-sonnet-5` | **5c** | Tavi, raw jq | 45% | 18% | $0.398 | 44% | 28% | $0.469 | $0.193 |
| v0.1 | `claude-sonnet-5` | **3** | iXBRL | 85% | 10% | $0.447 | 56% | 22% | $0.722 | $0.390 |
| v0.1 | `claude-sonnet-5` | **7c** | RDF, raw SPARQL | 42% | 25% | $0.564 | 48% | 20% | $0.379 | $0.210 |
| v0.1 | `claude-sonnet-5` | **5b** | OIM, text blocks removed | 37% | 23% | $0.572 | 48% | 22% | $0.503 | $0.225 |
| v0.1.1 | `claude-sonnet-5` | **2t** | plain text, search tool | 88% | 8% | $0.025 | 61% | 28% | $0.077 | $0.034 |
| v0.1.1 | `claude-sonnet-5` | **6+doc** | companyfacts + the document | 90% | 7% | $0.031 | 59% | 28% | $0.105 | $0.044 |
| v0.1.1 | `claude-sonnet-5` | **7a+doc** | knowledge graph, shaped tools + the document | 88% | 7% | $0.044 | 54% | 35% | $0.150 | $0.059 |
| v0.1.1 | `claude-sonnet-5` | **5a+doc** | OIM as published + the document | 85% | 10% | $0.046 | 61% | 26% | $0.118 | $0.055 |
| v0.1.1 | `claude-sonnet-5` | **7a-facts+doc** | knowledge graph, fact tools only + the document | 90% | 8% | $0.051 | 57% | 28% | $0.140 | $0.062 |
| v0.1.1 | `claude-sonnet-5` | **7b+doc** | property graph, raw Cypher + the document | 87% | 12% | $0.061 | 59% | 28% | $0.163 | $0.074 |
| v0.1.1 | `claude-sonnet-5` | **7c+doc** | RDF, raw SPARQL + the document | 92% | 7% | $0.072 | 56% | 31% | $0.182 | $0.082 |
| v0.1.1 | `claude-sonnet-5` | **5c+doc** | Tavi, raw jq + the document | 88% | 8% | $0.085 | 56% | 33% | $0.217 | $0.096 |
| v0.1.1 | `claude-sonnet-5` | **6+efts** | companyfacts + the SEC's full-text search | 22% | 37% | $0.400 | 41% | 30% | $0.210 | $0.086 |
| v0.1.1 | `claude-sonnet-5` | **7a-tagged** | knowledge graph, shaped tools, tagged text only | 48% | 17% | $0.403 | 50% | 26% | $0.541 | $0.230 |
| v0.2 | `claude-sonnet-5-5` | **7b+doc** | property graph, raw Cypher + the document | 93% | 7% | $0.059 | 61% | 28% | $0.152 | $0.073 |
| v0.2 | `claude-sonnet-5-5` | **4c** | XBRL package, xbrlkit's shaped tools | 90% | 10% | $0.061 | 63% | 24% | $0.159 | $0.076 |
| v0.2 | `claude-sonnet-5-5` | **7a** | property graph, shaped tools | 90% | 10% | $0.062 | 61%‡ | 37%‡ | $0.172‡ | $0.079 |
| v0.2 | `claude-sonnet-5-5` | **7c+doc** | RDF, raw SPARQL + the document | 93% | 7% | $0.063 | 59% | 30% | $0.167 | $0.078 |
| v0.2 | `claude-sonnet-5-5` | **5c+doc** | Tavi, raw jq + the document | 90% | 10% | $0.082 | 61% | 28% | $0.188 | $0.093 |
| v0.2 | `claude-sonnet-5-5` | **2** | HTML text | 93% | 7% | $0.124 | 63% | 26% | $0.231 | $0.130 |
| v0.2 | `claude-sonnet-5-5` | **7c** | RDF, raw SPARQL | 53% | 12% | $0.263 | 50% | 26% | $0.250 | $0.133 |
| v0.2 | `claude-sonnet-5-5` | **7b** | property graph, raw Cypher | 45% | 20% | $0.278 | 50% | 22% | $0.217 | $0.117 |
| v0.2 | `claude-sonnet-5-5` | **5c** | Tavi, raw jq | 53% | 12% | $0.280 | 50% | 22% | $0.313 | $0.153 |
| v0.2.1 | `claude-sonnet-5-5` | **7a.1** | property graph, shaped tools, first step re-pointed | 88% | 10% | $0.054 | 61%‡ | 39%‡ | $0.158‡ | $0.071 |
| v0.2.1 | `claude-sonnet-5-5` | **4c.1** | XBRL package, xbrlkit's shaped tools, argument aliases | 92% | 8% | $0.076 | 63% | 24% | $0.157 | $0.084 |

### The rows that recur — the cost curve

The same row across versions. The model changed between v0.1.1 and v0.2 (rung 2, the plain text read whole, is the anchor that separates the model's move from the tools'); the "+doc" instrument changed from the harness's two text tools (v0.1.1) to xbrlkit's (v0.2); `.1` rows are their base with one friction removed (PROTOCOL §12).

| Row | Version | Model | T1 acc | T1 $/correct | T2 acc | T2 $/correct |
|---|---|---|---|---|---|---|
| **2** | v0.1 | `claude-sonnet-5` | 93% | $0.139 | 61% | $0.267 |
| **2** | v0.2 | `claude-sonnet-5-5` | 93% | $0.124 | 63% | $0.231 |
| **4c** | v0.2 | `claude-sonnet-5-5` | 90% | $0.061 | 63% | $0.159 |
| **4c.1** | v0.2.1 | `claude-sonnet-5-5` | 92% | $0.076 | 63% | $0.157 |
| **5c** | v0.1 | `claude-sonnet-5` | 45% | $0.398 | 44% | $0.469 |
| **5c** | v0.2 | `claude-sonnet-5-5` | 53% | $0.280 | 50% | $0.313 |
| **7a** | v0.1 | `claude-sonnet-5` | 85% | $0.091 | 59% | $0.204 |
| **7a** | v0.2 | `claude-sonnet-5-5` | 90% | $0.062 | 61%‡ | $0.172‡ |
| **7a.1** | v0.2.1 | `claude-sonnet-5-5` | 88% | $0.054 | 61%‡ | $0.158‡ |
| **7b** | v0.1 | `claude-sonnet-5` | 42% | $0.316 | 43% | $0.401 |
| **7b** | v0.2 | `claude-sonnet-5-5` | 45% | $0.278 | 50% | $0.217 |
| **7c** | v0.1 | `claude-sonnet-5` | 42% | $0.564 | 48% | $0.379 |
| **7c** | v0.2 | `claude-sonnet-5-5` | 53% | $0.263 | 50% | $0.250 |
| **5c+doc** | v0.1.1 | `claude-sonnet-5` | 88% | $0.085 | 56% | $0.217 |
| **5c+doc** | v0.2 | `claude-sonnet-5-5` | 90% | $0.082 | 61% | $0.188 |
| **7b+doc** | v0.1.1 | `claude-sonnet-5` | 87% | $0.061 | 59% | $0.163 |
| **7b+doc** | v0.2 | `claude-sonnet-5-5` | 93% | $0.059 | 61% | $0.152 |
| **7c+doc** | v0.1.1 | `claude-sonnet-5` | 92% | $0.072 | 56% | $0.182 |
| **7c+doc** | v0.2 | `claude-sonnet-5-5` | 93% | $0.063 | 59% | $0.167 |

*Generated by `bin/results_table.py` from 4 published runs; regenerate with `just results-table`.*
<!-- results-table:end -->

The same files may be mirrored as a Hugging Face dataset beside the
`sec-xbrl-knowledge-graphs` corpus dump; this directory is the record.
