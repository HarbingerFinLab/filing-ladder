# Filing Ladder — protocol

**Status: v0.1, frozen 2026-09-06 (tag `protocol-v0.1`)** — every gate cleared 2026-09-03 (question
sets resolved, template golds confirmed by hand, every filing counted, the run priced); the corpus,
the graph and every exact count re-verified from scratch 2026-09-05 (principle 11); versions locked
(§6). v0.1 runs Sonnet 5 with an Opus 5 subset; a second frontier family and an open-weight column
are a v0.2 amendment on the same question sets, each with its provider pin. The protocol freezes as a tagged release whose
`filing-ladder questions` manifest (`questions/manifest.json`, question-set hashes) matches this document, *before* the
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
| 3 | iXBRL | the primary document with `<style>`, `<script>`, style/class attributes, ids on HTML tags, and the inline scaffolding (`<span>`, `<div>`, `<a>`, `<hr>`) removed; every `ix:` tag with its attributes, the `ix:header` (contexts, units) and the ids they reference kept; tables keep their markup | in context, 1M-context models; scored *cannot attempt* on any filing whose exact count exceeds the window (§7) |
| 4 | XBRL package | instance + schema + presentation/calculation/definition/label linkbases on disk; tools: list, read line range, grep | tools |
| 5a | OIM as published | xBRL-JSON and xBRL-CSV as Arelle's `saveLoadableOIM` writes them, with the SEC's inline-XBRL transformation registry loaded as EDGAR's own validator loads it; the same file tools | tools |
| 5b | OIM in context | the same export with text-block facts removed (a fact is a text block when its concept is a `TextBlock`, its value is markup, or its value is ≥300 characters); xBRL-CSV facts + metadata by default | in context |
| 5c | Tavi, raw jq | the filing as a Project Tavi compiled model (XBRL International's OIM Taxonomy Model, PWD 2026-09-01) — facts and taxonomy in one JSON document, written by `xbrlkit`; describe + one read-only jq tool, the same hand-off as 7b and 7c | tools |
| 5d | Tavi in context | the same document with text-block facts removed, as text | in context, 1M-context models |
| 6 | `companyfacts` | the SEC's `data.sec.gov` API through three tools: search concepts, one concept's facts, one frame across filers | tools |
| 7a | property graph, shaped tools | the RoboSystems `sec` graph over MCP: financial statements, fact grids, element resolution, document search and sections, read-only Cypher | tools |
| 7b | property graph, raw Cypher | the filing as a LadybugDB property graph — the RoboSystems `sec` graph's schema and ids, one filing, text blocks inline, built by `xbrlkit` (`--format lpg`): describe (schema computed from the database, concepts and periods present, example queries) + read-only Cypher | tools |
| 7c | RDF, raw SPARQL | the filing as `holon.jsonld` in an in-memory rdflib store: describe (prefixes, node shapes computed from the graph, concepts and periods present, example queries) + read-only SPARQL | tools |
| 7d | RDF in context | the `holon.jsonld` as text | in context, once compacted |

Rung 5c was added on 2026-09-04, before the freeze. The webinar claim quoted in §1 was made about
the OIM Taxonomy Model, since renamed Tavi, so the claim is measured on the artifact it was made
about rather than on the older xBRL-JSON alone. The document is produced by the author's own
converter (`xbrlkit`, diffed object by object against Arelle's unreleased Tavi plugin), which is
disclosed here for the same reason the graph rungs are.

Rung 7b moved off the production graph on 2026-09-05. It now queries the filing's own
property-graph file, built by `xbrlkit` from the same projection the platform builds its shared
graph from — the same tables, columns and ids, checked row for row against the platform's own
processor on the 26-filing corpus (§7.4) — so 7b, like 5c and 7c, runs from a file the harness
materializes and needs nothing to be up. The configuration it replaced, the shared graph over MCP
with only schema, examples and read-only Cypher exposed, is kept as the appendix ablation *7a
without tools* (§7.4).

**Where the taxonomy lives** is the axis the strata below test:

| Rung | Facts | Taxonomy (labels · presentation · calculation) |
|---|---|---|
| 4 | XML instance | XML linkbases, separate files — arcs to locators to hrefs |
| 5a / 5b | JSON / CSV | absent — xBRL-JSON references the DTS by URL and carries none of it |
| 5c / 5d | JSON | JSON, same document — labels, presentation, calculation, cubes |
| 7c | JSON-LD | JSON-LD, same graph, same query language |
| 7a / 7b | property graph | property graph, same graph |

**Six comparisons inside the ladder**, each isolating one thing: 7a vs 1 (the whole stack against
the PDF); 5b vs 7 (the layer above JSON); 7a vs 7b (the product against the substrate: the shaped
tools, the serving shape — a shared corpus graph with a search index against one filing's graph
with its text inline — and the corpus context, together; the tool layer alone is isolated by the
*7a without tools* ablation, §7.4); 7b vs 7c (the graph model, LPG vs RDF, the same facts including
the narrative, the same consolidated flag, the same period semantics — the only variable is the
query language and how reliably a model writes it; before 2026-09-05 the two did not hold the same
text, §7.3);
5c vs 7c (the taxonomy in JSON vs in RDF, the same describe-and-one-query hand-off — the only
variable is the data model and the query language); 4 / 5 vs 5c / 7c on structure questions
(taxonomy serialization — the standards body's own before and after).

**Same model, same effort, same prompt skeleton, same output contract, same turn budget on every
rung.** The output contract is a final block — `ANSWER` with units, `PROVENANCE`, `CONFIDENCE`
(high | medium | low | abstain) — so abstention and provenance are scored from the answer, not
inferred. A rung that cannot attempt a question (rung 4 in context; rung 3 on a 200K-context model;
rungs 1–3 on a corpus screen) scores it as a miss **and logs the cost of finding that out**.

**v0 runs rungs 1 · 2 · 3 · 5a · 5b · 5c · 6 · 7a · 7b · 7c**, k = 3 runs per question. Whether an in-context form fits is decided per filing from the frontier model's exact token count (`filing-ladder tokens --exact`), never from a byte estimate. Rung 5a joined v0 on 2026-09-05: the text-block facts are
four-fifths of an OIM file, so the in-context form (5b) cannot hold a narrative answer by
construction, and OIM as the standards body ships it is measured through the file tools beside
it, as Tavi is (5c beside 5d). Rungs 4, 5d and 7d,
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
  separately, never holistically. A rubric carries **correctness points** (each must be met)
  and, kept separate, **contradiction statements** (a conflict with any one is a confident-wrong):
  the Vals operators. They stay distinct because a negative phrased as a point inverts the score —
  found on the first judged run (2026-09-03), when two template rubrics written that way marked
  every correct answer wrong; fixed, and disclosed here as the class of scoring defect an
  interested author must publish. A second one (2026-09-04): the answer extractor read the
  first "answer:" in a transcript rather than the final block, so a bold *Answer:* heading in a
  model's reasoning scored a correct $1,181 million as wrong on rung 5b; it now reads the last
  complete block, and both measured runs were re-scored. Rubrics are human-reviewed before the run; the judge sees
  question, gold and answer only, never the rung. Claude 5 models expose no sampling controls, so the judge runs at the model's default with adaptive thinking, and the judge's own repeatability is checked on the human-reviewed sample. Every judge disagreement and a
  20% random sample are human-reviewed; transcripts are published. The Vals set is also reported by
  its nine task categories.
- **Abstention vs confident-wrong.** A confident answer that contradicts the gold is the
  confident-wrong case; on text answers the judge runs a dedicated contradiction check.
- **Cannot attempt.** A miss, reported separately, with its cost.
- **Provenance.** A locatable citation (page / statement line / concept + period) that is correct.
  A cited document, page or element that does not exist is a **hallucinated source**.
- **Repeatability.** k = 3 runs per question per rung; the share of questions whose runs agree.
- **Empty-result-answered** (7b, 7c). An answer produced after a query returned nothing.
- **Cost.** Per question per rung: input, cached and output tokens, dollars **at list price**,
  wall-clock, turns, tool calls, tool errors. v0 runs on the synchronous API and pays list, so
  the invoice and the exhibit are the same number; a batch lane (50% off, same list reported) is
  a re-run optimization, not part of v0. Rung 1 is reported
  cached and uncached. **Dollars per correct answer** is the headline.
- **Data-quality disagreements.** Where the PDF and the XBRL of the same filing disagree, logged as
  its own category, never scored against either rung.

## 5. Fairness rules

1. **Independent questions first, recent filings, the product corpus.** Set (i): Vals AI's 50
   public Finance Agent questions (CC BY 4.0) — expert-authored, written for document agents, so
   stacked toward the PDF rungs; the filing each needs is resolved for the model on every rung.
   **Resolved 2026-09-03 against the corpus (`questions/vals-filing-resolution.jsonl`): 32 of the
   50 map to a single 10-K or 10-Q; 18 do not and are dropped, by reason in §5.1.** That split is
   itself a finding about the set: a third of an expert-written "document agent" benchmark is
   answerable only from earnings releases, proxies, 8-Ks, or a foreign filer's reports.
   Set (ii): FinanceBench-shaped templates re-instantiated on current filings across the five
   strata; numeric gold read from the document by a person, never from a graph. The six v0
   template questions (3M FY2024 10-K, one per stratum plus one narrative) were confirmed by hand
   against the filing on 2026-09-03.
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
   workflow prompt. 7c uses raw SPARQL only, never a fact-grid convenience. Since 2026-09-05 they
   get the same text too: 7b queries the filing's own graph with its text blocks inline, as the
   holon carries them. Before that, 7b queried the production graph, which stores a text block as
   the URL of its CDN copy and indexes the text for rung 7a's search tool, so on a narrative
   question 7c could read the note and 7b could not; §7.3 records what that cost, and §7.4 keeps
   that configuration as the ablation.
10. **The shakedown endpoint never produces a published rung.** A free tier is used to prove the
    harness and read the per-rung token ratio, nothing more.
11. **A defect the subset finds in the author's own product is fixed and disclosed before the run,
    never scored as the graph's accuracy and never fixed silently.** The measured subset
    (2026-09-03: the six 3M questions, Sonnet 5, k = 1, cost calibration only, not a published
    rung) found two. The SEC text index cut every multi-page note after its first
    `ix:continuation`, so the PFAS exit-actions paragraph was not in the corpus at all and the
    commitments note held 570 of 130,272 characters; and the statement and fact-grid tools kept
    the first duplicate fact per period rather than the most precise, returning FY2024 R&D as
    1,100 (the narrative's rounded figure) for the statement's 1,085. Both are fixed in
    RoboSystems PR #1348 (2026-09-03); the run does not start until that fix is deployed and the
    text index rebuilt. Had they stayed, the run would have reported them as data-quality
    disagreements (§4). The interest named in the disclosure above is exactly the ability to fix
    the product between the shakedown and the run, which is why the fix is published here.
    A third defect (2026-09-04) was in this harness, not the product, and cut the other way:
    rung 5 was exported without the SEC's inline-XBRL transformation registry, so every fact
    an EDGAR filing formats through an `ixt-sec` transform — spelled-out durations and numbers,
    ballot boxes — carried a null value and no error. On 3M that was 106 null values against
    the 3 the filing reports as nil; every filing in the corpus had between 18 and 213. Fixed
    here by loading the registry as EDGAR's own validator does; the rung 5 exports are
    regenerated before the run.
    A fourth harness defect (2026-09-05), in rung 3: the styling strip removed every `id`
    attribute, so the 945 contexts the `ix:header` is kept for lost the ids the facts'
    `contextRef` point at, and the 149 continuations lost the ids the notes' `continuedAt`
    point at — the inline XBRL was handed over with its references dangling. Fixed by
    keeping ids on XBRL tags; at the same time the inline scaffolding EDGAR renderers leave
    (`<span>`, `<div>`, `<a>`, `<hr>`) is stripped, which carries nothing a reader uses and
    brings the reference filing under the window (§7). Rung 2 is byte-identical before and
    after. Rung 3 was re-counted for every corpus filing.
    Two more in the product (2026-09-05), found by checking every disclosure section the
    text index is built from against the filing's own text-block facts as Arelle resolves
    them, on all 26 corpus filings (`bin/check_text_layer.py`): a concept tagged more than
    once kept only its first occurrence, so Microsoft's second purchase-price table and
    loanDepot's second servicing-assets roll-forward were not in the index at all; and
    `ix:exclude` page headers inside a tagged block (Oracle, Microsoft) were indexed as
    section text. Both fixed in xbrlkit PR #24, with a re-index of both source types before
    the run. After the fix every text block in the corpus over twenty words matches its
    resolved value.
    After all of the above (2026-09-05) the corpus was rebuilt from scratch: every derived
    form of all 26 filings deleted and regenerated from the EDGAR packages under xbrlkit
    0.4.1 (Chrome 152.0.7977.83 for the PDFs), then re-counted exactly. Every count in the
    frozen table reproduced to the token. The one change is additive: the Tavi forms (rungs
    5c and 5d) had been materialized for the reference filing alone, so their exact counts
    are added for the other 25 filings; three Tavi compiled models exceed the exact counter's
    limit and have no exact count, which gates nothing since rung 5c reaches the file through
    a tool. The text-layer check and the index audit both pass on the rebuilt corpus.

### 5.1 Vals questions dropped from v0, by reason

| Reason | Questions | n |
|---|---|---|
| Guidance or beat-or-miss: the source is an earnings release (8-K exhibit 99.1), an earnings call, or a shareholder letter, not a 10-K/10-Q | vals-03, 04, 06, 09, 38, 39, 47, 48, 49, 50 | 10 |
| Proxy statement (DEF 14A): board nominees, director compensation | vals-05, 13 | 2 |
| Multi-document narrative with no single filing source (merger commentary across 8-Ks and press) | vals-01 | 1 |
| Pre-2024 history: needs FY2019–2021 10-Ks; the corpus holds filings made from 2024 onward | vals-02 | 1 |
| Foreign private issuer (20-F / 6-K, monthly revenue reports) | vals-12 | 1 |
| Acquisition terms in an 8-K / merger agreement | vals-36 | 1 |
| The 10-K carries only the annual figure; the quarterly one is in the earnings release (verified against the filing's MD&A) | vals-41 | 1 |
| Cross-entity peer set (five filers): a T3 question, v1 scope | vals-42 | 1 |

Three resolutions carry caveats, recorded in the file: vals-16 (KKR) is prospectus-level detail
answered from the Q1 2025 10-Q's equity note, so partial coverage is expected; vals-15 (United
States Steel) has no ticker on its graph entity, so the graph rungs must find it by name or CIK;
vals-29 (Spirit) is filed by Spirit Aviation Holdings under a post-emergence ticker. Eight of the
32 resolved questions read the same filing (Airbnb's FY2024 10-K), which the per-filing cache
makes cheap for the in-context rungs and which the write-up discloses.

## 6. Harness

Python; the harness runs its own tool loop so every rung runs on any model with function calling.
Providers: Anthropic direct for the frontier run (document blocks with citations, prompt caching,
batch for paying); OpenAI direct for a second frontier family (PDF as a file part, automatic
caching); an OpenAI-compatible route for the shakedown (NVIDIA Build: no PDF input, no caching)
and for open-weight models (OpenRouter, provider pinned, the credits charged recorded per turn).
OpenAI bills a request whose prompt reaches 272K tokens at long-context rates; the cost table
applies that tier per request, and on most filings it covers rungs 1, 3, 5a and 5b. Tool errors are returned to the model for correction; rate
limits and overloads get exponential backoff with jitter.

Filing acquisition, rung materialization and the graph rungs reuse published code: the
`xbrlkit` EDGAR client and holon builder, Arelle for the OIM export, the
`sec` graph's MCP transport, and the xbrlkit viewer's parallel Cypher / SPARQL hand-offs. Nothing in
the platform is built for the benchmark.

Versions locked for v0: `xbrlkit` 0.4.1, Arelle 2.44.6, Chrome 152.0.7977.83 for the PDF render,
and RoboSystems v1.11.16 (released 2026-09-06; the first release carrying the corpus fixes
disclosed under principle 11, PRs #1357–#1359, and the corpus-check harness) for rung 7a's index
and tools. The run's graph is a fresh local load of the 26 corpus filings under that release,
verified before the run by the index audit, the facts-against-gold check and the search probes.
The run manifest records the model, the provider pin and the context window per run.

## 7. The reference filing, measured

3M, FY2024 10-K, accession 0000066740-25-000006. The estimate column is bytes ÷ 4; the exact
column is the frontier model's own count (`claude-sonnet-5` tokenizer, Anthropic token-counting
endpoint, 2026-09-03), which is what decides "fits".

| Form | Size | ~Tokens (bytes ÷ 4) | Exact (Sonnet 5) | Fits on the frontier model |
|---|---|---|---|---|
| PDF, rendered, 189 pages (rung 1) | 6.96 MB | 378K | **513,102** | 1M window |
| Plain text (rung 2) | 531 KB | 133K | **215,180** | 1M window (not a 200K one) |
| iXBRL, styling stripped, `ix:` tags + header kept (rung 3) | 2.08 MB | 520K | **1,001,237** | **nowhere — cannot attempt** |
| XBRL instance XML, minified | 5.40 MB | 1.35M | — | nowhere |
| Full XBRL package (rung 4) | 9.44 MB | 2.36M | — | nowhere |
| xBRL-JSON as published (rung 5a) | 4.92 MB | 1.23M | — | nowhere |
| xBRL-JSON, text blocks removed (rung 5b) | 945 KB | 236K | **512,543** | 1M window |
| xBRL-CSV, text blocks removed (rung 5b) | 673 KB | 168K | **447,717** | 1M window |
| `holon.jsonld` as serialized (rung 7d) | 11.95 MB | 2.99M | — | nowhere |

Token counts are per tokenizer, not per byte, and the gap is not small. Claude 4.7 and later
models tokenize roughly 30% denser than earlier ones on prose, and structured forms fare worse
still: on Sonnet 5 the plain text counts 1.6× its byte estimate, the PDF 1.4×, and the xBRL-CSV
2.7× — numbers, commas and IRIs tokenize worse than prose. Three consequences for the ladder,
each a finding before a single question is asked: (1) the inline-tagged document EDGAR already
ships (rung 3) does not fit the largest window available, so "the tags are already in the
document" is not an option a model can take on this filing; (2) the OIM export without its text
blocks, the form XBRL International offers as the AI-ready one, is 2.1× the plain text and
the same size as the rendered PDF; (3) "fits in 200K" holds for nothing here. A byte estimate
was off by up to 2.7×; every fit decision in the run is made from the exact count.

### 7.1 Every filing in v0, counted

All 26 filings the 38 questions resolve to were materialized and counted the same way; the
per-filing counts are committed in `questions/filing-token-counts.json` (hashed in the manifest),
and the harness reads them when a replication has no API key, so a re-run makes the same fit
decisions. On the frontier tokenizer:

| Form | Range across the 26 filings | Exceeds the 1M window | Consequence |
|---|---|---|---|
| PDF (rung 1) | 201K – 692K tokens | none by tokens; **one filing's PDF (156 pages, 28 MB of embedded images) exceeds the API's 32 MB request cap** | rung 1 is *cannot attempt* on that filing (vals-31); the cap is a property of the PDF path and is scored as one |
| Plain text (rung 2) | 74K – 292K | none | attempts everywhere |
| iXBRL (rung 3) | 355K – **1.81M** | **4 of 26** (3M 1.00M, United States Steel 1.04M, Allstate 1.61M, KKR's 10-Q 1.81M) | rung 3 is *cannot attempt* on 9 of the 38 questions |
| xBRL-CSV, text blocks removed (rung 5b) | 116K – 976K | none (KKR at 976K leaves no room for output) | attempts everywhere; KKR may stop on the window |
| xBRL-JSON, text blocks removed | 131K – 1.10M | 1 (KKR) | v0 hands the CSV form |

Every in-context form of every filing is over 200K on at least one rung; a 200K-window model
could run only rung 2, and only on 22 of the 26 filings.

### 7.2 What the run costs, priced before it runs

At list prices on 2026-09-03 (Sonnet 5 $2 / $10 per million input / output tokens, 5-minute cache
write 1.25×, cache read 0.1×; Opus 5 $5 / $25), k = 3, 38 questions, with the run ordered by
filing so each document is cached once per rung and read for the remaining runs:

| Pass | Questions | With the per-filing cache | If every document run paid full input |
|---|---|---|---|
| Sonnet 5, full | 38 | ≈ $165 | ≈ $350 |
| Opus 5, stratified subset | 13 | ≈ $125 | ≈ $280 |

Roughly three quarters of the spend is the four in-context rungs; the four tool rungs together
are under $45 per pass. The judge adds single-digit dollars. These figures are the pre-registered
expectation; the run's actual usage is published beside them.

Tagging: 2,915 `ix:nonFraction` + 235 `ix:nonNumeric`; 549 distinct us-gaap concepts, 159 custom;
945 contexts, 917 dimensional; 3,151 facts in the OIM export, of which **107 are text blocks**.

**The finding under the table: the text-block facts carry about four fifths of every structured
serialization.** The structured forms are not big because of the numbers; they are big because
they embed the narrative as escaped HTML. As published, xBRL-JSON is no more ingestible than the
XML. Without the text blocks the structured facts fit in a 200K window — about a quarter larger
than the plain text by bytes, and 2.6× larger on one reasoning model's tokenizer, because numbers,
commas and IRIs tokenize worse than prose.

### 7.3 Control: the property graph with its text blocks inline (not a rung)

The ladder holds the facts constant so the rungs compare; the production system's shape is rung 7a
— facts in the graph, narrative in a search index, tools that read both. Rung 7b as shipped queries
a graph whose text blocks are URLs, so on a narrative question it has less than 7c (principle 9).
The 2026-09-04 shakedown found the case: 7b missed one rubric point on the PFAS exit question — that
the $66 million charge was "recorded primarily in cost of sales" — which the structured facts do
not carry and the filing states in the restructuring note. To separate the representation from the
query language, the graph was rebuilt on a local stack with the text blocks kept in the graph as
well as indexed (a default-off flag, RoboSystems PR #1351; never on in production, where the
narrative is four fifths of the bytes and the search index exists to keep it out of the graph),
3M FY2024 only, and rungs 7a and 7b were re-run on the six 3M questions. Same model (Sonnet 5),
same judge, k = 1, the same filing loaded once per configuration.

| Rung | Graph | Accuracy | $/q | Turns | Tool calls | Input tokens / q |
|---|---|---|---|---|---|---|
| 7a MCP tools | as shipped (text externalized) | 6/6 | $0.048 | 2.2 | 1.5 | 16,688 |
| 7b raw Cypher | as shipped (text externalized) | 5/6 | $0.107 | 5.0 | 4.3 | 39,333 |
| 7a MCP tools | control (text inline) | 6/6 | $0.045 | 2.3 | 1.5 | 14,727 |
| 7b raw Cypher | control (text inline) | 6/6 | $0.175 | 5.7 | 5.3 | 72,310 |

With the note in the graph, 7b answers the PFAS question fully. How it got there is the finding:
Cypher on this graph has no text search, so the model returned the whole 60,000-character note in
one result, tried `apoc.text.indexOf` (the engine has no APOC), then paged the note with
`substring` at fixed offsets — 10 turns, 11 tool calls, 294K input tokens for one question. 7b's
cost per question rose 63% and its average input nearly doubled. 7a did not move, because it never
read the inline text: the search tool found the sentence in both configurations.

Two conclusions, and the limits of each. The 7b miss was representational, not a query-language
result — the LPG-vs-RDF comparison is clean on numeric questions and confounded on narrative ones,
which is why principle 9 now says so. And the production shape is the cheapest surface on the
ladder that has both the numbers and the text; putting the text into the graph buys 7b the answer
at the price of reading the note by offsets. This is a control, not a rung: it is a configuration
nobody can run against the production graph, one filing, one run per question, and its transcripts
go into the results dataset beside the shakedown's rather than being scored beside the rungs.

Superseded as a configuration on 2026-09-05: rung 7b now runs on the filing's own graph, where the
text is inline by construction (§7.4), and the as-shipped 7b of this table is the *7a without
tools* ablation.

### 7.4 Rung 7b on the filing's own graph, and the *7a without tools* ablation

From 2026-09-05 rung 7b is a file. `xbrlkit build --format lpg` projects the filing into a
single-file LadybugDB database with the tables the RoboSystems `sec` graph is built from: the
same node labels (Entity, Report, Fact, Element, Period, Unit, Dimension, Taxonomy, Structure,
Association, Label, Reference), the same relationship types, the same columns in the same order,
and the same ids — every id is a UUID5 of the same content against the platform's namespace, so a
fact in the file and the same fact in the shared graph are one row. The projection was checked
against the platform's own processor on the corpus's 26 filings with the platform's enrichment
switched off: every node and relationship table is row-identical, with two explained exceptions —
association ids, which the platform mints at random and the projection derives from the arc, and
the exact duplicate arcs the platform writes inside Arelle's aggregate `XBRL-dimensions` network
(123 on 3M), which the derived ids collapse to one. What the file does not have is what the
platform adds after projection: text blocks stay inline in `Fact.value` where the platform serves
them from a CDN and indexes them for rung 7a's search tool, `Element.canonical_concept` and
`Structure.canonical_type` are empty where the platform's embedding pass fills them, and the
`FactSet` and `Classification` tables are empty where its association classifier fills them.

The hand-off is the one 5c and 7c get: `describe_graph` (the schema computed from the database,
how to read a fact, the concepts, periods and units present, and example queries — including one
that reads a note by `contains()` and a regex window, because the engine has no text index) and
`run_cypher` (one read-only query in a child process with a 60-second limit and a 200-row cap,
the database opened read-only). The rung needs nothing to be up, so it is reproducible from the
published corpus alone.

The *7a without tools* ablation is the configuration 7b had before this change: the production
graph over MCP with only `get-graph-schema`, `get-example-queries` and `read-graph-cypher`
exposed. It is the one pair that isolates the tool layer with serving and corpus held constant,
which 7a vs 7b no longer does. It is not a rung: it depends on the production system, its
transcripts go into the results dataset beside the control in §7.3, and it is run when 7a is run
and reported beside the rungs, never as one. The harness names it `7b-mcp`.

## 8. Publication and maintenance

Order: this protocol (frozen) → the harness → the results dataset and transcripts → the write-up.

**Versions.** The protocol version is the row of the results table; the model is the column. The
first number after *v0* changes when locks, question sets or rung definitions change, and every
rung re-runs. The last number changes when rungs or controls are *added* under unchanged locks and
question sets: they are pre-registered here before they run, tagged, and every earlier row carries
forward unchanged by identity (the same records, the same hashes). Corrections to this text after a
freeze go in §9, dated; additions go in their own numbered section, like §10.
The benchmark is re-run on each major model release or the page comes down. Every re-run
re-instantiates the templates on the newest filings (a new quarter of 10-Ks, public templates, new
instantiation) and re-runs the Vals public 50 as the fixed comparison point — contamination-proof
by construction.

## 9. Errata and amendments after the freeze

The text above is the pre-registered protocol as tagged `protocol-v0.1` and is not edited after
the freeze. Corrections to what it describes are recorded here, dated, and carried into the v0.2
pre-registration.

- **2026-09-06 — what rung 7a's search index contains.** §7.3 describes rung 7a as "facts in the
  graph, narrative in a search index", and §2's table calls it a property graph behind shaped
  tools. The index also holds the parsed narrative sections of the 10-K body (Items 1, 1A, 1C, 2,
  7 and 7A), which are untagged and therefore in no XBRL-derived form on the ladder; the protocol
  did not say so. Measured from the published transcripts: 21 of 7a's 51 correct T1 answers and
  10 of its 32 correct T2 answers were read from an untagged section; scored as misses, 7a would
  be 50% and 41%; eight questions were answered 24 of 24 times by 7a and 0 of 3 by every XBRL
  form. Recorded in full in `results/v0.1-sonnet-5/README.md` ("What rung 7a's index contained"),
  where the rung is relabelled "graph + document index, shaped tools". No score changes. For the
  claims: 7a against the XBRL forms compares the whole filing made queryable with projections of
  its tagged subset, not the same data in two forms; and 7a against 7b is confounded by content as
  well as by the query layer, since 7b's graph carries the tagged text blocks inline, no untagged
  section and no search tool. v0.2 pre-registers two controls: 7a with search restricted to
  tagged disclosures (a harness-side filter on the tool's results), and shaped tools over the
  loaded XBRL model with tagged content only.

- **2026-11-08 — a third versioning case (§8), for v0.1.2.** §8 names two: the first number
  moves when locks, question sets or rung definitions change and every rung re-runs; the last
  moves when rungs or controls are *added* under unchanged locks and question sets. v0.1.2 is
  neither: four rungs re-run under new locks, one is added, the question set, the model and the
  prompt skeleton are untouched. The rule, from here on: *a rung is re-materialized when its
  artifact bytes or its tool list change under a new lock; a re-materialized rung re-runs, and its
  published rows gain a successor rather than carrying forward. Every rung whose artifacts and
  tools are unchanged carries forward by identity, and the pre-registration records the SHA-256 of
  each carried-forward form so the identity is checkable rather than asserted. The last version
  number moves.* §11 was pre-registered under it as v0.1.2 the morning of 2026-11-08; that night,
  before any run and before any tag, the model moved to Sonnet 5.5 and §11 became v0.2 — the
  first-number case, under which nothing carries forward. The rule stands for the next case that
  fits it; v0.1.2 never ran.

## 10. v0.1.1 — the document as a constant (pre-registered 2026-09-07)

**What v0.1 could not separate.** §9's first entry: rung 7a's search index held the untagged body
of the 10-K, so 7a against the XBRL forms compared the whole filing made queryable with projections
of its tagged subset, and 7a against 7b was confounded by content as well as by the query layer.
`results/v0.1-sonnet-5/README.md` measured the shares: the tagged text blocks carry a median 46% of
a filing's text, the parsed Items a median 57%, the two together nearly all of it.

**The rule.** Every tool rung gets the whole primary document the same way, so the document is a
constant and the form is again the only variable. In-context rungs cannot take it, for size; that
stays their finding.

**Ten controls**, reported beside the rungs and never as rungs (the §7.3 / §7.4 precedent), same
locks as v0.1 (§6), same 38 questions (`questions/manifest.json`, hashes unchanged), same model
(`claude-sonnet-5`, Anthropic direct, model-default sampling), k = 3, the same turn budget (12),
prompt skeleton and output contract as v0.1 (fairness rule 3):

| Control | Built on | What is added or removed |
|---|---|---|
| 2t | — | rung 2's plain text behind `search_text` / `read_text` and nothing else: the minimal retrieval baseline |
| 5a+doc | 5a | the document tools beside the file tools over the OIM files |
| 5c+doc | 5c | the document tools beside describe + jq |
| 6+doc | 6 | the document tools beside the three companyfacts tools |
| 6+efts | 6 | `search_filings`: the SEC's EDGAR full-text search pinned to the filing — file-level hits with scores, no text (the publisher's own two surfaces, and nothing else) |
| 7a-tagged | 7a | `search-documents` results with every `narrative_section` hit removed and the total recomputed; `get-document-section` refuses any id the model was never shown; same tools, same descriptions, same prompt |
| 7a+doc | 7a | the document tools beside the MCP tools (the product's specified public shape: graph, index, and the raw filing beside) |
| 7a-facts+doc | 7a | 7a's fact tools only (`search-documents` and `get-document-section` removed) plus the document tools: the product's structure on exactly the document access every other form has |
| 7b+doc | 7b | the document tools beside describe + Cypher |
| 7c+doc | 7c | the document tools beside describe + SPARQL |

**The document tools, identical everywhere** (`filing_ladder/representations/document.py`):
`search_text(pattern, window=300, max_hits=10)` — a case-insensitive regular expression over the
plain text, each hit returned as its character offset and a window centred on it, with the total
match count (window ≤ 1,500, hits ≤ 25); `read_text(offset, length≤4000)` — the span at an
offset. The text is rung 2's (the EDGAR primary document, tags stripped), never re-chunked or
re-ordered; it is one line, so the tools work on offsets, not lines. The rung's own tools are
untouched; one runner dispatches between them. Each control's system prompt is its base rung's
plus one sentence naming the two tools (`filing_ladder/prompts.py`, `DOCUMENT_BESIDE`); 7a-tagged's
prompt is 7a's, unchanged, because the filter is silent.

**Why 7a needs two "+doc" rows.** As shipped, 7a is the only form whose document access goes
through its own index, and that index answers with chunks of ~14,000 characters where the constant
tool answers with 300-character windows, so 7a against an X+doc row would compare retrieval
mechanisms and their token bills, not forms; and 7a+doc holds two routes at once. 7a-facts+doc puts
the product's structure on the same document access as every other form, so X+doc rows compare
form to form; 7a as shipped against 7a-facts+doc then measures the product's index against the
constant tool — the retrieval mechanism as its own variable, on accuracy and on cost.

**What the pairs measure.** 7a-tagged against 7a: the content effect by subtraction. Each form
with the document against the form alone: the content effect by addition; the two should agree.
2t against each form with the document: the structure effect, per form, separated from the text.
6+efts against 6: what the publisher's own search adds. The API's shape predicts little on a
single-filing question, with one route left open and disclosed here: a phrase search can confirm a
name or figure the model already holds from memory (it asks whether "Elinor Mertz, Chief Financial
Officer" is in the filing rather than reading who signed), so a correct 6+efts answer may be the
model's memory checked against the publisher's index rather than read from the filing. The judge
scores the answer, not the route; the transcripts show the route.

**Publication.** `results/v0.1.1-sonnet-5/` holds the nine controls' records, judged by the v0.1
judge with the same rubrics, and a README with the combined table: the v0.1 rows carried forward
unchanged, the controls beneath them, labelled. Tags: `protocol-v0.1.1` on this section before the
run; `results-v0.1.1` after. Estimated cost at list: $165–215 for the ten at k = 3, plus the judge.


## 11. v0.2 — the forms that are ours, re-materialized; the document through xbrlkit; the model moved to Sonnet 5.5 (pre-registered 2026-11-08)

**What this is.** A re-measurement of the four forms that are ours — 5c (Tavi), 7a (the `sec`
graph's shaped tools), 7b (the filing as a LadybugDB file, raw Cypher), 7c (the holon, SPARQL) —
with the tooling as it stands, on the frozen question set, on the current Sonnet; one rung added; the
document delivered to every rung of ours by xbrlkit's own text tools; rung 2 run as the anchor that
reads the model's own gain. The model moved, so this is the first-number case §8 names — v0.2 — and
§8's other rule holds with it: the model is the column. The Sonnet 5.5 column opens here with the
nine rows this funding covers; nothing carries forward by identity across a model change, so the
column's other rows are open, pre-registered with their definitions unchanged, to run when funded.
Still one filing per question and no corpus claim. (This section was pre-registered the morning of
2026-11-08 as v0.1.2 under §9's third versioning case, with the model held; the same night the model
moved and the section became v0.2, before any run and before any tag. §9 records the sequence.)

**What changed since the freeze.** (1) xbrlkit 0.4.1 → 0.21.4. The holon went lossless in 0.7
(per-report namespace bindings, every label role, the lexical value), the property-graph projection
gained the single-file `.lbdb` export in 0.20, and `xbrlkit serve` arrived in 0.5 — shaped tools over
a filing held in memory, no graph, no platform. Every 7b and 7c artifact in the corpus was
re-materialized under 0.21.4 on 2026-11-08 (the 26 holons total 233 MB, about a quarter larger than
under 0.4.1; the 26 graphs 555 MB; 4–6 s a filing); the 5c Tavi files regenerated on 2026-10-14
stand. (2) The `sec` server grew five tools, all of them xbrlkit's own functions wrapped by the
platform over the filing held whole: `describe-filing`, `disclosures`, `information-block`,
`search-text`, `read-text`. The last two read the whole primary document — cover page, signatures,
Part III — which v0.1's results README named as the index gaps behind 7a's misses. 7a's tool filter
is by exclusion, so the five flow in; 15 tools listed, 13 given. (3) RoboSystems v1.22.2 carries the
`canonical_concept` restamp (#1941) the parent spec named as a known defect of the 7a path, verified
on the hosted repository on 2026-11-08, read-only, and the fact-read fix (#2008) recorded under the
7a lock below. (4) The model: Sonnet 5 → Sonnet 5.5 (`claude-sonnet-5-5`), the current Sonnet. Same
list prices for input and output ($2 / $10 per million tokens) and for a cache write ($2.50); a cache
read is half Sonnet 5's ($0.10 against $0.20); all verified on the provider's price page on
2026-11-08 and recorded in `prices.json`. Same tokenizer. Thinking is on by default on both models,
and the harness sends no thinking, sampling or tool-choice parameter to either, so the lock is the
model's defaults in both columns; Sonnet 5.5's effort levels are recalibrated, so its token volume per
question is not assumed from Sonnet 5's — it is measured on the model shakedown below. Its thinking
blocks are bound to the model and the conversation; the harness replays every block it receives
unchanged and only ever appends, as it did on Sonnet 5. It can end a turn with the stop reason
`refusal`, which the harness records as it records any stop reason.

**The lineup**, in run order — the headline first, the identity checks last, so that a cut for
cost falls on the rows whose predecessors already exist:

| | What the model gets | The document | v0.2 | Sits beside (the Sonnet 5 column) |
|---|---|---|---|---|
| **4c** *(new)* | xbrlkit's shaped tools over the filing parsed from its own XBRL package, in memory | native — `search_text` / `read_text`, product profile | **added, run** | 7a (the platform's shaped tools against the library's); 5c (shaped tools against raw jq over the same model) |
| **7a** | the `sec` repository's 13 shaped tools over MCP, hosted | native — `search-text` / `read-text` | **run** (lock: RoboSystems v1.22.2, hosted) | 7a v0.1; 7a+doc v0.1.1 |
| **5c+doc** | 5c + xbrlkit's two text tools | the instrument below | **run** | 5c+doc v0.1.1 |
| **7b+doc** | 7b + the two text tools | the instrument | **run** | 7b+doc v0.1.1 |
| **7c+doc** | 7c + the two text tools | the instrument | **run** | 7c+doc v0.1.1 |
| **5c** | the Tavi compiled model, describe + jq | none in the form | **run** (artifacts of 2026-10-14) | 5c v0.1 |
| **7b** | the filing as `.lbdb`, describe + read-only Cypher | none in the form | **run** (re-materialized) | 7b v0.1 |
| **7c** | the holon in rdflib, describe + SPARQL | none in the form | **run** (re-materialized) | 7c v0.1 |
| **2** | the plain text, whole, in context | by construction | **run as the anchor**: the same bytes rung 2 read in v0.1, on the new model, no tools in the form — the model's own gain is read here, and every tool row's move is read against it | 2 v0.1 |
| 1 · 3 · 5a · 5b · 6 · 2t · 5a+doc · 6+doc · 6+efts · 7a-tagged · 7a+doc · 7a-facts+doc · 7b-mcp | — | — | **open rows of the column, not run in this funding**: nothing carries forward across a model change; their definitions are unchanged, and the SHA-256 of every artifact they read is recorded in `results/v0.2-sonnet-5-5/artifact-hashes.json` so a later run reads the same bytes | their Sonnet 5 rows stand |

7a's own "+doc" control is retired: the product carries the document natively. 7a-tagged and
7a-facts+doc are not run — their tool subsets would need redefining against the new names, and
neither is what this run asks. Rungs 1 and 3 are the most expensive rows of the column and the least
affected by the tooling (nothing in either lock touches a PDF or an inline document); they wait on
funding, and until they run the Sonnet 5.5 column has no in-context row above rung 2. 5a and 5b come
from Arelle's export, untouched since 2026-09-05; the ladder's Arelle pin
moved to 2.45.3 since, recorded here, not acted on.

**Rung 4c — the package behind `xbrlkit serve`.** The harness loads the filing's package folder
(`data/<accession>/package/`, the inline document with its schema and linkbases, as acquired from
EDGAR) through xbrlkit's `FilingSession`, and builds the server `xbrlkit serve` runs —
`xbrlkit.serve.build_server` — over it, in-process: the tool definitions come from the server's own
`list_tools`, every call goes through its `call_tool`, so the tools, their descriptions, their
argument schemas and their answers are the library's and not the harness's. Only the Streamable HTTP
transport is left out; the transport is not a variable. `read_from` is `file`: the filing as filed,
no CDN, no EDGAR, no network (the filer-metadata lookup xbrlkit makes is on its EDGAR and CDN load
paths only). Product profile, the document on — what `uvx xbrlkit serve <package>` gives any reader.
**Nine tools given**: `describe_filing`, `resolve_element`, `fact_grid`, `statement`, `calculation`,
`disclosures`, `information_block`, `search_text`, `read_text`. **Ten withheld**, each for a reason
recorded in `filing_ladder/representations/xbrlkit_serve.py` (`WITHHELD`) and tested against the
server's registration so a tool xbrlkit adds later is placed rather than defaulted: `run_cypher`
(raw Cypher over the same file is rung 7b); `load_filing`, `unload_filing`, `list_filings` (the
one-filing frame, and housekeeping — 7a withholds `list-subgraphs` and `get-graph-info` the same
way); `search_filings` (the SEC's full-text search, the 6+efts control's surface); `export_filing`,
`view_filing` (side effects, not answers); `documents`, `read_document` (the filing's other
documents — more than the one primary document every other rung has, so out under v0.1.1's rule);
`records` (the XML-lane tool, not applicable to an XBRL report). The hand-off prompt is the tool
rungs' skeleton with `describe_filing` as the first step, parallel to 7a's. Whose claim: the
open-source library's — the query craft done once, on the reader's own machine, with no server,
account or network. It is the parent spec's candidate 3 ("the control the ladder is missing": the
package family's 7a) and the pair it makes with 7a is the point: the same functions behind the
platform and behind the library, on the same model and the same document. §9's 2026-09-06 note
promised v0.2 "shaped tools over the loaded XBRL model with tagged content only"; 4c is that surface
with the document on, as the product ships it (`with_document=True`); the tagged-only variant is the
same server with the document off, not run in this funding and recorded here.

**7a on the hosted repository — a lock change, disclosed.** v0.1 and v0.1.1 ran 7a on a fresh
local load of the 26 corpus filings under a named release (§6). v0.2 runs it on the hosted `sec`
repository at `api.robosystems.ai`, RoboSystems v1.22.2, over the same MCP transport with the same
filing hint (ticker, form, fiscal year, CIK, accession). Why: the local-load rule existed to pin a
release carrying the corpus fixes, and the hosted graph is at a named release, verified the morning
of the pre-registration; a local load of the corpus, its filer catalog and its text index is two to
three days of the five the funding window has; and the hosted repository is the product as a user
gets it. What differs, stated so it can be read in the transcripts: the corpus is every processed
filing, not 26, so the corpus-wide tools (cross-filer fact grids, `search-documents` over the whole
index) are present — no frozen question needs them; an answer read from a filing other than the
question's is a confident-wrong of the form and is scored as such. The 7a prompt's source paragraph
now names the five tools in its second step; its first step and the skeleton are v0.1's. 7a's
v0.1.1 controls derive their prompt from 7a's in code and are not run; their published
transcripts carry the prompts they ran with.

**An engine defect, found, fixed and disclosed before the tag (principle 11).** The morning of
the pre-registration, the hosted graph's `financial-statement-analysis` served two face-statement
numbers as 0.0 — Microsoft's FY2025 goodwill, and the FY2025 total assets of Realty Income, a filer
outside the corpus. The cause is in the engine, not the data: LadybugDB 0.22.x skips a compressed
column's exception values when a filtered scan's 2,048-row batch straddles a segment boundary, so a
DOUBLE projected through a filter can read exactly 0.0. On a production backup that was 210 of
146,029 facts across 123 of 300 FY2025 10-Ks on the affected read path, and which facts are hit
changes with every nightly rebuild; the fact's text `value` is never affected. RoboSystems v1.22.2
(#2008, deployed 2026-11-09 00:46 UTC) takes the number from the text in the two shaped reads that
return fact numbers, `financial-statement-analysis` and `build-fact-grid`: on the backup the text
parses to exactly the number for all 74.3 million numeric facts, the wrong reads on the affected
path go from 210 to 0, and both 0.0 reads above re-read correct on the hosted repository after the
deploy. The ten other tools return no fact number from the graph (the five xbrlkit tools read the
filing held whole; `resolve-element` returns names, labels and counts). What stays exposed is raw
`read-graph-cypher` that returns, orders, filters or aggregates `f.numeric_value`: the engine
underneath is still 0.22.1 (the fix is filed upstream, LadybugDB #1540, unreleased), and the tool's
rules and `get-example-queries` now tell the reader to return `f.value`, which is guidance, not a
rewrite. A 7a transcript that shows it is a defect of the form, disclosed in the results, never
re-scored. On the shakedown's six questions 7a never reached for Cypher.

**The hosted repository's caps, and the harness's pace.** The `sec` repository counts every MCP
tool call against the subscriber's plan — the ladder's key holds the advanced plan: 25 a minute, 500
a UTC clock hour, 5,000 a day — and refuses over the cap with HTTP 429, which the MCP client hands
the model as a tool error indistinguishable from the engine's. The shakedown's 7a ran at about 13
calls a minute; a full 7a row at k = 3 would cross 500 in an hour. So the harness paces: a call goes
out only when fewer than 20 went out in the trailing minute and fewer than 450 in the current UTC
hour, and waits otherwise (`Pacer` in `filing_ladder/representations/mcp.py`; the pace is written
into the run's config). The model never sees the wait; the wall clock does, and the 7a row's wall
clock in the results is read with that in mind. v0.1's local load had no cap, so this belongs to the
lock change, not to what the model is handed. Two more facts of the hosted lock, recorded so the
transcripts can be read against them: the repository rebuilds after each weekday's close (the
replica cutover lands at about 04:30–05:40 UTC, Tuesday to Saturday), and 7a is run in one sitting
outside that window, with the server's reported version (`/v1/status`) written into the results
README at its start and at its end; and the harness runs tool calls one at a time, as it always has.

**The document instrument — xbrlkit's text tools on every rung of ours.** v0.1.1's "+doc" was two
harness tools over rung 2's text file. In v0.2 the document on 5c+doc, 7b+doc and 7c+doc is
xbrlkit's `search_text` and `read_text` over the same loaded filing 4c reads — one loaded filing
per corpus filing, shared by the rung and the controls — with the definitions the server lists and
calls through the server. What differs from v0.1.1's tools, all of it the product profile: a section
label on each hit; when more matched than came back, `sections` counts where the matches fall and
`sections_omitted` how many further sections hold the rest; on no match, `terms` counts the
pattern's own words; `read_text` pages to 8,000 characters (was 4,000) and returns `next_offset`.
`--pure` restores v0.1.1's hit shape and read cap and is documented in the library as the ladder's;
it is not run here, and `filing-ladder run --document harness` keeps v0.1.1's own instrument for a
replication wanting parity with those rows. The gate (principle 11): xbrlkit's readable text and
rung 2's plain text must carry the same document on all 26 filings, compared on alphanumerics —
length ratio within ±3%, and 24 probes of 80 characters taken from each and found in the other,
matched with whitespace removed because the two renderers split table cells and footnote markers
differently. `bin/check_readable_text.py` (`just check-readable`); the result is published in
`results/v0.2-sonnet-5-5/text-layer-gate.json` either way. **Result, 2026-11-08: 26 of 26.** Alphanumeric
length ratios 0.9989–1.0000 (xbrlkit's text is the longer by 1–3% in raw characters, the renderers'
whitespace). Three filings — Microsoft FY2024, KKR's 2025 quarter, Zillow FY2024 — matched only under
the whitespace rule, on a glued footnote marker, a table header split across cells and a page-footer
link; none is a difference in what the document says, and the rule was written for them before any
answer was read.

**Locks.**

| Lock | v0.1 / v0.1.1 | v0.2 |
|---|---|---|
| Model | `claude-sonnet-5`, Anthropic direct, model-default sampling | **`claude-sonnet-5-5`**, Anthropic direct, model-default sampling and thinking (nothing sent, as before). The lock change that opens the column: "the tools improved" and "the model improved" are separated inside the column by rung 2, which has no tools in its form — not by holding the model |
| Questions | 38 (32 Vals + 6 templates), `questions/manifest.json` | **same**; verified unchanged on 2026-11-08. `filing-token-counts.json` is one of its four hashed files and is deliberately not re-exported: the re-materialized holon's size goes in the results README |
| k · turn cap · max tokens · prompt skeleton · output contract | 3 · 12 · 16,384 · as frozen | **same** |
| xbrlkit | 0.4.1 | **0.21.4** (`xbrlkit[lpg,mcp]`); the hosted server runs 0.21.3 — identical package code, the release differs in README and CI only |
| RoboSystems, rung 7a | v1.11.16, fresh local load | **v1.22.2, the hosted `sec` repository** (above), on the advanced plan, paced at 20 calls a minute and 450 an hour |
| LadybugDB (7b) | 0.20.x | 0.22.1 — the engine with the filtered-scan 0.0 read above. Checked on the 26 filing graphs on 2026-11-08 under two filter shapes (`bin/check_lbug_doubles.py`; `results/v0.2-sonnet-5-5/lbug-double-reads.json`): 16,649 consolidated numeric facts, 0 misreads, 0 other disagreements between `numeric_value` and the text. Each graph holds under 1,200 facts, a single scan batch |
| Arelle | 2.44.6 | 2.45.3 in the lock; 5a/5b exports not regenerated — recorded |
| Prices | `prices.json` 2026-09-03 | **`claude-sonnet-5-5` row added**, verified on the provider's price page 2026-11-08: $2 / $10, cache write $2.50, cache read $0.10; Sonnet 5's row unchanged |
| Judge | `claude-sonnet-5`, rubric decomposition + contradiction check | **same** — the judge scores both columns; it is a lock of the scoring, not of the model under test |

**Cost, pre-registered.** Published per-rung actuals from v0.1 and v0.1.1 (k = 3, 38 questions,
114 records a rung) at Sonnet 5 list; tool rungs cache little, so these are robust to ordering. The
table is at Sonnet 5's token volumes: Sonnet 5.5's prices per token are the same or lower, its token
volume per question is unknown until its shakedown, and the table is re-scaled from that shakedown's
per-question costs before the tag.

| Piece | Estimate | Basis |
|---|---|---|
| 4c | $10–15 | shaped like 5c+doc ($10.99) |
| 7a, 13 tools | $12–15 | v0.1 $11.17; more tools, more text reads |
| 5c+doc · 7b+doc · 7c+doc | $11 · $9 · $10 | v0.1.1 $10.99 · $8.40 · $9.40 |
| 5c · 7b · 7c | $22 · $17 · $24–26 | v0.1 $22.00 · $17.12 · $23.96; the holon is a quarter larger |
| 2 (drift control) | $17 | v0.1 $16.58 |
| Judge, and the two k = 1 shakedowns on the six template questions | $15–20 | |
| **Total** | **$147–167** | funded by a promotional credit expiring 2026-11-13; the ceiling is $233 |

The run order is the cut order. If actuals at the midpoint of the plan run a quarter over the
estimate, the bare rows (5c, 7b, 7c) and then rung 2 are dropped and left as open rows of the
column — stated now so a cut is a pre-registered branch, not a choice made on the numbers.

**Expectations, stated before the run** (principle 2). (a) 7a's T1 moves up toward the plain-text
row: v0.1 bounded the whole-document gain at roughly 90–92% against plain text's 93%, and the two
named misses are now reachable. (b) 4c lands near 7a, not near 5c — the same facts behind shaped
tools with the same document; if so, the parent spec's sentence applies, "retrieval does the work,
not the platform", and is published as such; (c) 4c costs less per correct answer than 7a (no
transport, no index, no graph round trips). (d) 7b and 7c move little on T1 and more on narrative
questions through their +doc controls, as in v0.1.1; the re-materialization is a fidelity change,
not a reach change. (e) 5c is unchanged within error bars. (f) Rung 2 moves by the model's gain alone — the
same bytes, no tools in the form; small on T1 (v0.1: 93%), larger where v0.1's misses were reading
rather than retrieval — and that move is the baseline every tool row's move is read against: a tool
row that moves more than rung 2 has the tools' change in it, one that moves less has fallen behind the
model's own reading of the text. (g) Cost per
correct answer on the four forms stays in the v0.1.1 band ($0.08–0.15), with 7a's native text reads
costing more than the file-beside controls did. A result that contradicts any of these is the
finding.

**Shakedowns**, both on the six template questions, k = 1, the eight tool rungs, before the tag and
never published (principle 10). *The harness shakedown, Sonnet 5, 2026-11-08* — what it changed in
this section: nothing. Two harness changes landed after it and before the tag, neither prompted by it: the
pace on 7a's MCP calls and the 7b engine check, each recorded where it is described above.
48 of 48 records completed, every one on `end_turn`, no transport error, no turn-cap hit, $5.25
at list. 16 of 181 tool calls errored: nine were `search_text` called with `query` or `program`
in place of `pattern` — the library's schema refused and the model corrected on the next turn,
which is the model's behaviour against the tool as shipped and stays as it is; the rest were the
engines' (a regex group in Cypher, a SPARQL query without its PREFIX line, `fact_grid` called with
`concepts` for `elements`), as in v0.1. Two things about the first step, recorded and not acted
on (fairness rule 3): on these six questions 7a never called `get-graph-schema` or
`get-example-queries` and never fell back to Cypher — it answered from
`financial-statement-analysis`, `search-text`, `disclosures` and `information-block`; and 4c called
`describe_filing` once in six, answering the rest from `statement`, `fact_grid`, `search_text` and
`information_block` in two turns. Per-question cost on the six: 4c $0.026 · 7a $0.064 · 5c+doc $0.069
· 7b+doc $0.065 · 7c+doc $0.129 · 5c $0.170 · 7b $0.102 · 7c $0.251 — below the estimate's basis,
which stands because the Vals questions run longer than these.

*The model shakedown, Sonnet 5.5* — the same six questions on the same eight rungs, run after the
model moved and before the tag; it measures what the Sonnet 5 shakedown cannot: the token volume per
question against Sonnet 5's (the cost table's basis), the thinking blocks replayed across tool turns,
the stop reasons seen. **Result: [recorded here before the tag].**

**Publication.** `results/v0.2-sonnet-5-5/`: the records of the nine rows, judged by the v0.1 judge
(`claude-sonnet-5`, rubric decomposition + contradiction check) with the same rubrics; the 20%
human-review sample and every disagreement; a README with the per-rung tables as the Sonnet 5.5
column beside the Sonnet 5 rows, the open rows marked as such, the gate and engine-check results, the
cost actuals beside the estimate, and the expectations above scored. Tags: `protocol-v0.2` on this
section before the run; `results-v0.2` after. Transcripts gzipped, as before.
