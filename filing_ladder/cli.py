"""``filing-ladder`` — materialize a filing, count tokens, validate questions, run, judge, report."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from . import __version__
from .config import Settings
from .ladder import BY_RUNG, Rung, parse_rungs
from .providers.base import Attachment, ToolDef
from .representations import text as text_rep

# The query tools whose LAST result being empty, followed by a confident answer, is the
# silent-failure case (empty-result-answered). Discovery tools do not count.
QUERY_TOOLS = {
  "run_sparql",
  "read-graph-cypher",
  "get_concept_facts",
  "get_frame",
  "grep",
  "read_lines",
  "build-fact-grid",
  "financial-statement-analysis",
}


def main(argv: list[str] | None = None) -> int:
  parser = build_parser()
  args = parser.parse_args(argv)
  if not getattr(args, "func", None):
    parser.print_help()
    return 1
  return int(args.func(args) or 0)


def build_parser() -> argparse.ArgumentParser:
  p = argparse.ArgumentParser(prog="filing-ladder", description=__doc__)
  p.add_argument("--version", action="version", version=__version__)
  sub = p.add_subparsers(dest="command")

  m = sub.add_parser("materialize", help="one filing into every representation")
  m.add_argument("--cik", required=True)
  m.add_argument("--accno", required=True)
  m.add_argument("--steps", default="package,text,ixbrl,pdf,oim,holon,companyfacts")
  m.add_argument("--force", action="store_true")
  m.set_defaults(func=cmd_materialize)

  t = sub.add_parser("tokens", help="the token table for a materialized filing")
  t.add_argument("--accno", required=True)
  t.add_argument("--cik")
  t.add_argument(
    "--exact",
    action="store_true",
    help="count with the Anthropic token counter (needs ANTHROPIC_API_KEY)",
  )
  t.add_argument("--model", default="claude-sonnet-4-5")
  t.set_defaults(func=cmd_tokens)

  q = sub.add_parser(
    "questions", help="validate the question sets; print the pre-registration manifest"
  )
  q.set_defaults(func=cmd_questions)

  d = sub.add_parser(
    "describe", help="print the rung 7c describe_report for a materialized filing"
  )
  d.add_argument("--accno", required=True)
  d.set_defaults(func=cmd_describe)

  s = sub.add_parser(
    "sparql", help="run one SPARQL query against a materialized filing's holon"
  )
  s.add_argument("--accno", required=True)
  s.add_argument("--query", required=True)
  s.set_defaults(func=cmd_sparql)

  mt = sub.add_parser("mcp-tools", help="list the tools the sec graph exposes over MCP")
  mt.set_defaults(func=cmd_mcp_tools)

  r = sub.add_parser("run", help="run rungs on a question set")
  r.add_argument("--rungs", default="v0", help="v0 | all | comma list, e.g. 2,5b,7c")
  r.add_argument(
    "--provider", default="nvidia", choices=["anthropic", "nvidia", "openrouter"]
  )
  r.add_argument("--model", required=True)
  r.add_argument("--set", default="all", help="vals-public-50 | templates | all")
  r.add_argument("--ids", help="comma list of question ids")
  r.add_argument("--limit", type=int)
  r.add_argument(
    "--k", type=int, default=1, help="runs per question (the protocol uses 3)"
  )
  r.add_argument("--max-turns", type=int, default=12)
  r.add_argument("--max-tokens", type=int, default=16384)
  r.add_argument("--temperature", type=float)
  r.add_argument(
    "--context-window",
    type=int,
    help="tokens; in-context rungs above it are 'cannot attempt' (default: 1M anthropic, 200K others)",
  )
  r.add_argument("--betas", help="comma list of Anthropic beta flags")
  r.add_argument(
    "--oim-form",
    default="csv",
    choices=["csv", "json"],
    help="what rung 5b hands the model",
  )
  r.add_argument("--label", default="")
  r.add_argument("--resume", help="an existing run directory to continue")
  r.add_argument(
    "--retry-errors",
    action="store_true",
    help="with --resume: re-run records that ended in a transport error",
  )
  r.add_argument("--dry-run", action="store_true", help="plan the run, call nothing")
  r.set_defaults(func=cmd_run)

  j = sub.add_parser("judge", help="score a run's transcripts")
  j.add_argument("--run", required=True)
  j.add_argument(
    "--provider", default="anthropic", choices=["anthropic", "nvidia", "openrouter"]
  )
  j.add_argument("--model", required=True)
  j.set_defaults(func=cmd_judge)

  rp = sub.add_parser("report", help="aggregate a judged run into the results table")
  rp.add_argument("--run", required=True)
  rp.set_defaults(func=cmd_report)
  return p


# ---- materialize / tokens / questions / describe / sparql ----------------------------


def cmd_materialize(args: argparse.Namespace) -> int:
  from .filings import materialize

  settings = Settings.from_env()
  steps = [s.strip() for s in args.steps.split(",") if s.strip()]
  paths = materialize(args.cik, args.accno, settings, steps, force=args.force)
  print(f"materialized under {paths.root}")
  return 0


def cmd_tokens(args: argparse.Namespace) -> int:
  from .filings import FilingPaths, token_table

  settings = Settings.from_env()
  paths = FilingPaths(settings.data_dir, args.accno)
  if not paths.meta.exists():
    print(
      f"nothing materialized at {paths.root}; run materialize first", file=sys.stderr
    )
    return 1
  cik = args.cik or paths.read_meta()["cik"]
  rows = token_table(paths, cik)
  exact: dict[str, int] = {}
  if args.exact:
    from .providers.anthropic import AnthropicProvider

    prov = AnthropicProvider(
      settings.require("anthropic_api_key"), args.model, cache=False
    )
    for row in rows:
      path = _row_path(paths, cik, row.form)
      if path is not None and path.suffix != ".pdf" and row.tokens < 900_000:
        att = Attachment(
          path.name, "text/plain", path.read_text(encoding="utf-8", errors="replace")
        )
        try:
          exact[row.form] = prov.count_tokens("Count.", "Count.", [att])
        except Exception as exc:  # too large, or a transport error — keep the estimate
          print(f"  ({row.form}: exact count failed: {exc})", file=sys.stderr)
  print(f"{'form':<44} {'rung':<5} {'bytes':>12} {'~tokens':>10} {'exact':>10}  fits")
  for row in rows:
    ex = f"{exact[row.form]:,}" if row.form in exact else ""
    print(
      f"{row.form:<44} {row.rung:<5} {row.n_bytes:>12,} {row.tokens:>10,} {ex:>10}  {row.fits()}"
    )
  return 0


def _row_path(paths, cik: str, form: str) -> Path | None:
  mapping = {
    "PDF (rendered)": paths.pdf,
    "plain text": paths.text,
    "iXBRL, styling stripped, tags + header kept": paths.ixbrl,
    "xBRL-JSON as published": paths.oim_json,
    "xBRL-CSV facts as published": paths.oim_facts_csv,
    "xBRL-JSON, text blocks removed": paths.oim_json_notext,
    "xBRL-CSV, text blocks removed": paths.oim_csv_notext,
    "companyfacts (whole company)": paths.companyfacts(cik),
    "holon.jsonld as serialized": paths.holon,
  }
  return mapping.get(form)


def cmd_questions(args: argparse.Namespace) -> int:
  from .questions import load_all, manifest, validate

  questions = load_all()
  problems = validate(questions)
  for p in problems:
    print(f"problem: {p}", file=sys.stderr)
  print(json.dumps(manifest(), indent=2))
  return 1 if problems else 0


def cmd_describe(args: argparse.Namespace) -> int:
  from .filings import FilingPaths
  from .representations import holon as holon_rep

  settings = Settings.from_env()
  paths = FilingPaths(settings.data_dir, args.accno)
  graph = holon_rep.load_holon(paths.holon)
  print(holon_rep.describe_report(graph))
  return 0


def cmd_sparql(args: argparse.Namespace) -> int:
  from .filings import FilingPaths
  from .representations import holon as holon_rep

  settings = Settings.from_env()
  paths = FilingPaths(settings.data_dir, args.accno)
  graph = holon_rep.load_holon(paths.holon)
  query = (
    args.query
    if "PREFIX" in args.query.upper()
    else f"{holon_rep.PREFIX_BLOCK}\n{args.query}"
  )
  print(holon_rep.run_sparql(graph, query))
  return 0


def cmd_mcp_tools(args: argparse.Namespace) -> int:
  from .representations.mcp import McpClient

  settings = Settings.from_env()
  client = McpClient(_mcp_url(settings), settings.require("robosystems_api_key"))
  try:
    for tool in client.list_tools():
      print(f"- {tool.name}: {tool.description[:140]}")
  finally:
    client.close()
  return 0


def _mcp_url(settings: Settings) -> str:
  return f"{settings.robosystems_api_url}/v1/graphs/{settings.robosystems_graph_id}/mcp"


# ---- run -----------------------------------------------------------------------------


class RungContext:
  """What a rung hands the model for one filing: attachments, or tools plus a runner."""

  def __init__(
    self,
    attachments: list[Attachment] | None = None,
    tools: list[ToolDef] | None = None,
    runner=None,
    note: str = "",
    cannot_attempt: str | None = None,
  ) -> None:
    self.attachments = attachments or []
    self.tools = tools or []
    self.runner = runner
    self.note = note
    self.cannot_attempt = cannot_attempt


def cmd_run(args: argparse.Namespace) -> int:
  from .loop import run_question
  from .prompts import system_prompt, user_prompt
  from .providers import make_provider
  from .providers.base import CannotAttempt
  from .providers.pricing import cost_usd, load_prices
  from .questions import load_all
  from .results import RunDir, append_jsonl, done_keys, new_run, write_json

  settings = Settings.from_env()
  rungs = parse_rungs(args.rungs)
  questions = _select_questions(load_all(), args)
  if not questions:
    print("no questions selected", file=sys.stderr)
    return 1
  context_window = args.context_window or (
    1_000_000 if args.provider == "anthropic" else 200_000
  )
  provider_kwargs: dict[str, Any] = {
    "max_tokens": args.max_tokens,
    "temperature": args.temperature,
  }
  if args.provider == "anthropic" and args.betas:
    provider_kwargs["betas"] = [b.strip() for b in args.betas.split(",") if b.strip()]

  plan = [
    (rung, q, k) for rung in rungs for q in questions for k in range(1, args.k + 1)
  ]
  print(
    f"plan: {len(rungs)} rung(s) × {len(questions)} question(s) × k={args.k} = {len(plan)} runs on {args.provider}/{args.model}"
  )
  if args.dry_run:
    for rung, q, k in plan[:40]:
      print(
        f"  {rung:<3} {q.id:<24} run {k}  {'(unresolved filing)' if q.filing is None else q.filing.hint()}"
      )
    return 0

  provider = make_provider(args.provider, args.model, settings, **provider_kwargs)
  prices = load_prices(Path.cwd())
  run = (
    RunDir(Path(args.resume))
    if args.resume
    else new_run(
      settings.results_dir,
      args.label or f"{args.provider}-{args.model.split('/')[-1]}-{args.rungs}",
    )
  )
  done = done_keys(run, drop_errors=args.retry_errors) if args.resume else set()
  write_json(
    run.config,
    {
      "rungs": [str(r) for r in rungs],
      "provider": args.provider,
      "model": args.model,
      "k": args.k,
      "max_turns": args.max_turns,
      "max_tokens": args.max_tokens,
      "temperature": args.temperature,
      "context_window": context_window,
      "betas": provider_kwargs.get("betas"),
      "oim_form": args.oim_form,
      "question_ids": [q.id for q in questions],
      "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    },
  )
  print(f"run directory: {run.path}")

  contexts: dict[tuple[str, str], RungContext] = {}
  mcp_client = None
  try:
    for rung in rungs:
      for q in questions:
        for k in range(1, args.k + 1):
          key = (str(rung), q.id, k)
          if key in done:
            continue
          if q.filing is None:
            append_jsonl(
              run.transcripts,
              _skipped(rung, q, k, provider, "filing unresolved for this question"),
            )
            continue
          ctx_key = (str(rung), q.filing.accession)
          if ctx_key not in contexts:
            if rung in (Rung.LPG_SHAPED, Rung.LPG_CYPHER) and mcp_client is None:
              from .representations.mcp import McpClient

              mcp_client = McpClient(
                _mcp_url(settings), settings.require("robosystems_api_key")
              )
            contexts[ctx_key] = _build_context(
              rung, q.filing, settings, args.oim_form, context_window, mcp_client
            )
          ctx = contexts[ctx_key]
          system = system_prompt(rung)
          user = user_prompt(q.question, q.filing.hint())
          t0 = time.monotonic()
          if ctx.cannot_attempt:
            transcript = run_question(
              provider, str(rung), q.id, k, system, user, [], [], None, 0
            )
            transcript.cannot_attempt = ctx.cannot_attempt
            transcript.stop_reason = "cannot_attempt"
          else:
            try:
              transcript = run_question(
                provider,
                str(rung),
                q.id,
                k,
                system,
                user,
                ctx.attachments,
                ctx.tools,
                ctx.runner,
                args.max_turns,
              )
            except CannotAttempt as exc:
              transcript = run_question(
                provider, str(rung), q.id, k, system, user, [], [], None, 0
              )
              transcript.cannot_attempt = str(exc)
          record = transcript.as_dict()
          record.update(
            {
              "set": q.set,
              "tier": q.tier,
              "stratum": q.stratum,
              "category": q.category,
              "filing": q.filing.__dict__,
              "context_note": ctx.note,
              "cost_usd": cost_usd(_usage_of(record), args.model, prices),
            }
          )
          append_jsonl(run.transcripts, record)
          status = transcript.stop_reason or "ok"
          print(
            f"  {rung:<3} {q.id:<24} run {k}: {status:<14} turns={transcript.turns} tools={transcript.tool_calls} err={transcript.tool_errors} in={record['usage'].get('input_tokens', 0):,} out={record['usage'].get('output_tokens', 0):,} {time.monotonic() - t0:.0f}s"
          )
  finally:
    if mcp_client is not None:
      mcp_client.close()
  print(f"done → {run.transcripts}")
  return 0


def _select_questions(questions, args):
  if args.set != "all":
    questions = [q for q in questions if q.set == args.set]
  if args.ids:
    wanted = {i.strip() for i in args.ids.split(",")}
    questions = [q for q in questions if q.id in wanted]
  if args.limit:
    questions = questions[: args.limit]
  return questions


def _skipped(rung, q, k, provider, why: str) -> dict:
  from .loop import Transcript

  t = Transcript(
    str(rung), q.id, k, provider.name, provider.model, stop_reason="skipped", error=why
  )
  d = t.as_dict()
  d.update(
    {
      "set": q.set,
      "tier": q.tier,
      "stratum": q.stratum,
      "category": q.category,
      "filing": None,
      "cost_usd": 0.0,
    }
  )
  return d


def _usage_of(record: dict):
  from .providers.base import Usage

  u = record.get("usage") or {}
  return Usage(
    u.get("input_tokens", 0),
    u.get("output_tokens", 0),
    u.get("cache_read_tokens", 0),
    u.get("cache_write_tokens", 0),
  )


def _build_context(
  rung: Rung, filing, settings: Settings, oim_form: str, context_window: int, mcp_client
) -> RungContext:
  from .filings import FilingPaths

  paths = FilingPaths(settings.data_dir, filing.accession)
  spec = BY_RUNG[rung]

  def text_attachment(path: Path, media: str, name: str) -> RungContext:
    if not path.exists():
      return RungContext(cannot_attempt=f"{path.name} not materialized")
    size = path.stat().st_size
    tokens = text_rep.estimate_tokens(size)
    if tokens > context_window:
      return RungContext(
        cannot_attempt=f"{name}: ~{tokens:,} tokens exceeds the {context_window:,}-token window",
        note=f"{size:,} bytes",
      )
    return RungContext(
      [Attachment(name, media, path.read_text(encoding="utf-8", errors="replace"))],
      note=f"{size:,} bytes ~{tokens:,} tokens",
    )

  if rung == Rung.PDF:
    if not paths.pdf.exists():
      return RungContext(cannot_attempt="PDF not materialized (no Chrome?)")
    from .representations.pdf import page_count

    pages = page_count(paths.pdf)
    return RungContext(
      [Attachment(paths.pdf.name, "application/pdf", paths.pdf.read_bytes())],
      note=f"{pages} pages, {paths.pdf.stat().st_size:,} bytes",
    )
  if rung == Rung.HTML_TEXT:
    return text_attachment(paths.text, "text/plain", "filing.txt")
  if rung == Rung.IXBRL:
    return text_attachment(paths.ixbrl, "text/html", "filing.ixbrl.htm")
  if rung == Rung.OIM_IN_CONTEXT:
    if oim_form == "json":
      return text_attachment(
        paths.oim_json_notext, "application/json", "facts.xbrl.json"
      )
    ctx = text_attachment(paths.oim_csv_notext, "text/csv", "facts.csv")
    meta = paths.oim_dir / "oim-metadata.json"
    if ctx.attachments and meta.exists():
      ctx.attachments.insert(
        0,
        Attachment(
          "facts-metadata.json", "application/json", meta.read_text(encoding="utf-8")
        ),
      )
    return ctx
  if rung == Rung.RDF_IN_CONTEXT:
    return text_attachment(paths.holon, "application/json", "holon.jsonld")
  if rung in (Rung.XBRL_PACKAGE, Rung.OIM_FILES):
    from .representations import files as files_rep

    root = paths.package if rung == Rung.XBRL_PACKAGE else paths.oim_dir
    if not root.exists():
      return RungContext(cannot_attempt=f"{root.name} not materialized")
    tools = files_rep.FileTools(root)
    return RungContext(
      tools=files_rep.TOOL_DEFS,
      runner=files_rep.make_tool_runner(tools),
      note=f"{len(tools.list_files())} files",
    )
  if rung == Rung.COMPANYFACTS:
    from .representations import companyfacts as cf_rep

    cf = cf_rep.CompanyFacts(
      settings.require_user_agent(), settings.data_dir / "companyfacts"
    )
    return RungContext(
      tools=[ToolDef.from_dict(t) for t in cf_rep.TOOL_DEFS],
      runner=cf_rep.make_tool_runner(cf),
    )
  if rung in (Rung.LPG_SHAPED, Rung.LPG_CYPHER):
    from .representations import mcp as mcp_rep

    assert mcp_client is not None
    tools = mcp_rep.tools_for(mcp_client, str(rung))
    return RungContext(
      tools=tools,
      runner=mcp_rep.make_tool_runner(mcp_client, tools),
      note=", ".join(t.name for t in tools),
    )
  if rung == Rung.RDF_SPARQL:
    from .representations import holon as holon_rep

    if not paths.holon.exists():
      return RungContext(cannot_attempt="holon not materialized")
    graph = holon_rep.load_holon(paths.holon)
    return RungContext(
      tools=[ToolDef.from_dict(t) for t in holon_rep.TOOL_DEFS],
      runner=holon_rep.make_tool_runner(graph),
      note=f"{len(graph):,} triples",
    )
  raise SystemExit(f"rung {rung} ({spec.name}, {spec.shape}) has no context builder")


# ---- judge / report ---------------------------------------------------------------------


def cmd_judge(args: argparse.Namespace) -> int:
  from .judge import judge_rubric, parse_final, score_numeric
  from .providers import make_provider
  from .questions import load_all
  from .results import RunDir, append_jsonl, read_jsonl

  settings = Settings.from_env()
  run = RunDir(Path(args.run))
  questions = {q.id: q for q in load_all()}
  judged = {
    (j["rung"], j["question_id"], int(j["run_index"]))
    for j in read_jsonl(run.judgments)
  }
  judge = None
  for t in read_jsonl(run.transcripts):
    key = (t["rung"], t["question_id"], int(t["run_index"]))
    if key in judged:
      continue
    q = questions.get(t["question_id"])
    if q is None:
      continue
    final = parse_final(t.get("final_text") or "")
    query_events = [e for e in t.get("tool_events", []) if e.get("name") in QUERY_TOOLS]
    empty_answered = (
      bool(query_events)
      and bool(query_events[-1].get("empty_result"))
      and not final.abstained
      and bool(final.answer)
    )
    out: dict[str, Any] = {
      "rung": t["rung"],
      "question_id": t["question_id"],
      "run_index": t["run_index"],
      "answer": final.answer,
      "provenance": final.provenance,
      "confidence": final.confidence,
      "abstained": final.abstained,
      "provenance_present": bool(final.provenance.strip())
      and final.provenance.lower() not in ("none", "n/a", "-"),
      "empty_result_answered": empty_answered,
      "cannot_attempt": bool(t.get("cannot_attempt")),
      "error": bool(t.get("error")) and t.get("stop_reason") != "skipped",
      "skipped": t.get("stop_reason") == "skipped",
    }
    if (
      t.get("cannot_attempt")
      or t.get("error")
      or not (t.get("final_text") or "").strip()
    ):
      out.update({"correct": False, "contradiction": False, "extracted": None})
    elif q.gold_type == "numeric":
      s = score_numeric(t["final_text"], q.gold, q.gold_scale)
      out.update(
        {
          "correct": bool(s.get("correct")),
          "abstained": bool(s.get("abstained")),
          "contradiction": (not s.get("correct"))
          and (not s.get("abstained"))
          and s.get("extracted") is not None,
          "extracted": s.get("extracted"),
          "gold": s.get("gold"),
        }
      )
    else:
      if judge is None:
        judge = make_provider(
          args.provider, args.model, settings, temperature=0.0, max_tokens=4096
        )
      j = judge_rubric(judge, q.question, q.gold, q.rubric, t["final_text"])
      points = j.get("points") or []
      met = sum(1 for p in points if p.get("met"))
      out.update(
        {
          "correct": bool(points) and met == len(points) and not j.get("contradiction"),
          "points_met": met,
          "points_total": len(points),
          "contradiction": bool(j.get("contradiction")),
          "abstained": out["abstained"] or bool(j.get("abstained")),
          "provenance_present": out["provenance_present"]
          or bool(j.get("provenance_present")),
          "judge": j,
        }
      )
    append_jsonl(run.judgments, out)
    print(
      f"  {out['rung']:<3} {out['question_id']:<24} run {out['run_index']}: {'correct' if out['correct'] else ('abstain' if out['abstained'] else 'wrong')}"
    )
  return 0


def cmd_report(args: argparse.Namespace) -> int:
  from .results import RunDir, iter_pairs, read_jsonl, write_json
  from .score import Record, aggregate, markdown_table

  run = RunDir(Path(args.run))
  records: list[Record] = []
  for t, j in iter_pairs(read_jsonl(run.transcripts), read_jsonl(run.judgments)):
    if j is None or j.get("skipped"):
      continue
    u = t.get("usage") or {}
    records.append(
      Record(
        rung=t["rung"],
        question_id=t["question_id"],
        run_index=int(t["run_index"]),
        tier=t.get("tier", "?"),
        stratum=t.get("stratum", "?"),
        category=t.get("category", ""),
        correct=bool(j.get("correct")),
        abstained=bool(j.get("abstained")),
        contradiction=bool(j.get("contradiction")),
        cannot_attempt=bool(j.get("cannot_attempt")),
        error=bool(j.get("error")),
        provenance_present=bool(j.get("provenance_present")),
        empty_result_answered=bool(j.get("empty_result_answered")),
        cost_usd=t.get("cost_usd"),
        input_tokens=int(u.get("input_tokens", 0)),
        output_tokens=int(u.get("output_tokens", 0)),
        cache_read_tokens=int(u.get("cache_read_tokens", 0)),
        cache_write_tokens=int(u.get("cache_write_tokens", 0)),
        turns=int(t.get("turns", 0)),
        tool_calls=int(t.get("tool_calls", 0)),
        tool_errors=int(t.get("tool_errors", 0)),
        wall_s=float(t.get("wall_s", 0.0)),
        extracted=j.get("extracted"),
      )
    )
  by_stratum = aggregate(records, by_stratum=True)
  by_rung = aggregate(records, by_stratum=False)
  write_json(
    run.summary_json,
    {
      "by_rung_tier": [c.__dict__ for c in by_rung],
      "by_rung_tier_stratum": [c.__dict__ for c in by_stratum],
    },
  )
  md = f"# {run.path.name}\n\n## By rung × tier\n\n{markdown_table(by_rung)}\n\n## By rung × tier × stratum\n\n{markdown_table(by_stratum)}\n"
  run.summary_md.write_text(md, encoding="utf-8")
  print(md)
  return 0


if __name__ == "__main__":  # pragma: no cover
  sys.exit(main())
