"""The ladder as data: rungs, tiers, strata, and what each rung needs.

Every rung hands the *same filing* to the *same model* in a different representation.
``shape`` says whether the representation arrives in context or behind tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Shape(StrEnum):
  IN_CONTEXT = "in_context"
  TOOLS = "tools"


class Rung(StrEnum):
  PDF = "1"
  HTML_TEXT = "2"
  IXBRL = "3"
  XBRL_PACKAGE = "4"
  OIM_FILES = "5a"
  OIM_IN_CONTEXT = "5b"
  TAVI_JQ = "5c"
  TAVI_IN_CONTEXT = "5d"
  COMPANYFACTS = "6"
  LPG_SHAPED = "7a"
  LPG_CYPHER = "7b"
  LPG_CYPHER_MCP = (
    "7b-mcp"  # appendix ablation: 7a without its shaped tools, not a rung
  )
  RDF_SPARQL = "7c"
  RDF_IN_CONTEXT = "7d"
  # protocol v0.1.1 controls — reported beside the rungs, never as rungs
  TEXT_SEARCH = "2t"
  OIM_FILES_DOC = "5a+doc"
  TAVI_JQ_DOC = "5c+doc"
  COMPANYFACTS_DOC = "6+doc"
  COMPANYFACTS_EFTS = "6+efts"
  LPG_SHAPED_TAGGED = "7a-tagged"
  LPG_SHAPED_DOC = "7a+doc"
  LPG_CYPHER_DOC = "7b+doc"
  RDF_SPARQL_DOC = "7c+doc"


class Tier(StrEnum):
  T1_LOOKUP = "T1"
  T2_DERIVED = "T2"
  T3_CROSS_ENTITY = "T3"
  T4_CORPUS_SCREEN = "T4"


class Stratum(StrEnum):
  LOOKUP = "lookup"
  DIMENSION = "dimension"
  PERIOD = "period"
  IDENTITY = "identity"
  STRUCTURE = "structure"


@dataclass(frozen=True)
class RungSpec:
  rung: Rung
  name: str
  shape: Shape
  what_the_model_gets: str
  whose_claim: str
  v0: bool
  min_context: int  # tokens; 0 for tools-shaped rungs
  needs: tuple[str, ...]  # settings attributes that must be present to run
  control: bool = (
    False  # a v0.1.1 control: a rung plus the document, or minus part of it
  )


RUNGS: tuple[RungSpec, ...] = (
  RungSpec(
    Rung.PDF,
    "PDF",
    Shape.IN_CONTEXT,
    "the filing rendered to pages, whole, as a document block with citations",
    "the opponents' claim in its literal form",
    True,
    1_000_000,
    ("anthropic_api_key",),
  ),
  RungSpec(
    Rung.HTML_TEXT,
    "HTML text",
    Shape.IN_CONTEXT,
    "the EDGAR primary document with every tag stripped",
    "'just the document' without the rendering cost; the control for rung 3",
    True,
    200_000,
    (),
  ),
  RungSpec(
    Rung.IXBRL,
    "iXBRL",
    Shape.IN_CONTEXT,
    "the same document, styling stripped, ix: tags and ix:header kept",
    "EDGAR already ships tags inline — do they help without the linkbases?",
    True,
    1_000_000,
    (),
  ),
  RungSpec(
    Rung.XBRL_PACKAGE,
    "XBRL package",
    Shape.TOOLS,
    "instance + schema + the four linkbases on disk, via list / read-range / grep",
    "the format alone does not fit and does not compose",
    False,
    0,
    (),
  ),
  RungSpec(
    Rung.OIM_FILES,
    "OIM as published",
    Shape.TOOLS,
    "xBRL-JSON and xBRL-CSV as Arelle writes them, via file tools",
    "the standards body's fix, as shipped",
    True,
    0,
    (),
  ),
  RungSpec(
    Rung.OIM_IN_CONTEXT,
    "OIM, text blocks removed",
    Shape.IN_CONTEXT,
    "xBRL-JSON / xBRL-CSV with text-block facts removed, in context",
    "the structured facts that fit — and carry no taxonomy",
    True,
    200_000,
    (),
  ),
  RungSpec(
    Rung.TAVI_JQ,
    "Tavi, raw jq",
    Shape.TOOLS,
    "the filing as a Tavi compiled model — facts and taxonomy in one JSON document; describe + one jq tool",
    "the standards body's next serialization: JSON with the taxonomy in the same document",
    True,
    0,
    (),
  ),
  RungSpec(
    Rung.TAVI_IN_CONTEXT,
    "Tavi in context",
    Shape.IN_CONTEXT,
    "the Tavi compiled model with text-block facts removed, as text",
    "the same document handed whole, where it fits",
    False,
    1_000_000,
    (),
  ),
  RungSpec(
    Rung.COMPANYFACTS,
    "companyfacts",
    Shape.TOOLS,
    "the SEC's own structured API through three thin tools",
    "structured without the layer, with the SEC's own normalization",
    True,
    0,
    ("sec_user_agent",),
  ),
  RungSpec(
    Rung.LPG_SHAPED,
    "property graph, shaped tools",
    Shape.TOOLS,
    "the RoboSystems sec graph via its MCP tools",
    "the product: the query craft done once, on the server",
    True,
    0,
    ("robosystems_api_key",),
  ),
  RungSpec(
    Rung.LPG_CYPHER,
    "property graph, raw Cypher",
    Shape.TOOLS,
    "the filing as a LadybugDB property graph — the RoboSystems sec graph's schema, one filing, text blocks inline; describe + one read-only Cypher tool",
    "the property-graph substrate, with the taxonomy in the same graph",
    True,
    0,
    (),
  ),
  RungSpec(
    Rung.LPG_CYPHER_MCP,
    "property graph, raw Cypher over MCP (ablation: 7a without tools)",
    Shape.TOOLS,
    "the RoboSystems sec graph over MCP: schema + example queries + read-only Cypher only",
    "7a's serving with the shaped tools removed — the appendix control, not a rung",
    False,
    0,
    ("robosystems_api_key",),
  ),
  RungSpec(
    Rung.RDF_SPARQL,
    "RDF, raw SPARQL",
    Shape.TOOLS,
    "the filing as holon.jsonld in an in-memory store; describe + one SPARQL tool",
    "the RDF substrate, with the taxonomy in the same graph",
    True,
    0,
    (),
  ),
  RungSpec(
    Rung.RDF_IN_CONTEXT,
    "RDF in context",
    Shape.IN_CONTEXT,
    "the holon.jsonld as text",
    "cannot attempt until the holon is compacted",
    False,
    1_000_000,
    (),
  ),
  # ---- protocol v0.1.1 controls: the document as a constant, the form as the variable ----
  RungSpec(
    Rung.TEXT_SEARCH,
    "plain text, search tool",
    Shape.TOOLS,
    "rung 2's plain text behind search_text and read_text only",
    "the minimal retrieval baseline every form-plus-document control has to beat",
    False,
    0,
    (),
    control=True,
  ),
  RungSpec(
    Rung.OIM_FILES_DOC,
    "OIM as published + the document",
    Shape.TOOLS,
    "rung 5a's file tools plus search_text / read_text over the plain text",
    "the standard's form with the whole filing beside it",
    False,
    0,
    (),
    control=True,
  ),
  RungSpec(
    Rung.TAVI_JQ_DOC,
    "Tavi, raw jq + the document",
    Shape.TOOLS,
    "rung 5c's describe + jq plus search_text / read_text over the plain text",
    "the compiled model with the whole filing beside it",
    False,
    0,
    (),
    control=True,
  ),
  RungSpec(
    Rung.COMPANYFACTS_DOC,
    "companyfacts + the document",
    Shape.TOOLS,
    "rung 6's three tools plus search_text / read_text over the plain text",
    "the SEC's API with the whole filing beside it",
    False,
    0,
    ("sec_user_agent",),
    control=True,
  ),
  RungSpec(
    Rung.COMPANYFACTS_EFTS,
    "companyfacts + the SEC's full-text search",
    Shape.TOOLS,
    "rung 6's three tools plus search_filings: EDGAR full-text search pinned to this filing (file-level hits, no passages)",
    "the publisher's own two surfaces, and nothing else",
    False,
    0,
    ("sec_user_agent",),
    control=True,
  ),
  RungSpec(
    Rung.LPG_SHAPED_TAGGED,
    "knowledge graph, shaped tools, tagged text only",
    Shape.TOOLS,
    "rung 7a with search-documents results filtered to tagged text blocks (no narrative_section hits)",
    "the product's index without the untagged body of the filing",
    False,
    0,
    ("robosystems_api_key",),
    control=True,
  ),
  RungSpec(
    Rung.LPG_SHAPED_DOC,
    "knowledge graph, shaped tools + the document",
    Shape.TOOLS,
    "rung 7a plus search_text / read_text over the plain text",
    "the product as its public shape specifies: graph, index, and the raw filing beside",
    False,
    0,
    ("robosystems_api_key",),
    control=True,
  ),
  RungSpec(
    Rung.LPG_CYPHER_DOC,
    "property graph, raw Cypher + the document",
    Shape.TOOLS,
    "rung 7b's describe + Cypher plus search_text / read_text over the plain text",
    "the property-graph substrate with the whole filing beside it",
    False,
    0,
    (),
    control=True,
  ),
  RungSpec(
    Rung.RDF_SPARQL_DOC,
    "RDF, raw SPARQL + the document",
    Shape.TOOLS,
    "rung 7c's describe + SPARQL plus search_text / read_text over the plain text",
    "the RDF substrate with the whole filing beside it",
    False,
    0,
    (),
    control=True,
  ),
)

BY_RUNG: dict[Rung, RungSpec] = {spec.rung: spec for spec in RUNGS}
V0_RUNGS: tuple[Rung, ...] = tuple(spec.rung for spec in RUNGS if spec.v0)
CONTROLS_V0_1_1: tuple[Rung, ...] = tuple(spec.rung for spec in RUNGS if spec.control)

# Every control is one rung plus the document (``+doc``), a rung minus part of its source
# (``-tagged``), a rung plus the publisher's own search (``+efts``), or the document alone.
_BASES: dict[Rung, Rung | None] = {
  Rung.TEXT_SEARCH: None,
  Rung.OIM_FILES_DOC: Rung.OIM_FILES,
  Rung.TAVI_JQ_DOC: Rung.TAVI_JQ,
  Rung.COMPANYFACTS_DOC: Rung.COMPANYFACTS,
  Rung.COMPANYFACTS_EFTS: Rung.COMPANYFACTS,
  Rung.LPG_SHAPED_TAGGED: Rung.LPG_SHAPED,
  Rung.LPG_SHAPED_DOC: Rung.LPG_SHAPED,
  Rung.LPG_CYPHER_DOC: Rung.LPG_CYPHER,
  Rung.RDF_SPARQL_DOC: Rung.RDF_SPARQL,
}


def base_rung(rung: Rung) -> Rung | None:
  """The rung a control is built on; the rung itself when it is not a control."""
  if rung in _BASES:
    return _BASES[rung]
  return rung


def carries_document(rung: Rung) -> bool:
  return rung == Rung.TEXT_SEARCH or str(rung).endswith("+doc")


def uses_mcp(rung: Rung) -> bool:
  return base_rung(rung) in (Rung.LPG_SHAPED, Rung.LPG_CYPHER_MCP)


# Context windows we report "fits" against, in tokens.
CONTEXT_WINDOWS: tuple[tuple[str, int], ...] = (
  ("200K", 200_000),
  ("256K", 256_000),
  ("1M", 1_000_000),
)


def parse_rungs(text: str) -> list[Rung]:
  """Parse ``"1,2,7a"`` (or ``"v0"`` / ``"all"``) into rungs."""
  text = text.strip().lower()
  if text in ("v0", ""):
    return list(V0_RUNGS)
  if text == "v0.1.1":
    return list(CONTROLS_V0_1_1)
  if text == "all":
    return [spec.rung for spec in RUNGS]
  return [Rung(part.strip()) for part in text.split(",") if part.strip()]
