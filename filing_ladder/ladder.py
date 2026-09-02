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
  COMPANYFACTS = "6"
  LPG_SHAPED = "7a"
  LPG_CYPHER = "7b"
  RDF_SPARQL = "7c"
  RDF_IN_CONTEXT = "7d"


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
    False,
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
    "schema + example queries + one read-only Cypher tool on the same graph",
    "the property-graph substrate",
    True,
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
)

BY_RUNG: dict[Rung, RungSpec] = {spec.rung: spec for spec in RUNGS}
V0_RUNGS: tuple[Rung, ...] = tuple(spec.rung for spec in RUNGS if spec.v0)

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
  if text == "all":
    return [spec.rung for spec in RUNGS]
  return [Rung(part.strip()) for part in text.split(",") if part.strip()]
