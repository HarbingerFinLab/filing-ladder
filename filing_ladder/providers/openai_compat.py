"""OpenAI-compatible chat completions — OpenAI direct, NVIDIA Build (shakedown), OpenRouter.

Text attachments are inlined into the user message inside ``<document>`` tags. A PDF goes out
as a ``file`` content part where the host accepts one (OpenAI, OpenRouter) and raises
``CannotAttempt`` where it does not (NVIDIA Build). Reasoning models return
``reasoning_content``; it is kept out of the answer and recorded on the turn.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from typing import Any

import openai

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
  messages: list[dict]
  tools: list[dict]
  serialized: list[dict] = field(default_factory=list)


class OpenAICompatProvider:
  def __init__(
    self,
    api_key: str,
    base_url: str,
    model: str,
    name: str = "openai-compatible",
    max_tokens: int = 16384,
    temperature: float | None = None,
    extra_body: dict | None = None,
    provider_order: list[str] | None = None,
    accepts_pdf: bool = False,
    max_tokens_param: str = "max_tokens",
  ) -> None:
    self.name = name
    self.model = model
    self.max_tokens = max_tokens
    self.max_tokens_param = (
      max_tokens_param  # reasoning models take max_completion_tokens
    )
    self.accepts_pdf = accepts_pdf
    self.temperature = temperature
    self.extra_body = dict(extra_body or {})
    if provider_order:  # OpenRouter provider pinning for a pre-registered protocol
      self.extra_body["provider"] = {"order": provider_order, "allow_fallbacks": False}
    self._client = openai.OpenAI(
      api_key=api_key, base_url=base_url, max_retries=0, timeout=600
    )

  def start(
    self,
    system: str,
    user_text: str,
    attachments: list[Attachment],
    tools: list[ToolDef],
  ) -> Conversation:
    files: list[dict] = []
    parts: list[str] = []
    for att in attachments:
      if att.is_pdf:
        if not self.accepts_pdf:
          raise CannotAttempt(f"{self.name} route does not accept PDF input")
        raw = att.data if isinstance(att.data, bytes) else att.data.encode()
        files.append(
          {
            "type": "file",
            "file": {
              "filename": att.name,
              "file_data": "data:application/pdf;base64,"
              + base64.b64encode(raw).decode(),
            },
          }
        )
        continue
      text = (
        att.data if isinstance(att.data, str) else att.data.decode("utf-8", "replace")
      )
      parts.append(
        f'<document name="{att.name}" type="{att.media_type}">\n{text}\n</document>'
      )
    parts.append(user_text)
    text = "\n\n".join(parts)
    content: str | list[dict] = (
      [*files, {"type": "text", "text": text}] if files else text
    )
    conv = Conversation(
      messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": content},
      ],
      tools=[
        {
          "type": "function",
          "function": {
            "name": t.name,
            "description": t.description,
            "parameters": t.input_schema,
          },
        }
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
      "messages": conversation.messages,
      self.max_tokens_param: self.max_tokens,
    }
    if conversation.tools:
      kwargs["tools"] = conversation.tools
    if self.temperature is not None:
      kwargs["temperature"] = self.temperature
    if self.extra_body:
      kwargs["extra_body"] = self.extra_body

    response = with_backoff(
      lambda: self._client.chat.completions.create(**kwargs), _retryable
    )
    choice = response.choices[0]
    message = choice.message
    text = message.content or ""
    reasoning = getattr(message, "reasoning_content", None) or getattr(
      message, "reasoning", None
    )
    tool_calls: list[ToolCall] = []
    assistant: dict[str, Any] = {"role": "assistant", "content": text or None}
    if message.tool_calls:
      assistant["tool_calls"] = []
      for tc in message.tool_calls:
        try:
          args = json.loads(tc.function.arguments or "{}")
        except json.JSONDecodeError:
          args = {"_malformed_arguments": tc.function.arguments}
        tool_calls.append(ToolCall(tc.id, tc.function.name, args))
        assistant["tool_calls"].append(
          {
            "id": tc.id,
            "type": "function",
            "function": {
              "name": tc.function.name,
              "arguments": tc.function.arguments or "{}",
            },
          }
        )
    conversation.messages.append(assistant)
    u = response.usage
    cached = 0
    details = getattr(u, "prompt_tokens_details", None) if u else None
    if details is not None:
      cached = getattr(details, "cached_tokens", 0) or 0
    usage = Usage(
      input_tokens=(u.prompt_tokens if u else 0),
      output_tokens=(u.completion_tokens if u else 0),
      cache_read_tokens=cached,
    )
    conversation.serialized.append(
      {
        "role": "assistant",
        "content": text,
        "tool_calls": [tc.__dict__ for tc in tool_calls],
        "reasoning": reasoning,
      }
    )
    return Turn(
      text,
      tool_calls,
      usage,
      str(choice.finish_reason),
      [],
      reasoning,
      response.model_dump(),
    )

  def add_tool_results(
    self, conversation: Conversation, results: list[tuple[ToolCall, str, bool]]
  ) -> None:
    for call, text, is_error in results:
      conversation.messages.append(
        {"role": "tool", "tool_call_id": call.id, "content": text}
      )
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


def _retryable(exc: Exception) -> bool:
  if isinstance(
    exc, (openai.RateLimitError, openai.APIConnectionError, openai.APITimeoutError)
  ):
    return True
  if isinstance(exc, openai.APIStatusError):
    return exc.status_code in (408, 409, 429, 500, 502, 503, 504)
  return False
