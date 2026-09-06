import base64
from pathlib import Path

import pytest

from filing_ladder.config import Settings
from filing_ladder.providers import make_provider
from filing_ladder.providers.base import Attachment, CannotAttempt
from filing_ladder.providers.openai_compat import OpenAICompatProvider

PDF = Attachment("filing.pdf", "application/pdf", b"%PDF-1.4 not really")
TXT = Attachment("filing.txt", "text/plain", "Net sales 24,575")


def provider(**kw) -> OpenAICompatProvider:
  return OpenAICompatProvider(
    api_key="k", base_url="http://localhost:1/v1", model="m", **kw
  )


def test_pdf_is_refused_where_the_host_has_no_file_input():
  with pytest.raises(CannotAttempt):
    provider().start("sys", "q", [PDF], [])


def test_pdf_goes_out_as_a_file_part_where_the_host_accepts_one():
  conv = provider(accepts_pdf=True).start("sys", "q", [PDF, TXT], [])
  content = conv.messages[1]["content"]
  assert content[0] == {
    "type": "file",
    "file": {
      "filename": "filing.pdf",
      "file_data": "data:application/pdf;base64," + base64.b64encode(PDF.data).decode(),
    },
  }
  text = content[-1]
  assert text["type"] == "text"
  assert '<document name="filing.txt"' in text["text"]
  assert text["text"].endswith("q")


def test_text_only_stays_a_plain_string():
  conv = provider(accepts_pdf=True).start("sys", "q", [TXT], [])
  assert isinstance(conv.messages[1]["content"], str)


def test_reasoning_models_get_max_completion_tokens(monkeypatch):
  p = provider(max_tokens_param="max_completion_tokens", max_tokens=99)
  captured: dict = {}

  class Message:
    content = "ok"
    tool_calls = None

  class Choice:
    message = Message()
    finish_reason = "stop"

  class Usage:
    prompt_tokens = 1
    completion_tokens = 1
    prompt_tokens_details = None

  class Response:
    choices = [Choice()]
    usage = Usage()

    def model_dump(self):
      return {}

  def create(**kwargs):
    captured.update(kwargs)
    return Response()

  monkeypatch.setattr(p._client.chat.completions, "create", create)
  turn = p.step(p.start("sys", "q", [], []))
  assert turn.text == "ok"
  assert captured["max_completion_tokens"] == 99
  assert "max_tokens" not in captured


def test_routes_declare_what_the_host_accepts():
  settings = Settings(
    sec_user_agent=None,
    anthropic_api_key=None,
    openai_api_key="k",
    nvidia_api_key="k",
    openrouter_api_key="k",
    robosystems_api_key=None,
    robosystems_api_url="http://localhost:8000",
    robosystems_graph_id="sec",
    data_dir=Path("data"),
    results_dir=Path("results"),
    chrome_path=None,
  )
  openai = make_provider("openai", "m", settings)
  nvidia = make_provider("nvidia", "m", settings)
  openrouter = make_provider("openrouter", "m", settings)
  assert isinstance(openai, OpenAICompatProvider) and openai.accepts_pdf
  assert openai.max_tokens_param == "max_completion_tokens"
  assert isinstance(nvidia, OpenAICompatProvider) and not nvidia.accepts_pdf
  assert isinstance(openrouter, OpenAICompatProvider) and openrouter.accepts_pdf
  assert openrouter.extra_body["usage"] == {"include": True}
