"""Rung 1 — the filing rendered to pages.

EDGAR does not publish a PDF of a 10-K; the filer's own PDF (when one exists) is a
different document. The rung therefore renders the primary document with headless
Chrome at default scale, US Letter, no header/footer, so that every reader can reproduce
the exact bytes the model saw. The page count is recorded because providers cap pages per
request (Anthropic: 600 with a 1M-token context, 100 below that).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def render_pdf(html_path: Path, out_pdf: Path, chrome: str, timeout: int = 600) -> Path:
  out_pdf.parent.mkdir(parents=True, exist_ok=True)
  cmd = [
    chrome,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--no-pdf-header-footer",
    "--virtual-time-budget=20000",
    f"--print-to-pdf={out_pdf}",
    html_path.resolve().as_uri(),
  ]
  subprocess.run(cmd, check=True, capture_output=True, timeout=timeout)
  if not out_pdf.exists() or out_pdf.stat().st_size == 0:
    raise RuntimeError(f"Chrome produced no PDF at {out_pdf}")
  return out_pdf


def page_count(pdf: Path) -> int:
  return len(PdfReader(str(pdf)).pages)


def split_pdf(pdf: Path, max_pages: int, out_dir: Path) -> list[Path]:
  """Split into consecutive parts of at most ``max_pages`` (for providers with lower caps)."""
  reader = PdfReader(str(pdf))
  out_dir.mkdir(parents=True, exist_ok=True)
  parts: list[Path] = []
  for start in range(0, len(reader.pages), max_pages):
    writer = PdfWriter()
    for page in reader.pages[start : start + max_pages]:
      writer.add_page(page)
    part = out_dir / f"{pdf.stem}.part{len(parts) + 1:02d}.pdf"
    with part.open("wb") as fh:
      writer.write(fh)
    parts.append(part)
  return parts
