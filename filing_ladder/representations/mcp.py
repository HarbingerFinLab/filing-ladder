"""Rungs 7a and 7b — the RoboSystems ``sec`` graph over MCP (Streamable HTTP, ``X-API-Key``).

The harness runs its own MCP client loop so the graph rungs run on any model with tool use.
Rung 7a exposes the server's shaped tools; rung 7b exposes only schema + example queries +
read-only Cypher, the same hand-off shape as the SPARQL rung.
"""

from __future__ import annotations

import asyncio
import json
import threading
from typing import Any

import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from ..providers.base import ToolDef
from .companyfacts import clip

SHAPED_EXCLUDE = {"list-subgraphs", "get-graph-info"}
CYPHER_ONLY = ("get-graph-schema", "get-example-queries", "read-graph-cypher")


class McpClient:
  """One live MCP session on a background event loop, callable synchronously."""

  def __init__(self, url: str, api_key: str, timeout_s: float = 120.0) -> None:
    self.url = url
    self._headers = {"X-API-Key": api_key}
    self._timeout_s = timeout_s
    self._loop = asyncio.new_event_loop()
    self._thread = threading.Thread(
      target=self._loop.run_forever, name="mcp-loop", daemon=True
    )
    self._session: ClientSession | None = None
    self._ready = threading.Event()
    self._closing: asyncio.Event | None = None
    self._failure: BaseException | None = None
    self._thread.start()
    asyncio.run_coroutine_threadsafe(self._main(), self._loop)
    self._ready.wait(timeout=timeout_s)
    if self._failure is not None:
      raise RuntimeError(f"MCP connect failed: {self._failure}")
    if self._session is None:
      raise RuntimeError("MCP connect timed out")

  async def _main(self) -> None:
    self._closing = asyncio.Event()
    try:
      async with httpx2.AsyncClient(
        headers=self._headers, timeout=httpx2.Timeout(30.0, read=self._timeout_s)
      ) as http:
        async with streamable_http_client(self.url, http_client=http) as (read, write):
          async with ClientSession(read, write) as session:
            await session.initialize()
            self._session = session
            self._ready.set()
            await self._closing.wait()
    except BaseException as exc:  # surfaced to the constructor / callers
      self._failure = exc
      self._ready.set()
    finally:
      self._session = None

  def _run(self, coro: Any) -> Any:
    return asyncio.run_coroutine_threadsafe(coro, self._loop).result(
      timeout=self._timeout_s + 30
    )

  def list_tools(self) -> list[ToolDef]:
    assert self._session is not None
    result = self._run(self._session.list_tools())
    return [
      ToolDef(
        t.name,
        t.description or "",
        dict(
          getattr(t, "input_schema", None)
          or getattr(t, "inputSchema", None)
          or {"type": "object"}
        ),
      )
      for t in result.tools
    ]

  def call(self, name: str, args: dict) -> str:
    assert self._session is not None
    result = self._run(self._session.call_tool(name, args))
    texts: list[str] = []
    for block in result.content:
      text = getattr(block, "text", None)
      texts.append(
        text
        if text is not None
        else json.dumps(getattr(block, "model_dump", lambda: str(block))())
      )
    body = "\n".join(texts)
    if getattr(result, "isError", False):
      return json.dumps({"error": body})
    return clip(body)

  def close(self) -> None:
    if self._closing is not None:
      self._loop.call_soon_threadsafe(self._closing.set)
    self._loop.call_soon_threadsafe(self._loop.stop)


def tools_for(client: McpClient, rung: str) -> list[ToolDef]:
  tools = client.list_tools()
  if rung == "7b":
    return [t for t in tools if t.name in CYPHER_ONLY]
  return [t for t in tools if t.name not in SHAPED_EXCLUDE]


def make_tool_runner(client: McpClient, allowed: list[ToolDef]):
  names = {t.name for t in allowed}

  def run(name: str, args: dict) -> str:
    if name not in names:
      return json.dumps({"error": f"tool {name} is not available on this rung"})
    return client.call(name, args)

  return run
