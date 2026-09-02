"""Runtime settings, read from the environment (``.env`` is loaded first).

Nothing here is required to materialize a filing except ``SEC_GOV_USER_AGENT``; each
rung's provider key is required only when that rung runs.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

CHROME_CANDIDATES = (
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
  "google-chrome",
  "google-chrome-stable",
  "chromium",
  "chromium-browser",
)


def find_chrome(explicit: str | None = None) -> str | None:
  """Locate a Chrome/Chromium binary for PDF rendering (rung 1)."""
  if explicit:
    return explicit
  for candidate in CHROME_CANDIDATES:
    if candidate.startswith("/"):
      if Path(candidate).exists():
        return candidate
    elif shutil.which(candidate):
      return shutil.which(candidate)
  return None


class MissingSetting(SystemExit):
  """Raised (as a clean exit) when a rung needs a key that is not configured."""

  def __init__(self, name: str, why: str) -> None:
    super().__init__(f"{name} is not set — {why}. See .env.example.")


@dataclass(frozen=True)
class Settings:
  sec_user_agent: str | None
  anthropic_api_key: str | None
  nvidia_api_key: str | None
  openrouter_api_key: str | None
  robosystems_api_key: str | None
  robosystems_api_url: str
  robosystems_graph_id: str
  data_dir: Path
  results_dir: Path
  chrome_path: str | None

  @classmethod
  def from_env(cls) -> Settings:
    # The .env beside the caller's working directory, then dotenv's own search.
    load_dotenv(Path.cwd() / ".env", override=False)
    load_dotenv(override=False)
    env = os.environ.get
    return cls(
      sec_user_agent=_clean(env("SEC_GOV_USER_AGENT")),
      anthropic_api_key=_clean(env("ANTHROPIC_API_KEY")),
      nvidia_api_key=_clean(env("NVIDIA_BUILD_API_KEY")),
      openrouter_api_key=_clean(env("OPENROUTER_API_KEY")),
      robosystems_api_key=_clean(env("ROBOSYSTEMS_API_KEY")),
      robosystems_api_url=(
        env("ROBOSYSTEMS_API_URL") or "https://api.robosystems.ai"
      ).rstrip("/"),
      robosystems_graph_id=env("ROBOSYSTEMS_GRAPH_ID") or "sec",
      data_dir=Path(env("FILING_LADDER_DATA_DIR") or "data"),
      results_dir=Path(env("FILING_LADDER_RESULTS_DIR") or "results"),
      chrome_path=find_chrome(_clean(env("CHROME_PATH"))),
    )

  def require_user_agent(self) -> str:
    if not self.sec_user_agent or self.sec_user_agent.startswith("Your Name"):
      raise MissingSetting(
        "SEC_GOV_USER_AGENT", "EDGAR refuses undeclared automated clients"
      )
    return self.sec_user_agent

  def require(self, name: str) -> str:
    value = getattr(self, name)
    if not value:
      raise MissingSetting(name.upper(), "this rung's provider needs it")
    return str(value)


def _clean(value: str | None) -> str | None:
  if value is None:
    return None
  value = value.strip().strip("'\"")
  return value or None
