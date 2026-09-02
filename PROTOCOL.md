# Filing Ladder — protocol

**Status: DRAFT v0.1, not yet frozen.** The protocol freezes as a tagged release whose
`filing-ladder questions` manifest (question-set hashes) matches this document, *before* the
first scored run. Runs happen once. What comes out is published, tier by tier, whichever rung
wins.

**Disclosure.** Harbinger FinLab, the implementation-and-training practice for RoboSystems,
authors this benchmark. Its founder built the RoboSystems SEC knowledge graph and MCP tools
(rungs 7a, 7b) and the XBRL holon RDF proof of concept (rungs 7c, 7d). Every fairness rule below
exists because of that interest.

## 1. The claims under test

> *Financial statements as PDFs are sufficient for AI analysis; machine-readable structured data
> (XBRL) is no longer necessary.*

This position is being made to regulators now — in the debate over GASB's draft XBRL taxonomy for
state and local government reports and in the Financial Data Transparency Act rulemaking. And from
the standards body's side, on its new serializations (OIM Taxonomy Model requirements webinar,
January 2026):

> *"You slap this new stuff into AI and it knows what to do with it. You slap the old stuff into
> AI and... nothing."*

Neither half of either sentence has been measured. The counter-claims, made falsifiable:

1. On single-document lookups a frontier model reading a PDF is *good enough to be dangerous*:
   plausible numbers, weak provenance, wrong at a rate an analyst would not accept.
2. When a question spans periods, entities or a corpus, the PDF path fails on cost and
   reliability together, not only on accuracy.
3. Raw XBRL does not rescue it. The package is siloed (instance + five taxonomy files, per filing,
   per taxonomy vintage), does not fit in context (2.4M tokens for one 10-K), and does not compose
   across filers.
4. OIM's JSON does not rescue it either. xBRL-JSON modernizes the half of a filing that is readable
   without the taxonomy and leaves the half that gives facts their meaning — labels, presentation,
   calculation — in XML, or absent.
5. Cost per *correct* answer is structural, not a model-generation artifact.
6. Tagging is an issuer's assertion paid for once; extraction from a PDF is a stranger's guess paid
   for by every reader, non-deterministically. Run it twice, get two answers, no audit trail.

## 2. Design — one filing, every representation

The unit is a single SEC filing handed to a single model in each form the filing exists in, asked
the same questions under the same budget. Representation is the only variable.

| Rung | Representation | What the model gets | Shape |
|---|---|---|---|
| 1 | PDF | the primary document rendered to pages by headless Chrome (US Letter, default scale, no header/footer) as a document block with citations, whole | in context |
| 2 | HTML text | the EDGAR primary document with every tag stripped, entities unescaped, whitespace collapsed | in context |
| 3 | iXBRL | the primary document with `<style>`, `<script>` and style/class/id attributes removed; every `ix:` tag and the `ix:header` (contexts, units) kept | in context, 1M-context models |
| 4 | XBRL package | instance + schema + presentation/calculation/definition/label linkbases on disk; tools: list, read line range, grep | tools |
| 5a | OIM as published | xBRL-JSON and xBRL-CSV as Arelle's `saveLoadableOIM` writes them; the same file tools | tools |
| 5b | OIM in context | the same export with text-block facts removed (a fact is a text block when its concept is a `TextBlock`, its value is markup, or its value is ≥300 characters); xBRL-CSV facts + metadata by default | in context |
| 6 | `companyfacts` | the SEC's `data.sec.gov` API through three tools: search concepts, one concept's facts, one frame across filers | tools |
| 7a | property graph, shaped tools | the RoboSystems `sec` graph over MCP: financial statements, fact grids, element resolution, document search and sections, read-only Cypher | tools |
| 7b | property graph, raw Cypher | the same graph: schema + example queries + read-only Cypher only | tools |
| 7c | RDF, raw SPARQL | the filing as `holon.jsonld` in an in-memory rdflib store: describe (prefixes, node shapes computed from the graph, concepts and periods present, example queries) + read-only SPARQL | tools |
| 7d | RDF in context | the `holon.jsonld` as text | in context, once compacted |

**Where the taxonomy lives** is the axis the strata below test:

| Rung | Facts | Taxonomy (labels · presentation · calculation) |
|---|---|---|
| 4 | XML instance | XML linkbases, separate files — arcs to locators to hrefs |
| 5 | JSON / CSV | absent — xBRL-JSON references the DTS by URL and carries none of it |
| 7c | JSON-LD | JSON-LD, same graph, same query language |
| 7a / 7b | property graph | property graph, same graph |

**Five comparisons inside the ladder**, each isolating one thing: 7a vs 1 (the whole stack against
the PDF); 5b vs 7 (the layer above JSON); 7a vs 7b (the tool layer — the query craft done once on
the server); 7b vs 7c (the graph model, LPG vs RDF, same facts, same consolidated flag, same
period semantics — the only variable is the query language and how reliably a model writes it);
4 / 5 vs 7c on structure questions (taxonomy serialization).

**Same model, same effort, same prompt skeleton, same output contract, same turn budget on every
rung.** The output contract is a final block — `ANSWER` with units, `PROVENANCE`, `CONFIDENCE`
(high | medium | low | abstain) — so abstention and provenance are scored from the answer, not
inferred. A rung that cannot attempt a question (rung 4 in context; rung 3 on a 200K-context model;
rungs 1–3 on a corpus screen) scores it as a miss **and logs the cost of finding that out**.

**v0 runs rungs 1 · 2 · 3 · 5b · 6 · 7a · 7b · 7c**, k = 3 runs per question. Rungs 4, 5a and 7d,
and the two agent variants (D: the Vals document agent with search over rungs 1–3; E: rung 6 with
search) are v1.

## 3. Tiers and strata

| Tier | Shape | Ground truth |
|---|---|---|
| T1 lookup | one filing, one fact | the reported value, read from the document by a person |
| T2 derived | one filing or one entity's history; ratio, growth, judgement | Vals gold + rubrics; template judgement gold authored by a CPA, marked so |
| T3 cross-entity (v1) | a named peer set, one period | computed from `companyfacts` or a hand read of each document — never from a graph |
| T4 corpus screen (v1) | the corpus is the search space | computed from EDGAR's own APIs, independently of the graph |
| T5 provenance | scored on every tier | the evidence page or the fact identity |

T1 and T2 are the ladder; T3 and T4 are the scale axis. Every T1/T2 question is stratified five
ways; on the reference filing each stratum is a count:

| Stratum | Question shape | 3M FY2024 10-K |
|---|---|---|
| lookup | one reported value, unambiguous | — |
| dimension | the consolidated total, where nearly every context is a segment/member breakdown | 945 contexts, 917 dimensional, 28 consolidated |
| period | Q4 standalone from YTD; a non-calendar fiscal year; TTM — the serialization carries dates only | two facts share the 2024-12-31 end date (annual 24,575M; quarterly 6,010M); only duration distinguishes them |
| identity | a value tagged on a custom extension concept | 403 of 2,915 numeric tags on 159 custom `mmm:` concepts |
| structure | what sums to a subtotal; which statement a fact sits on; the label of a custom concept | 4,714 associations across 155 networks |

"Doesn't fit" erodes with every context-window release. The strata do not: rung 5b fits
everywhere, and the model still has to pick 28 consolidated contexts out of 945 and infer the
fiscal period from bare dates.

## 4. Metrics — per rung × tier × stratum, never aggregated across tiers

- **Accuracy.** Numeric: unit- and scale-normalized, ±1%, scored mechanically. Text and judgement:
  rubric decomposition — the gold is split into its points and a judge checks each point
  separately, never holistically; rubrics are human-reviewed before the run; the judge sees
  question, gold and answer only, never the rung, at temperature 0. Every judge disagreement and a
  20% random sample are human-reviewed; transcripts are published. The Vals set is also reported by
  its nine task categories.
- **Abstention vs confident-wrong.** A confident answer that contradicts the gold is the
  confident-wrong case; on text answers the judge runs a dedicated contradiction check.
- **Cannot attempt.** A miss, reported separately, with its cost.
- **Provenance.** A locatable citation (page / statement line / concept + period) that is correct.
  A cited document, page or element that does not exist is a **hallucinated source**.
- **Repeatability.** k = 3 runs per question per rung; the share of questions whose runs agree.
- **Empty-result-answered** (7b, 7c). An answer produced after a query returned nothing.
- **Cost.** Per question per rung: input, cached and output tokens, dollars **at list price** (pay
  batch, report list, disclose), wall-clock, turns, tool calls, tool errors. Rung 1 is reported
  cached and uncached. **Dollars per correct answer** is the headline.
- **Data-quality disagreements.** Where the PDF and the XBRL of the same filing disagree, logged as
  its own category, never scored against either rung.

## 5. Fairness rules

1. **Independent questions first, recent filings, the product corpus.** Set (i): Vals AI's 50
   public Finance Agent questions (CC BY 4.0) — expert-authored, written for document agents, so
   stacked toward the PDF rungs; the filing each needs is resolved for the model on every rung.
   Set (ii): FinanceBench-shaped templates re-instantiated on current filings across the five
   strata; numeric gold read from the document by a person, never from a graph.
2. **Pre-register.** This document and the question-set hashes are published before the run.
3. **Strongest baseline, not a strawman.** 1M context on rung 1; rung 4 gets file tools because
   in-context is impossible; rung 5b gets the text-block split the graph already has; the v1
   document agent is the Vals harness itself.
4. **Same model everywhere**, not tuned by us; a second frontier family in v1 so the result is not
   one vendor's model preferring one vendor's tools.
5. **Ground-truth provenance disclosed per tier**; the disagreement log published.
6. **Publish everything**: harness (MIT), question sets, per-question transcripts for every rung,
   raw usage, judge outputs, human-review notes, as a dataset beside the corpus dump.
7. **If the PDF rung wins a tier, that is the headline for that tier.**
8. **Gold never comes from the graph.**
9. **7b and 7c get the same hand-off**: a describe tool, example queries, one query tool, the same
   workflow prompt. 7c uses raw SPARQL only, never a fact-grid convenience.
10. **The shakedown endpoint never produces a published rung.** A free tier is used to prove the
    harness and read the per-rung token ratio, nothing more.

## 6. Harness

Python; the harness runs its own tool loop so every rung runs on any model with function calling.
Providers: Anthropic direct for the frontier run (document blocks with citations, prompt caching,
batch for paying); an OpenAI-compatible route for the shakedown (no PDF input, no caching) and for
the second family (provider pinned). Tool errors are returned to the model for correction; rate
limits and overloads get exponential backoff with jitter.

Filing acquisition, rung materialization and the graph rungs reuse published code: the
`robosystems-xbrl-holon` EDGAR client and holon builder, Arelle for the OIM export, the
`sec` graph's MCP transport, and the holon viewer's parallel Cypher / SPARQL hand-offs. Nothing in
the platform is built for the benchmark.

## 7. The reference filing, measured

3M, FY2024 10-K, accession 0000066740-25-000006. Tokens at roughly bytes ÷ 4.

| Form | Size | ~Tokens | Fits |
|---|---|---|---|
| Plain text (rung 2) | 531 KB | 133K | everywhere |
| iXBRL, styling stripped, `ix:` tags + header kept (rung 3) | 2.08 MB | 520K | 1M-context models |
| XBRL instance XML, minified | 5.40 MB | 1.35M | nowhere |
| Full XBRL package (rung 4) | 9.44 MB | 2.36M | nowhere |
| xBRL-JSON as published (rung 5a) | 4.92 MB | 1.23M | nowhere |
| xBRL-JSON, text blocks removed (rung 5b) | 945 KB | 236K | 256K and up |
| xBRL-CSV, text blocks removed (rung 5b) | 673 KB | 168K | everywhere |
| `holon.jsonld` as serialized (rung 7d) | 11.95 MB | 2.99M | nowhere |
| PDF, rendered (rung 1) | 6.96 MB | 189 pages | under the 600-page cap |

Token counts are per tokenizer, not per byte: on one reasoning model the plain text counted 111K tokens (bytes ÷ 4 said 131K) and the xBRL-CSV 292K (the estimate said 168K) — numbers, commas and IRIs tokenize worse than prose. The frozen protocol carries the frontier model's exact counts, and "fits" is stated per model.

Tagging: 2,915 `ix:nonFraction` + 235 `ix:nonNumeric`; 549 distinct us-gaap concepts, 159 custom;
945 contexts, 917 dimensional; 3,151 facts in the OIM export, of which **107 are text blocks**.

**The finding under the table: the text-block facts carry about four fifths of every structured
serialization.** The structured forms are not big because of the numbers; they are big because
they embed the narrative as escaped HTML. As published, xBRL-JSON is no more ingestible than the
XML. Without the text blocks, xBRL-CSV is smaller than the plain text.

## 8. Publication and maintenance

Order: this protocol (frozen) → the harness → the results dataset and transcripts → the write-up.
The benchmark is re-run on each major model release or the page comes down. Every re-run
re-instantiates the templates on the newest filings (a new quarter of 10-Ks, public templates, new
instantiation) and re-runs the Vals public 50 as the fixed comparison point — contamination-proof
by construction.
