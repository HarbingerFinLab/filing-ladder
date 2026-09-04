from pathlib import Path

from filing_ladder.representations import oim
from filing_ladder.representations.oim import (
  fact_stats,
  is_text_block,
  sec_transforms_plugin,
  strip_text_blocks_json,
)


def test_sec_transform_registry_is_installed():
  plugin = sec_transforms_plugin()
  assert plugin.name == "transform" and plugin.parent.name == "EDGAR"
  assert (plugin / "__init__.py").exists()


def test_arelle_loads_the_sec_transform_registry(monkeypatch, tmp_path):
  """Without ixt-sec, every SEC-formatted fact exports as null; the plugin must be on the command."""
  captured: dict = {}

  def fake_run(cmd, **kwargs):
    captured["cmd"] = cmd

    class Done:
      returncode = 0
      stderr = ""

    return Done()

  monkeypatch.setattr(oim.subprocess, "run", fake_run)
  oim._arelle(tmp_path / "filing.htm", tmp_path / "out.json")
  cmd = captured["cmd"]
  plugins = cmd[cmd.index("--plugins") + 1]
  writer, _, transforms = plugins.partition("|")
  assert writer == "saveLoadableOIM"
  assert Path(transforms) == sec_transforms_plugin()


def test_is_text_block_rules():
  assert is_text_block("us-gaap:AccountingPoliciesTextBlock", "short")
  assert is_text_block("us-gaap:EnvironmentalCostsPolicy", "<p>markup</p>")
  assert is_text_block("us-gaap:Revenues", "x" * 300)
  assert not is_text_block("us-gaap:Revenues", "24575000000")


def test_strip_json():
  doc = {
    "documentInfo": {"documentType": "https://xbrl.org/2021/xbrl-json"},
    "facts": {
      "f1": {
        "value": "1",
        "dimensions": {
          "concept": "us-gaap:Revenues",
          "entity": "cik:1",
          "period": "2024-01-01/2025-01-01",
        },
      },
      "f2": {
        "value": "<div>long</div>",
        "dimensions": {
          "concept": "us-gaap:NotesTextBlock",
          "entity": "cik:1",
          "period": "2024-01-01/2025-01-01",
        },
      },
      "f3": {
        "value": "2",
        "dimensions": {
          "concept": "us-gaap:Revenues",
          "entity": "cik:1",
          "period": "2024-01-01/2025-01-01",
          "srt:ProductOrServiceAxis": "mmm:Foo",
        },
      },
    },
  }
  stripped, removed = strip_text_blocks_json(doc)
  assert removed == 1 and set(stripped["facts"]) == {"f1", "f3"}
  assert doc["facts"]  # original untouched
  assert fact_stats(doc) == {"facts": 3, "text_blocks": 1, "dimensional": 1}
