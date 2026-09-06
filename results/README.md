# results/

Local run outputs land here and are gitignored. A published run is committed under
`results/<protocol version>-<model>/` — the report, every judgment, every transcript (gzipped),
the run parameters and a README with the tables — and the commit is tagged, so a result is cited
by an immutable commit and never re-run in place. Runs happen once (PROTOCOL principle 6).

| Run | What |
|---|---|
| [`v0.1-sonnet-5/`](v0.1-sonnet-5/README.md) | protocol v0.1, Claude Sonnet 5, 38 questions, every v0 rung, k = 3 — 2026-09-05/06 |

The same files may be mirrored as a Hugging Face dataset beside the
`sec-xbrl-knowledge-graphs` corpus dump; this directory is the record.
