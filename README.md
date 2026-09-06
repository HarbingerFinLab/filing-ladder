# Filing Ladder

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Test](https://github.com/HarbingerFinLab/filing-ladder/actions/workflows/test.yml/badge.svg)](https://github.com/HarbingerFinLab/filing-ladder/actions/workflows/test.yml)

**One filing, every representation: which shape of the same financial filing can a model actually use?**

A benchmark that hands the *same* SEC filing to the *same* model in every form the filing exists in —
rendered PDF, HTML text, inline XBRL, the XBRL package, OIM (xBRL-JSON / xBRL-CSV), the Tavi
compiled model (XBRL International's OIM Taxonomy Model, facts and taxonomy in one JSON document),
the SEC's `companyfacts` API, a property graph over MCP, and the filing as RDF — asks the *same*
questions, and
scores accuracy, abstention versus confident-wrong, provenance, repeatability, and **dollars per
correct answer at list price**. Representation is the only variable.

## Disclosure, first

Filing Ladder is published by **Harbinger FinLab**, the implementation-and-training practice for
[RoboSystems](https://robosystems.ai). Its founder built the RoboSystems SEC knowledge graph and the
MCP tools that rung 7a queries, the XBRL "holon" (RDF) proof of concept that rungs 7c and
7d use, and the converter (`xbrlkit`) that writes the Tavi compiled model rungs 5c and 5d use and
the property-graph file rung 7b queries — Tavi
is XBRL International's draft, but no published implementation writes it yet, so the author's does,
checked object by object against Arelle's unreleased plugin. Every other rung is public data in the
form its publisher ships it. The protocol, the
harness, the question sets, every transcript, and the raw usage are published so a reader can weigh
that interest and check the numbers. The fairness rules in [PROTOCOL.md](PROTOCOL.md) exist because
a benchmark with an interested author has to earn every claim — including the rule that **if the PDF
wins a tier, that is the headline for that tier**.

## Status

**Protocol v0.1, frozen 2026-09-06 (tag `protocol-v0.1`). First run published: judge-scored, human
review in progress.** The v0.1 run — Claude Sonnet 5, 38 questions, every v0 rung, k = 3, 1,140
records — is in [`results/v0.1-sonnet-5/`](results/v0.1-sonnet-5/README.md) with every transcript,
judgment and token count. Runs happen once; those numbers are final. The human review the protocol
requires (the disagreement log) is added there when it closes and annotates rather than re-scores.

## The ladder

| Rung | Representation | What the model gets | Shape |
|---|---|---|---|
| 1 | PDF | the filing rendered to pages, whole, in context | in context |
| 2 | HTML text | the EDGAR primary document with tags stripped | in context |
| 3 | iXBRL | the same document with styling and inline scaffolding stripped and the `ix:` tags and header kept | in context (1M-context models) |
| 4 | XBRL package | instance + schema + linkbases on disk, via file tools | tools |
| 5a / 5b | OIM | xBRL-JSON and xBRL-CSV as published (file tools) / with text-block facts removed (in context) | tools / in context |
| 5c / 5d | Tavi | the OIM Taxonomy Model (Tavi) compiled model — facts and taxonomy in one JSON document — describe + one jq tool / with text-block facts removed (in context) | tools / in context |
| 6 | `companyfacts` | the SEC's own structured API, three thin tools | tools |
| 7a | property graph, shaped tools | the RoboSystems `sec` graph via its MCP tools | tools |
| 7b | property graph, raw Cypher | the filing as a LadybugDB property graph (the `sec` graph's schema, text blocks inline), describe + one query tool | tools |
| 7c | RDF, raw SPARQL | the filing as `holon.jsonld` in an in-memory store, describe + one query tool | tools |
| 7d | RDF in context | the `holon.jsonld` as text | in context (once compacted) |

Questions are stratified so that each structural gap the serializations have — dimensional
contexts, period semantics, custom-concept identity, and where the taxonomy lives — gets its own
number. The full design, the metrics, and the fairness rules are in [PROTOCOL.md](PROTOCOL.md).

## The two claims under test

> *Financial statements as PDFs are sufficient for AI analysis; machine-readable structured data is no longer necessary.*

> *You slap this new stuff into AI and it knows what to do with it. You slap the old stuff into AI and... nothing.*

The first is being made to regulators now. The second is the standards body's own bet on its new
serializations. Neither half of either sentence has been measured. This is the measurement.

## Quick start

```bash
brew install uv just            # toolchain
just install                    # deps + .env from the template
# set SEC_GOV_USER_AGENT in .env — EDGAR refuses undeclared clients

# One filing into every representation (3M's FY2024 10-K):
just materialize 66740 0000066740-25-000006

# The token table — what fits in context, and where:
just tokens 0000066740-25-000006

# Validate the question sets and print their pre-registration hashes:
just questions

# Check the text layer the graph rungs' search index is built from, against
# each filing's own text-block facts (PROTOCOL principle 11):
just check-text
```

Materializing needs no model key. Running a rung needs the key for its provider — Anthropic
direct, OpenAI direct, NVIDIA Build, or OpenRouter; see `.env.example`.

## What gets published

The protocol (pre-registered), this harness (MIT), the question sets, per-question transcripts for
every rung, raw token usage and cost at list price, judge outputs, and human-review notes —
committed in this repository under [`results/`](results/README.md), one directory per run,
tagged so a result is cited by an immutable commit. The same files may be mirrored as a Hugging
Face dataset beside the
[`sec-xbrl-knowledge-graphs`](https://huggingface.co/datasets/robosystems/sec-xbrl-knowledge-graphs)
corpus dump, which is what makes the graph rungs reproducible offline.

## Attribution

- **Vals AI, Finance Agent Benchmark** ([arXiv:2508.00828](https://arxiv.org/abs/2508.00828)) — the 50
  public questions with gold answers and rubrics (CC BY 4.0) are one of the two question sets, and
  their rubric-decomposition judge design is reused. Their agentic harness (MIT) is the strongest form
  of the document-only baseline.
- **FinanceBench** (Patronus AI) — the question *shapes* are reused with attribution and
  re-instantiated on current filings; the original rows (CC BY-NC 4.0) are not.
- **XBRL International / XBRL US** — the OIM Taxonomy Model requirements and the "AI-readiness" goal
  this benchmark measures.

## Related

- [`robosystems`](https://github.com/RoboFinSystems/robosystems) — the platform whose `sec` graph is rung 7a, and whose graph projection rung 7b's file carries
- [`xbrlkit`](https://github.com/RoboFinSystems/xbrlkit) — builds the `holon.jsonld` for rungs 7c/7d, the Tavi compiled model for rungs 5c/5d, and the property-graph file for rung 7b
- [`robosystems-holon-viewer`](https://github.com/RoboFinSystems/robosystems-holon-viewer) — the parallel Cypher / SPARQL hand-offs rungs 7b/7c reuse
- [`vals-ai/finance-agent`](https://github.com/vals-ai/finance-agent) — the document-agent baseline

## Contributing

Gold corrections, replication results and harness fixes are all welcome — see
[CONTRIBUTING.md](.github/CONTRIBUTING.md). A gold correction needs the document evidence; a
replication needs the run's `summary.json`.

## License

MIT © 2026 Harbinger FinLab — see [LICENSE](LICENSE). Question sets carry their own licenses in `questions/`.
