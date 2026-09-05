import json
import time

from filing_ladder.representations import tavi
from filing_ladder.representations.tavi import (
  TOOL_DEFS,
  describe_model,
  make_tool_runner,
  run_jq,
  strip_text_blocks,
  summary_note,
)

FY2024 = "2024-01-01T00:00:00/2025-01-01T00:00:00"


def tiny_doc() -> dict:
  """A compiled model the size of a unit test: one statement, two concepts, four facts."""
  return {
    "documentInfo": {
      "documentType": "https://xbrl.org/PWD/2026-09-01/compiled",
      "namespaces": {
        "xbrl": "https://xbrl.org/PWD/2026-09-01",
        "us-gaap": "http://fasb.org/us-gaap/2024",
        "cik": "http://www.sec.gov/CIK",
        "rpt": "https://robosystems.ai/tavi/report/0000000000-24-000001",
      },
    },
    "xbrlModel": {
      "name": "rpt:Report",
      "properties": [{"property": "xbrl:reportFilingDate", "value": "2025-02-05"}],
      "entities": [{"name": "cik:0000066740"}],
      "concepts": [
        {
          "name": "us-gaap:Revenues",
          "dataType": "xbrlr:monetary",
          "periodType": "duration",
        },
        {
          "name": "us-gaap:CostOfRevenue",
          "dataType": "xbrlr:monetary",
          "periodType": "duration",
        },
      ],
      "headings": [{"name": "us-gaap:IncomeStatementAbstract"}],
      "labels": [
        {
          "forObject": "us-gaap:Revenues",
          "labelType": "xbrl:label",
          "language": "en-US",
          "value": "Revenues",
        },
        {
          "forObject": "us-gaap:Revenues",
          "labelType": "xbrl:totalLabel",
          "language": "en-US",
          "value": "Total net sales",
        },
        {
          "forObject": "us-gaap:CostOfRevenue",
          "labelType": "xbrl:label",
          "language": "en-US",
          "value": "Cost of sales",
        },
        {
          "forObject": "rpt:group-0",
          "labelType": "xbrl:label",
          "language": "en-US",
          "value": "Consolidated Statement of Income",
        },
      ],
      "groups": [
        {
          "name": "rpt:group-0",
          "groupURI": "http://example.com/role/ConsolidatedStatementofIncome",
        }
      ],
      "groupContents": [
        {"groupName": "rpt:group-0", "forObject": "rpt:network-presentation-0"},
        {"groupName": "rpt:group-0", "forObject": "rpt:network-calculation-1"},
      ],
      "networks": [
        {
          "name": "rpt:network-presentation-0",
          "relationshipTypeName": "xbrl:parent-child",
          "relationships": [
            {
              "source": "xbrl:rootSource",
              "target": "us-gaap:IncomeStatementAbstract",
              "order": 1.0,
            },
            {
              "source": "us-gaap:IncomeStatementAbstract",
              "target": "us-gaap:Revenues",
              "order": 1.0,
              "properties": [
                {"property": "xbrl:preferredLabel", "value": "xbrl:totalLabel"}
              ],
            },
            {
              "source": "us-gaap:IncomeStatementAbstract",
              "target": "us-gaap:CostOfRevenue",
              "order": 2.0,
            },
          ],
        },
        {
          "name": "rpt:network-calculation-1",
          "relationshipTypeName": "xbrl:summation-item",
          "relationships": [
            {"source": "xbrl:rootSource", "target": "us-gaap:Revenues", "order": 1.0},
            {
              "source": "us-gaap:Revenues",
              "target": "us-gaap:CostOfRevenue",
              "order": 1.0,
              "properties": [{"property": "xbrl:weight", "value": -1.0}],
            },
          ],
        },
      ],
      "facts": [
        {
          "name": "rpt:f-0",
          "factDimensions": {
            "xbrl:concept": "us-gaap:Revenues",
            "xbrl:period": FY2024,
            "xbrl:entity": "cik:0000066740",
            "xbrl:unit": "iso4217:USD",
          },
          "factValues": [{"value": "24575000000", "decimals": -6}],
        },
        {
          "name": "rpt:f-1",
          "factDimensions": {
            "xbrl:concept": "us-gaap:Revenues",
            "xbrl:period": FY2024,
            "xbrl:entity": "cik:0000066740",
            "xbrl:unit": "iso4217:USD",
            "srt:ProductOrServiceAxis": "mmm:SafetyMember",
          },
          "factValues": [{"value": "8000000000", "decimals": -6}],
        },
        {
          "name": "rpt:f-2",
          "factDimensions": {
            "xbrl:concept": "us-gaap:RevenueRecognitionPolicyTextBlock",
            "xbrl:period": FY2024,
            "xbrl:entity": "cik:0000066740",
            "xbrl:language": "en-us",
          },
          "factValues": [
            {
              "value": "<div>Revenue is recognized when control transfers.</div>",
              "language": "en-us",
            }
          ],
        },
        {
          "name": "rpt:f-3",
          "factDimensions": {
            "xbrl:concept": "us-gaap:CostOfRevenue",
            "xbrl:period": FY2024,
            "xbrl:entity": "cik:0000066740",
            "xbrl:unit": "iso4217:USD",
          },
        },
      ],
    },
  }


def test_describe_orients_the_model():
  d = describe_model(tiny_doc())
  assert "us-gaap:Revenues" in d and '"Revenues"' in d
  assert FY2024 in d and "iso4217:USD" in d
  assert "srt:ProductOrServiceAxis: 1 members" in d
  assert "Consolidated Statement of Income" in d
  assert "Example queries" in d and ".xbrlModel.facts[]" in d
  assert "cik:0000066740" in d


def test_run_jq_consolidated_value_is_the_undimensioned_fact():
  program = """[.xbrlModel.facts[]
  | select(.factDimensions["xbrl:concept"] == "us-gaap:Revenues")
  | select([.factDimensions | keys[] | select(startswith("xbrl:") | not)] | length == 0)
  | .factValues[0].value | tonumber]"""
  out = json.loads(run_jq(tiny_doc(), program))
  assert out["result_count"] == 1 and out["results"] == [[24575000000]]


def test_run_jq_calculation_weight_and_group_label():
  weight = run_jq(
    tiny_doc(),
    '.xbrlModel.networks[] | select(.relationshipTypeName == "xbrl:summation-item") '
    '| .relationships[] | select(.source == "us-gaap:Revenues") '
    '| [.properties[] | select(.property == "xbrl:weight") | .value] | first',
  )
  assert json.loads(weight)["results"] == [-1.0]
  label = run_jq(
    tiny_doc(),
    '.xbrlModel.labels[] | select(.forObject == "rpt:group-0" and .labelType == "xbrl:label") | .value',
  )
  assert json.loads(label)["results"] == ["Consolidated Statement of Income"]


def test_run_jq_errors_and_empty_results():
  assert "jq error" in run_jq(tiny_doc(), ".foo[")
  out = json.loads(
    run_jq(
      tiny_doc(),
      '.xbrlModel.facts[] | select(.factDimensions["xbrl:concept"] == "us-gaap:Nope")',
    )
  )
  assert out["result_count"] == 0 and "empty result" in out["note"]
  out = json.loads(run_jq(tiny_doc(), '[.xbrlModel.facts[] | select(.name == "none")]'))
  assert out["results"] == [[]] and "empty result" in out["note"]


def test_run_jq_refuses_the_environment():
  assert "environment" in run_jq(tiny_doc(), "$ENV | keys")
  assert "environment" in run_jq(tiny_doc(), "env | keys")
  # a field that happens to be called env is data, not the process environment
  assert "error" not in run_jq(tiny_doc(), '.xbrlModel.env // "no such field"')


def test_run_jq_caps_and_times_out(monkeypatch):
  out = json.loads(run_jq(tiny_doc(), ".xbrlModel.labels[]", max_results=2))
  assert (
    out["result_count"] == 4
    and len(out["results"]) == 2
    and "showing 2 of 4" in out["note"]
  )

  def slow(doc, program, max_results):
    time.sleep(2)
    return "{}"

  monkeypatch.setattr(tavi, "_evaluate", slow)
  out = json.loads(run_jq(tiny_doc(), ".", timeout_s=0.3))
  assert "timed out" in out["error"]


def test_strip_text_blocks_keeps_the_numbers():
  stripped, removed = strip_text_blocks(tiny_doc())
  assert removed == 1
  names = [f["name"] for f in stripped["xbrlModel"]["facts"]]
  assert names == ["rpt:f-0", "rpt:f-1", "rpt:f-3"]
  assert len(tiny_doc()["xbrlModel"]["facts"]) == 4  # the source is untouched


def test_tool_runner_and_note():
  run = make_tool_runner(tiny_doc())
  assert {t["name"] for t in TOOL_DEFS} == {"describe_model", "run_jq"}
  assert "Example queries" in run("describe_model", {})
  assert json.loads(run("run_jq", {"program": ".xbrlModel.name"}))["results"] == [
    "rpt:Report"
  ]
  assert "unknown tool" in run("nope", {})
  assert summary_note(tiny_doc()) == "4 facts, 2 concepts, 2 networks, 4 labels"
