# Filing Ladder — protocol

**Status: v0.1, ready to freeze — every gate cleared 2026-09-03** (question sets resolved, template
golds confirmed by hand, every filing counted, the run priced). The protocol freezes as a tagged release whose
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
and for open-weight models (OpenRouter, provider pinned, the credits charged recorded per turn). Tool errors are returned to the model for correction; rate
limits and overloads get exponential backoff with jitter.

Filing acquisition, rung materialization and the graph rungs reuse published code: the
`xbrlkit` EDGAR client and holon builder, Arelle for the OIM export, the
`sec` graph's MCP transport, and the holon viewer's parallel Cypher / SPARQL hand-offs. Nothing in
the platform is built for the benchmark.

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
The benchmark is re-run on each major model release or the page comes down. Every re-run
re-instantiates the templates on the newest filings (a new quarter of 10-Ks, public templates, new
instantiation) and re-runs the Vals public 50 as the fixed comparison point — contamination-proof
by construction.
