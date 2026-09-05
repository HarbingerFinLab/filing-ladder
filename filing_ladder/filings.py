"""Filing acquisition and materialization — one filing into every representation.

Everything lands under ``<data_dir>/<accession>/``; every step is idempotent and skipped when
its output exists, so a rung can be re-run without refetching from EDGAR.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from xbrlkit.config import Config as HolonConfig
from xbrlkit.edgar.client import EdgarClient
from xbrlkit.edgar.download import download_filing

from .config import Settings
from .ladder import CONTEXT_WINDOWS, Rung
from .representations import holon as holon_rep
from .representations import oim as oim_rep
from .representations import pdf as pdf_rep
from .representations import tavi as tavi_rep
from .representations import text as text_rep

# Anthropic's guidance: a text-dense page costs roughly 1,500-3,000 tokens (text + image).
PDF_TOKENS_PER_PAGE = 2_000

STEPS: tuple[str, ...] = (
  "package",
  "text",
  "ixbrl",
  "pdf",
  "oim",
  "tavi",
  "holon",
  "companyfacts",
)


def exported_token_counts_path() -> Path:
  return (
    Path(__file__).resolve().parent.parent / "questions" / "filing-token-counts.json"
  )


def export_token_counts(data_dir: Path) -> tuple[Path, int]:
  """Merge every ``data/<accession>/tokens.json`` into the committed per-filing counts file."""
  out = exported_token_counts_path()
  merged: dict[str, dict] = {}
  if out.exists():
    merged = json.loads(out.read_text(encoding="utf-8"))
  n = 0
  for tokens in sorted(data_dir.glob("*/tokens.json")):
    merged.setdefault(tokens.parent.name, {}).update(
      json.loads(tokens.read_text(encoding="utf-8"))
    )
    n += 1
  out.write_text(json.dumps(merged, indent=2, sort_keys=True) + "\n", encoding="utf-8")
  return out, n


@dataclass(frozen=True)
class FilingPaths:
  data_dir: Path
  accession: str

  @property
  def root(self) -> Path:
    return self.data_dir / self.accession

  @property
  def meta(self) -> Path:
    return self.root / "meta.json"

  @property
  def tokens(self) -> Path:
    """Exact token counts per materialized file, per model tokenizer (``tokens --exact``)."""
    return self.root / "tokens.json"

  def read_exact_tokens(self, model: str) -> dict[str, int]:
    """This filing's exact counts for ``model``: the local ``tokens.json`` first, else the
    committed ``questions/filing-token-counts.json`` so a replication without an API key
    makes the same fit decisions the published run made."""
    if self.tokens.exists():
      data = json.loads(self.tokens.read_text(encoding="utf-8"))
      if model in data:
        return {k: int(v) for k, v in data[model].items()}
    published = exported_token_counts_path()
    if published.exists():
      data = json.loads(published.read_text(encoding="utf-8"))
      return {k: int(v) for k, v in data.get(self.accession, {}).get(model, {}).items()}
    return {}

  def write_exact_tokens(self, model: str, counts: dict[str, int]) -> None:
    data = {}
    if self.tokens.exists():
      data = json.loads(self.tokens.read_text(encoding="utf-8"))
    data.setdefault(model, {}).update(counts)
    self.tokens.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

  @property
  def package(self) -> Path:
    return self.root / "package"

  @property
  def pdf(self) -> Path:
    return self.root / "rung1.filing.pdf"

  @property
  def text(self) -> Path:
    return self.root / "rung2.text.txt"

  @property
  def ixbrl(self) -> Path:
    return self.root / "rung3.ixbrl.htm"

  @property
  def oim_dir(self) -> Path:
    return self.root / "oim"

  @property
  def oim_json(self) -> Path:
    return self.oim_dir / "oim.json"

  @property
  def oim_facts_csv(self) -> Path:
    return self.oim_dir / "oim-facts.csv"

  @property
  def oim_json_notext(self) -> Path:
    return self.root / "rung5b.oim-notext.json"

  @property
  def oim_csv_notext(self) -> Path:
    return self.root / "rung5b.oim-notext-facts.csv"

  @property
  def tavi(self) -> Path:
    return self.root / "rung5c.tavi.json"

  @property
  def tavi_gaps(self) -> Path:
    """What the filing carries that Tavi has nowhere to put — xbrlkit writes it beside the model."""
    return self.root / "rung5c.tavi.gaps.json"

  @property
  def tavi_notext(self) -> Path:
    return self.root / "rung5d.tavi-notext.json"

  @property
  def holon(self) -> Path:
    return self.root / "rung7c.holon.jsonld"

  def read_meta(self) -> dict:
    return json.loads(self.meta.read_text())

  @property
  def primary_html(self) -> Path:
    return self.package / self.read_meta()["primary_document"]

  @property
  def instance(self) -> Path:
    """The XBRL instance for Arelle: the extracted ``*_htm.xml`` when EDGAR ships one, else the inline document."""
    candidates = sorted(self.package.glob("*_htm.xml")) or [
      p
      for p in self.package.glob("*.xml")
      if (self.package / (p.stem + ".xsd")).exists()
    ]
    return candidates[0] if candidates else self.primary_html

  def companyfacts(self, cik: str) -> Path:
    return self.data_dir / "companyfacts" / f"CIK{int(cik):010d}.json"


Log = Callable[[str], None]


def acquire(
  cik: str, accession: str, settings: Settings, log: Log = print
) -> FilingPaths:
  """Download and extract the filing's XBRL package; record what EDGAR says about it."""
  paths = FilingPaths(settings.data_dir, accession)
  if paths.meta.exists():
    log(f"package: present ({paths.package})")
    return paths
  ua = settings.require_user_agent()
  client = EdgarClient(HolonConfig(user_agent=ua))
  ref = client.get_filing_ref(cik, accession)
  info = client.company_info(cik)
  t0 = time.monotonic()
  target = download_filing(client, cik, accession, paths.package)
  meta = {
    "cik": f"{int(cik):010d}",
    "accession": accession,
    "form": ref.form,
    "filing_date": ref.filing_date,
    "primary_document": ref.primary_document or target.name,
    "is_inline": ref.is_inline,
    "entity_name": info.name,
    "ticker": info.ticker,
    "package_files": sorted(p.name for p in paths.package.iterdir()),
    "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
  }
  paths.meta.write_text(json.dumps(meta, indent=2))
  log(f"package: {len(meta['package_files'])} files in {time.monotonic() - t0:.1f}s")
  return paths


def materialize(
  cik: str,
  accession: str,
  settings: Settings,
  steps: Iterable[str] = STEPS,
  force: bool = False,
  log: Log = print,
) -> FilingPaths:
  wanted = set(steps)
  paths = acquire(cik, accession, settings, log)
  primary = paths.primary_html.read_text(encoding="utf-8", errors="replace")

  if "ixbrl" in wanted and (force or not paths.ixbrl.exists()):
    paths.ixbrl.write_text(text_rep.to_ixbrl(primary), encoding="utf-8")
    log(f"ixbrl: {paths.ixbrl.stat().st_size:,} bytes")
  if "text" in wanted and (force or not paths.text.exists()):
    paths.text.write_text(text_rep.to_plain_text(primary), encoding="utf-8")
    log(f"text: {paths.text.stat().st_size:,} bytes")
  if "pdf" in wanted and (force or not paths.pdf.exists()):
    if not settings.chrome_path:
      log("pdf: skipped — no Chrome found (set CHROME_PATH)")
    else:
      t0 = time.monotonic()
      pdf_rep.render_pdf(paths.primary_html, paths.pdf, settings.chrome_path)
      log(
        f"pdf: {paths.pdf.stat().st_size:,} bytes, {pdf_rep.page_count(paths.pdf)} pages in {time.monotonic() - t0:.0f}s"
      )
  if "oim" in wanted and (force or not paths.oim_csv_notext.exists()):
    t0 = time.monotonic()
    files = oim_rep.export_oim(paths.instance, paths.oim_dir, force=force)
    doc = json.loads(files.json.read_text())
    stripped, removed = oim_rep.strip_text_blocks_json(doc)
    paths.oim_json_notext.write_text(oim_rep.minified(stripped), encoding="utf-8")
    removed_csv = oim_rep.strip_text_blocks_csv(files.facts_csv, paths.oim_csv_notext)
    log(
      f"oim: {len(doc.get('facts', {}))} facts; {removed} text blocks removed (json), "
      f"{removed_csv} (csv) in {time.monotonic() - t0:.0f}s"
    )
  if "tavi" in wanted and (force or not paths.tavi_notext.exists()):
    t0 = time.monotonic()
    tavi_rep.build_tavi(cik, accession, paths.tavi, settings.require_user_agent())
    doc = tavi_rep.load_tavi(paths.tavi)
    stripped, removed = tavi_rep.strip_text_blocks(doc)
    paths.tavi_notext.write_text(tavi_rep.minified(stripped), encoding="utf-8")
    log(
      f"tavi: {paths.tavi.stat().st_size:,} bytes, {tavi_rep.summary_note(doc)}; "
      f"{removed} text blocks removed in {time.monotonic() - t0:.0f}s"
    )
  if "holon" in wanted and (force or not paths.holon.exists()):
    t0 = time.monotonic()
    holon_rep.build_holon(cik, accession, paths.holon, settings.require_user_agent())
    log(f"holon: {paths.holon.stat().st_size:,} bytes in {time.monotonic() - t0:.0f}s")
  if "companyfacts" in wanted and (force or not paths.companyfacts(cik).exists()):
    from .representations.companyfacts import CompanyFacts

    CompanyFacts(
      settings.require_user_agent(), paths.data_dir / "companyfacts"
    ).company_facts(cik)
    log(f"companyfacts: {paths.companyfacts(cik).stat().st_size:,} bytes")
  return paths


@dataclass(frozen=True)
class TokenRow:
  form: str
  rung: str
  n_bytes: int
  tokens: int

  def fits(self) -> str:
    for label, window in CONTEXT_WINDOWS:
      if self.tokens < window * 0.95:
        return f"{label}+"
    return "nowhere"


def token_table(paths: FilingPaths, cik: str) -> list[TokenRow]:
  """Every materialized form, with the bytes/4 estimate (``tokens --exact`` overrides it)."""
  rows: list[TokenRow] = []

  def add(form: str, rung: str, path: Path) -> None:
    if path.exists():
      size = path.stat().st_size
      rows.append(TokenRow(form, rung, size, text_rep.estimate_tokens(size)))

  if paths.pdf.exists():
    from .representations.pdf import page_count

    pages = page_count(paths.pdf)
    rows.append(
      TokenRow(
        f"PDF, rendered ({pages} pages at ~{PDF_TOKENS_PER_PAGE:,}/page)",
        Rung.PDF,
        paths.pdf.stat().st_size,
        pages * PDF_TOKENS_PER_PAGE,
      )
    )
  add("plain text", Rung.HTML_TEXT, paths.text)
  add("iXBRL, styling stripped, tags + header kept", Rung.IXBRL, paths.ixbrl)
  if paths.meta.exists():
    total = sum(p.stat().st_size for p in paths.package.iterdir() if p.is_file())
    rows.append(
      TokenRow(
        "XBRL package (every file)",
        Rung.XBRL_PACKAGE,
        total,
        text_rep.estimate_tokens(total),
      )
    )
  add("xBRL-JSON as published", Rung.OIM_FILES, paths.oim_json)
  add("xBRL-CSV facts as published", Rung.OIM_FILES, paths.oim_facts_csv)
  add("xBRL-JSON, text blocks removed", Rung.OIM_IN_CONTEXT, paths.oim_json_notext)
  add("xBRL-CSV, text blocks removed", Rung.OIM_IN_CONTEXT, paths.oim_csv_notext)
  add("Tavi compiled model", Rung.TAVI_JQ, paths.tavi)
  add("Tavi, text blocks removed", Rung.TAVI_IN_CONTEXT, paths.tavi_notext)
  add("companyfacts (whole company)", Rung.COMPANYFACTS, paths.companyfacts(cik))
  add("holon.jsonld as serialized", Rung.RDF_IN_CONTEXT, paths.holon)
  return rows
