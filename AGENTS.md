# Agent instructions

Read [PLAN.md](./PLAN.md) before adding benchmark outputs. It is the run protocol.

- For a **new benchmark run**, start whole-run measurement with `scripts/run_metrics.py start`
  before reading/generating the three prompts. Record real harness token usage and finalize
  `run.json`, then rebuild/check `run-metrics.js` before committing. See PLAN section 6a.
- Existing model folders are historical records. Never backfill guessed metrics, overwrite their
  outputs, or treat missing metrics as zero. Unavailable/partial usage must be explicit.
- Archive raw generated outputs unchanged. Preserve the exact canonical prompt bytes.
- For repository maintenance (as opposed to adding a model), follow the user's requested scope;
  the playbook's model-folder-only restriction applies to benchmark submissions, not maintenance.
- After metrics changes run `python -m unittest discover -s tests -p "test_*.py"`,
  `node --test tests/metrics-display.test.cjs`, and `python scripts/run_metrics.py check`.
  Check the actual comparison page for user-visible changes, including `file://` mode.
