## Summary

<!-- What this PR does and why. Ground it in the actual change, not the diff mechanics. -->

## Changes

<!-- Grouped by layer: representations/ (what a rung hands the model) · providers/ + loop.py
     (how the model is called) · judge.py + score.py (how answers are scored) · questions/
     (the sets and their gold) · PROTOCOL.md (what is measured). -->

-

## Protocol impact

<!-- Required judgment. Pick one and say why:
     - PROTOCOL: changes what is measured or how it is scored (a metric, a tolerance, a prompt,
       a fairness rule, a rung's hand-off). After a freeze this means a new protocol version
       and a re-run, not a patch to published numbers.
     - RUNG FIDELITY: changes what a rung hands the model (a strip rule, the text-block rule,
       the describe tool, a tool set). Say which rungs and re-measure the token table.
     - QUESTIONS: adds or changes a question or its gold. Gold comes from the document, read by
       a person, never from a graph — name the filing and where in it the value sits.
     - HARNESS: internal; nothing a model sees or a score depends on changes. -->

HARNESS

## Testing

<!-- Run `just test-all` (test -> lint -> typecheck) before opening. `just format` auto-writes,
     so stage what it rewrote. Name the filing(s) you materialized or ran against (accession
     numbers) and the run directory if a shakedown was involved. "Not run" is a valid answer. -->
