"""The shared prompt skeleton and the per-rung source descriptions.

Every rung gets the same analyst role, the same output contract and the same abstention
rule; only the paragraph describing *what the model has* changes. The three raw-query rungs
(5c jq, 7b Cypher, 7c SPARQL) are worded in parallel on purpose.
"""

from __future__ import annotations

from .ladder import Rung

SKELETON = """You are a financial analyst answering ONE question about a specific SEC filing, using only the source you are given.

{source}

Rules:
- Use only the source. Never rely on memory of the company; if the source does not contain what the question needs, say so.
- Show your working briefly: which figures you used, from where, and any arithmetic.
- Every figure you report must carry its unit and scale (e.g. USD millions) and its period.
- Finish with exactly this block, and nothing after it:

ANSWER: <the final answer with units, or "Cannot determine from the provided source">
PROVENANCE: <where it comes from: page or statement line for a document; concept qname + period for structured data; the query you ran for a database>
CONFIDENCE: <high | medium | low | abstain>"""

TOOLS_WORKFLOW = """Workflow:
1. {first_step}
2. {second_step}
3. If a call errors or returns nothing useful, read the message, fix the call, and try again. You have a limited number of steps — never repeat a failing call unchanged.
4. Answer from what the tools returned. A query that returned zero rows is not evidence of a value; if you cannot retrieve the figure, abstain."""

# 7a's source paragraph, shared with 7a.1 (v0.2.1), whose workflow steps differ.
LPG_SHAPED_SOURCE = (
  "You have the RoboSystems SEC knowledge graph through its MCP tools (financial statements, fact grids, element resolution, "
  "a filing's layout, disclosures and information blocks, its whole primary document through search-text and read-text, "
  "document search and sections, and read-only Cypher). "
)

SOURCES: dict[Rung, str] = {
  Rung.PDF: "The filing is attached as a PDF. Cite page numbers.",
  Rung.HTML_TEXT: "The filing's primary document is attached as plain text (its HTML tags removed). Cite the statement or section and the line item.",
  Rung.IXBRL: (
    "The filing's primary document is attached as inline XBRL: the readable text with its ix: tags and the ix:header "
    '(contexts and units) kept, styling removed. Tagged values carry a concept name (name="…"), a contextRef and a unitRef; '
    "the ix:header resolves contexts to periods and dimensions. Cite the concept qname and the period."
  ),
  Rung.OIM_IN_CONTEXT: (
    "The filing's facts are attached as OIM (xBRL-JSON and/or xBRL-CSV) with text-block facts removed. Each fact has a concept, "
    "an entity, a period (start/end or instant), a unit, and — when it is a breakdown — dimension members; the consolidated total "
    "is the fact with no dimensions beyond concept/entity/period/unit. No labels, presentation or calculation structure is included. "
    "Cite the concept qname and the period."
  ),
  Rung.RDF_IN_CONTEXT: (
    "The filing is attached as JSON-LD (an XBRL holon): facts, elements, periods, units and dimensions in the scene graph, "
    "and the presentation / calculation / definition structures in the projection graph. Cite the concept qname and the period."
  ),
  Rung.TAVI_IN_CONTEXT: (
    "The filing is attached as a Project Tavi compiled model (one JSON document) with text-block facts removed. Under .xbrlModel, "
    "each fact's factDimensions carries xbrl:concept, xbrl:period (a dateTime interval whose end is exclusive), xbrl:entity, "
    "xbrl:unit and one further key per taxonomy axis; the consolidated total is the fact with no axis key. factValues holds the "
    "value as a string and its decimals. The taxonomy is in the same document: labels (forObject, labelType), presentation and "
    "calculation networks, groups (statements and notes) and cubes. Cite the concept qname and the period."
  ),
  Rung.XBRL_PACKAGE: (
    "The filing's XBRL package is on disk: the instance document, the schema, and the presentation, calculation, definition and "
    "label linkbases. Use the file tools to list, read ranges of, and grep the files. "
    + TOOLS_WORKFLOW.format(
      first_step="List the files and read the instance's contexts you need.",
      second_step="Grep for the concept, read the matching facts, resolve their contexts.",
    )
  ),
  Rung.OIM_FILES: (
    "The filing's facts are on disk as OIM (xBRL-JSON and xBRL-CSV as published). Use the file tools to list, read ranges of, and grep them. "
    + TOOLS_WORKFLOW.format(
      first_step="List the files and read the metadata.",
      second_step="Grep for the concept and read the matching facts.",
    )
  ),
  Rung.COMPANYFACTS: (
    "You have the SEC's companyfacts API through three tools: search_concepts, get_concept_facts and get_frame. It carries every "
    "reported value of every concept a company has filed (fiscal year, fiscal period, form, period dates, filing date), but no "
    "labels beyond the concept's, no statement structure, no dimensional breakdowns and no narrative. "
    + TOOLS_WORKFLOW.format(
      first_step="Call search_concepts to find the exact concept name.",
      second_step="Call get_concept_facts, filtered to the fiscal year and form you need; pick the value whose period matches the question.",
    )
  ),
  Rung.LPG_SHAPED: (
    LPG_SHAPED_SOURCE
    + TOOLS_WORKFLOW.format(
      first_step="Call get-example-queries and get-graph-schema first — never guess the schema.",
      second_step="Prefer the shaped tools (financial-statement-analysis, build-fact-grid, resolve-element, describe-filing, disclosures, information-block, search-text / read-text, search-documents); fall back to read-graph-cypher.",
    )
  ),
  Rung.XBRLKIT_SERVE: (
    "You have this ONE filing, parsed from its own XBRL package and held in memory, through xbrlkit's shaped tools: "
    "describe_filing, resolve_element, fact_grid, statement, calculation, disclosures and information_block, and its whole "
    "primary document through search_text and read_text. "
    + TOOLS_WORKFLOW.format(
      first_step="Call describe_filing FIRST — the entity, the periods with the keys the other tools take, the statements and disclosures by role, the axes present. Never guess a concept name or a period key.",
      second_step="Prefer the shaped tools (statement, fact_grid, calculation, resolve_element; disclosures, then information_block for one section whole); use search_text and read_text for what the narrative says.",
    )
  ),
  Rung.LPG_CYPHER: (
    "You have this ONE filing as a property graph (LadybugDB) through read-only Cypher only. "
    + TOOLS_WORKFLOW.format(
      first_step="Call describe_graph FIRST to get the node labels, relationship types and properties computed from the database, the concepts and periods present, and example queries. Never guess the schema.",
      second_step="Write a read-only Cypher query (MATCH … RETURN, always with a LIMIT, using the patterns from describe_graph) and run it with run_cypher.",
    )
  ),
  Rung.LPG_CYPHER_MCP: (
    "You have the RoboSystems SEC knowledge graph — a large, shared repository of public-company XBRL filings — through read-only Cypher only. "
    + TOOLS_WORKFLOW.format(
      first_step="Call get-graph-schema FIRST to discover node labels, relationships and properties, then get-example-queries for working patterns tuned to this graph. Never guess the schema.",
      second_step="Write a read-only Cypher query (MATCH … RETURN, always with a LIMIT, anchored on the Entity by CIK or ticker or on the Report by accession) and run it with read-graph-cypher.",
    )
  ),
  Rung.RDF_SPARQL: (
    "You have this ONE filing as RDF (an XBRL holon) through read-only SPARQL 1.1 only. "
    + TOOLS_WORKFLOW.format(
      first_step="Call describe_report FIRST to get the prefixes, the node shapes, the concepts and periods present, and example queries. Never guess the schema.",
      second_step="Write a SPARQL SELECT (always with the PREFIX lines from describe_report) and run it with run_sparql.",
    )
  ),
  Rung.TAVI_JQ: (
    "You have this ONE filing as a Project Tavi compiled model — one JSON document holding the facts and the taxonomy "
    "(labels, presentation and calculation networks, cubes) — through read-only jq only. "
    + TOOLS_WORKFLOW.format(
      first_step="Call describe_model FIRST to learn how the document is laid out, the concepts, periods, units, axes and groups present, and example programs. Never guess the shape.",
      second_step="Write a jq program (starting from .xbrlModel, using the patterns from describe_model) and run it with run_jq.",
    )
  ),
  Rung.TEXT_SEARCH: (
    "You have the filing's primary document as plain text (its HTML tags removed) through two tools only: search_text and read_text. "
    + TOOLS_WORKFLOW.format(
      first_step="Call search_text with the line item, concept or phrase the question names; read the windows around the hits.",
      second_step="Call read_text at a hit's offset to read the surrounding passage or table; search again with a narrower pattern when the first one is too broad.",
    )
  ),
}

# v0.1.1: the document beside a rung's own source, the same two tools everywhere.
DOCUMENT_BESIDE = (
  " You also have the filing's primary document as plain text (its HTML tags removed) through search_text and read_text: "
  "search for a phrase, then read the passage at an offset. Use it when the structured source does not carry what the "
  "question needs; cite the passage."
)
EFTS_BESIDE = (
  " You also have the SEC's own EDGAR full-text search over this filing through search_filings: it returns which files of "
  "the filing contain a phrase, with scores, and no text."
)
SOURCES[Rung.OIM_FILES_DOC] = SOURCES[Rung.OIM_FILES] + DOCUMENT_BESIDE
SOURCES[Rung.TAVI_JQ_DOC] = SOURCES[Rung.TAVI_JQ] + DOCUMENT_BESIDE
SOURCES[Rung.COMPANYFACTS_DOC] = SOURCES[Rung.COMPANYFACTS] + DOCUMENT_BESIDE
SOURCES[Rung.COMPANYFACTS_EFTS] = SOURCES[Rung.COMPANYFACTS] + EFTS_BESIDE
SOURCES[Rung.LPG_SHAPED_TAGGED] = SOURCES[
  Rung.LPG_SHAPED
]  # the filter is silent: same prompt
SOURCES[Rung.LPG_SHAPED_DOC] = SOURCES[Rung.LPG_SHAPED] + DOCUMENT_BESIDE
SOURCES[Rung.LPG_SHAPED_FACTS_DOC] = (
  "You have the RoboSystems SEC knowledge graph through its MCP fact tools (financial statements, fact grids, element "
  "resolution, and read-only Cypher); its document search is not available on this rung. "
  + TOOLS_WORKFLOW.format(
    first_step="Call get-example-queries and get-graph-schema first — never guess the schema.",
    second_step="Prefer the shaped tools (financial-statement-analysis, build-fact-grid, resolve-element); fall back to read-graph-cypher.",
  )
  + DOCUMENT_BESIDE
)
SOURCES[Rung.LPG_CYPHER_DOC] = SOURCES[Rung.LPG_CYPHER] + DOCUMENT_BESIDE
SOURCES[Rung.RDF_SPARQL_DOC] = SOURCES[Rung.RDF_SPARQL] + DOCUMENT_BESIDE

# Protocol v0.2.1 (§12): 4c.1's prompt is 4c's word for word — the change is in the installed
# xbrlkit; 7a.1's is 7a's source paragraph with workflow steps 1 and 2 pointed at the shaped tools.
SOURCES[Rung.XBRLKIT_SERVE_V021] = SOURCES[Rung.XBRLKIT_SERVE]
SOURCES[Rung.LPG_SHAPED_V021] = LPG_SHAPED_SOURCE + TOOLS_WORKFLOW.format(
  first_step=(
    "Start with the shaped tool the question calls for: financial-statement-analysis for a statement line; "
    "build-fact-grid or resolve-element for a concept and its values; describe-filing for the filing's Items; "
    "disclosures, then information-block, for one note read whole; search-text, then read-text, for what the "
    "narrative says; search-documents for where the corpus discusses something. Never guess a concept qname — "
    "resolve-element returns the filer's own."
  ),
  second_step=(
    "Fall back to read-graph-cypher only when the shaped tools cannot answer, and call get-example-queries "
    "and get-graph-schema before writing it — never guess the schema."
  ),
)


def system_prompt(rung: Rung) -> str:
  return SKELETON.format(source=SOURCES[rung])


def user_prompt(question: str, filing_hint: str | None) -> str:
  if filing_hint:
    return f"Filing: {filing_hint}\n\nQuestion: {question}"
  return f"Question: {question}"
