"""Anthropic direct — the frontier route: document blocks with citations, prompt caching.

Rung 1 hands the PDF as a ``document`` block; rungs 2, 3, 5b and 7d hand text documents the
same way, so citations (provenance) come back from every in-context rung. The last document
carries ``cache_control`` so a filing is cached across its questions; the cache write and
read tokens are reported separately so a reader can price the uncached case.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Any

import anthropic

from .base import (
  Attachment,
  CannotAttempt,
  ToolCall,
  ToolDef,
  Turn,
  Usage,
  with_backoff,
)


@dataclass
class Conversation:
  system: Any
  messages: list[dict]
  tools: list[dict]
  serialized: list[dict] = field(default_factory=list)


class AnthropicProvider:
  name = "anthropic"

  def __init__(
    self,
    api_key: str,
    model: str,
    max_tokens: int = 8192,
    temperature: float | None = None,
    betas: list[str] | None = None,
    thinking_budget: int | None = None,
    cache: bool = True,
  ) -> None:
    self.model = model
    self.max_tokens = max_tokens
    self.temperature = temperature
    self.betas = betas or []
    self.thinking_budget = thinking_budget
    self.cache = cache
    self._client = anthropic.Anthropic(api_key=api_key, max_retries=0, timeout=600)

  # ---- interface ----------------------------------------------------------------

  def start(
    self,
    system: str,
    user_text: str,
    attachments: list[Attachment],
    tools: list[ToolDef],
  ) -> Conversation:
    content: list[dict] = []
    for i, att in enumerate(attachments):
      block = _document_block(att)
      if self.cache and i == len(attachments) - 1:
        block["cache_control"] = {"type": "ephemeral"}
      content.append(block)
    content.append({"type": "text", "text": user_text})
    system_blocks: Any = [{"type": "text", "text": system}]
    if self.cache and not attachments:
      system_blocks[0]["cache_control"] = {"type": "ephemeral"}
    conv = Conversation(
      system=system_blocks,
      messages=[{"role": "user", "content": content}],
      tools=[
        {"name": t.name, "description": t.description, "input_schema": t.input_schema}
        for t in tools
      ],
    )
    conv.serialized.append({"role": "system", "content": system})
    conv.serialized.append(
      {
        "role": "user",
        "content": user_text,
        "attachments": [a.name for a in attachments],
      }
    )
    return conv

  def step(self, conversation: Conversation) -> Turn:
    kwargs: dict[str, Any] = {
      "model": self.model,
      "max_tokens": self.max_tokens,
      "system": conversation.system,
      "messages": conversation.messages,
    }
    if conversation.tools:
      kwargs["tools"] = conversation.tools
    # Claude 4.7 and later expose no sampling controls (temperature / top_p / top_k are
    # rejected), so a requested temperature is recorded on the run but never sent.
    if self.thinking_budget:
      # Claude 4.6+ takes adaptive thinking; budget_tokens is rejected on Sonnet 5 / Opus 5.
      kwargs["thinking"] = {"type": "adaptive"}
    if self.betas:
      kwargs["betas"] = self.betas
      create = self._client.beta.messages.create
    else:
      create = self._client.messages.create

    try:
      response = with_backoff(lambda: create(**kwargs), _retryable)
    except anthropic.BadRequestError as exc:
      if "prompt is too long" in str(exc).lower():
        raise CannotAttempt(f"{self.model}: {exc.message}") from exc
      raise
    except anthropic.APIStatusError as exc:
      if exc.status_code == 413:  # request exceeds the API's 32 MB cap (large PDFs)
        raise CannotAttempt(f"{self.model}: request too large — {exc.message}") from exc
      raise
    blocks = [b.model_dump() for b in response.content]
    conversation.messages.append({"role": "assistant", "content": blocks})

    text_parts: list[str] = []
    citations: list[dict] = []
    tool_calls: list[ToolCall] = []
    reasoning: list[str] = []
    for b in blocks:
      kind = b.get("type")
      if kind == "text":
        text_parts.append(b.get("text", ""))
        for c in b.get("citations") or []:
          citations.append(_citation(c))
      elif kind == "tool_use":
        tool_calls.append(ToolCall(b["id"], b["name"], dict(b.get("input") or {})))
      elif kind == "thinking":
        reasoning.append(b.get("thinking", ""))
    u = response.usage
    usage = Usage(
      input_tokens=u.input_tokens,
      output_tokens=u.output_tokens,
      cache_read_tokens=getattr(u, "cache_read_input_tokens", 0) or 0,
      cache_write_tokens=getattr(u, "cache_creation_input_tokens", 0) or 0,
    )
    text = "".join(text_parts)
    conversation.serialized.append(
      {
        "role": "assistant",
        "content": text,
        "tool_calls": [tc.__dict__ for tc in tool_calls],
        "citations": citations,
        "reasoning": "".join(reasoning) or None,
      }
    )
    return Turn(
      text,
      tool_calls,
      usage,
      str(response.stop_reason),
      citations,
      "".join(reasoning) or None,
      blocks,
    )

  def add_tool_results(
    self, conversation: Conversation, results: list[tuple[ToolCall, str, bool]]
  ) -> None:
    content = [
      {
        "type": "tool_result",
        "tool_use_id": call.id,
        "content": text,
        "is_error": is_error,
      }
      for call, text, is_error in results
    ]
    conversation.messages.append({"role": "user", "content": content})
    for call, text, is_error in results:
      conversation.serialized.append(
        {
          "role": "tool",
          "name": call.name,
          "id": call.id,
          "content": text,
          "is_error": is_error,
        }
      )

  def serialize(self, conversation: Conversation) -> list[dict]:
    return conversation.serialized

  # ---- extras -------------------------------------------------------------------

  def count_tokens(
    self, system: str, user_text: str, attachments: list[Attachment]
  ) -> int:
    conv = self.start(system, user_text, attachments, [])
    kwargs: dict[str, Any] = {
      "model": self.model,
      "system": conv.system,
      "messages": conv.messages,
    }
    if self.betas:
      kwargs["betas"] = self.betas
      return int(self._client.beta.messages.count_tokens(**kwargs).input_tokens)
    return int(self._client.messages.count_tokens(**kwargs).input_tokens)


def _document_block(att: Attachment) -> dict:
  if att.is_pdf:
    data = att.data if isinstance(att.data, bytes) else att.data.encode()
    source = {
      "type": "base64",
      "media_type": "application/pdf",
      "data": base64.b64encode(data).decode(),
    }
  else:
    text = (
      att.data if isinstance(att.data, str) else att.data.decode("utf-8", "replace")
    )
    source = {"type": "text", "media_type": "text/plain", "data": text}
  return {
    "type": "document",
    "source": source,
    "title": att.name,
    "citations": {"enabled": True},
  }


def _citation(c: dict) -> dict:
  keep = (
    "type",
    "document_index",
    "document_title",
    "start_page_number",
    "end_page_number",
    "start_char_index",
    "end_char_index",
    "cited_text",
  )
  return {k: c[k] for k in keep if k in c}


def _retryable(exc: Exception) -> bool:
  if isinstance(
    exc,
    (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.APITimeoutError),
  ):
    return True
  if isinstance(exc, anthropic.APIStatusError):
    return exc.status_code in (408, 409, 429, 500, 502, 503, 504, 529)
  return False
