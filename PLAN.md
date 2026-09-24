# PLAN.MD — Agent Playbook

> You are an AI coding agent. This repository is a **model comparison archive**. Your job: run the three
> test prompts with *your* model, save the raw output, and commit. Follow this file top to bottom.

## 0. TL;DR

1. Work out **who you are** (your provider + model).
2. **Before reading/generating the prompts**, start measurement (section 6a):
   `python scripts/run_metrics.py start <provider-slug>/<model-slug>`.
   Then create `01-car-parallax/`, `02-plants-vs-zombies/`, `03-threejs-thriller/` inside the new model folder.
3. For **each** of the three prompts in [`PROMPTS/`](./PROMPTS): generate the complete answer exactly as
   the prompt asks, save it as `output.html`, copy the prompt text into `prompt.md`, and fill in `meta.json`.
4. Append your model to [`manifest.js`](./manifest.js) so `compare.html` can show it.
5. Add your model as a row in the **Models tested** table in [`README.md`](./README.md).
6. Verify outputs, finish whole-run metrics, rebuild/check `run-metrics.js` (section 6a), then commit + push.

**Do not modify other models' folders, `PLAN.md`, or `PROMPTS/`. The only edits you make outside your
own `providers/<provider>/<model>/` folder are: append one entry to `manifest.js`, add one row to the
Models tested table in `README.md`, and regenerate `run-metrics.js` with the helper. Never touch other
models' rows/entries. These submission restrictions do not prohibit user-requested repository maintenance.**

## 1. The goal

Identical prompts, many models, untouched outputs, side‑by‑side comparison. Never edit a prompt to suit
your model — that defeats the comparison.

## 2. Folder layout

```
providers/
└── <provider-slug>/          # e.g. z-ai, openai, anthropic, google, deepseek, xai
    └── <model-slug>/         # e.g. glm-5.2, gpt-4o, claude-3.5-sonnet
        ├── run.json         # future runs: whole three-prompt run timing + sourced token usage
        ├── 01-car-parallax/
        │   ├── output.html   # your complete answer — untouched, exactly as produced
        │   ├── prompt.md     # the exact prompt text (verbatim copy of PROMPTS/01-car-parallax.md)
        │   └── meta.json     # who/when/what (schema below)
        ├── 02-plants-vs-zombies/
        │   ├── output.html
        │   ├── prompt.md
        │   └── meta.json
        └── 03-threejs-thriller/
            ├── output.html
            ├── prompt.md
            └── meta.json
```

## 3. Slug rules

- **Provider slug:** lowercase; dots, slashes, spaces, underscores → single dash.
  Examples: `z.ai → z-ai`, `OpenAI → openai`, `Anthropic → anthropic`, `Google → google`,
  `xAI → xai`, `DeepSeek → deepseek`, `Mistral AI → mistral-ai`.
- **Model slug:** lowercase; spaces → dashes; **keep version dots**.
  Examples: `GLM 5.2 → glm-5.2`, `GPT-4o → gpt-4o`, `Claude 3.5 Sonnet → claude-3.5-sonnet`,
  `Gemini 1.5 Pro → gemini-1.5-pro`.
- Do not invent your own structure. **If a folder for your provider/model already exists, stop and ask
  the human** rather than overwriting.

## 4. The three prompts

The exact, canonical prompt text lives in [`PROMPTS/`](./PROMPTS). Read each file there and answer it in
full. Do **not** paraphrase the prompt; copy it verbatim into each folder's `prompt.md`.

- [`PROMPTS/01-car-parallax.md`](./PROMPTS/01-car-parallax.md)
- [`PROMPTS/02-plants-vs-zombies.md`](./PROMPTS/02-plants-vs-zombies.md)
- [`PROMPTS/03-threejs-thriller.md`](./PROMPTS/03-threejs-thriller.md)

## 5. Rules for the output

- Save as **`output.html`** (HTML is the common deliverable for all three tests).
- If the prompt says "no libraries", obey it (test 01). If it permits a library via CDN
  (test 03 = Three.js), that's fine.
- Ship the **complete, runnable answer** — not a stub, not "… rest omitted". The point is to compare
  real quality.
- One self‑contained file per test. Inline all CSS/JS unless the prompt explicitly calls for a CDN.
- **Verbatim fidelity:** save exactly what you produced. Do not "tidy" or post‑edit to look better than
  your raw output.

## 6. `meta.json` schema

Create one per test:

```json
{
  "provider": "z-ai",
  "provider_display": "Z.AI",
  "model": "glm-5.2",
  "model_display": "GLM 5.2",
  "test_id": "01-car-parallax",
  "prompt_hash": "sha256:abc123...",
  "generated_at": "2026-06-13T12:00:00Z",
  "runner": "GLM-5.2 via pi agent",
  "notes": "",
  "hosting": "api",
  "weights": "open"
}
```

- `prompt_hash`: SHA‑256 of the exact prompt bytes (the contents of the matching `PROMPTS/*.md`),
  prefixed with `sha256:`. This lets us detect if a prompt drifted between runs.
  On most systems: `sha256sum PROMPTS/01-car-parallax.md`.
- `generated_at`: ISO‑8601 UTC timestamp of generation.
- `runner`: a short human‑readable string saying what generated this.
- `notes`: optional — anything notable (stylization choices, known limitations).
- `hosting`: **required.** Either `"api"` (served by the vendor over an API) or `"local"` (open weights you run
  yourself). Must match the `hosting` value in `manifest.js`; it drives the **Type** column in the README.
- `weights`: **required.** Either `"open"` (weights are publicly downloadable) or `"closed"` (proprietary).
  This is a *separate axis from `hosting`* — e.g. an open-weights model can still be used over an API.
  Must match the `weights` value in `manifest.js`; it drives the **Weights** column in the README.
- `runtime`: **required for local models, omitted for API models.** Provenance for reproducibility:

  ```json
  "runtime": {
    "weights": "open",          // "open" always, for local models
    "quant": "QAT",             // quantization, e.g. "QAT", "GGUF Q4_K_M", "FP16"; "" if unknown
    "variant": "A4B",           // optional sub-variant / fine-tune family, e.g. "Heretic v2"
    "engine": "llama.cpp",      // inference engine, e.g. "llama.cpp", "vLLM", "Ollama"
    "gpu": "RTX 4090"           // hardware it ran on
  }
  ```

  Fill what you know; leave unknowns as `""`. API/hosted models omit `runtime` entirely.

## 6a. Whole-run tokens and elapsed time (required for future runs)

One **run** is the entire three-prompt model submission, not one response or the selected test.
Use Python 3.10+ and the standard-library recorder; no service, package installation, or API key is needed.
The script records timing and validates your usage report; it does **not** call a model or discover private
harness transcripts automatically. If the harness does not expose trustworthy usage, record that honestly.

### Start before doing the work

1. Identify your provider/model and read these instructions, but do not start processing the test prompts yet.
2. Arrange usage capture in a **fresh dedicated harness session**, or record an exact cumulative baseline.
   Prefer a supervising runner that can read the worker's final usage after its completion event.
3. Run `python scripts/run_metrics.py start openai/example-model` (replace with your slugs).
   This creates the model folder and `run.json` with a UTC start timestamp. It refuses an existing folder,
   so old submissions cannot accidentally be backfilled. Create the three test subfolders afterward.
4. Generate all three outputs, write metadata, register the model, update README, and verify the submission.
   Include tools, retries, follow-ups, and any delegated generation in usage accounting. Keep their outputs raw.

### Normalize real usage, never estimate it

After the generation worker(s) complete, collect the whole-run usage from the harness/API's authoritative
usage events or cumulative counters. For cumulative counters, subtract the pre-run baseline from the final
snapshot; do not sum successive cumulative snapshots. For per-call events, sum each distinct call once,
including retries. Include all run workers; do not include an unrelated supervisor conversation.

Write a small **sanitized** report, for example `providers/openai/example-model/usage.json`:

```json
{
  "coverage": "complete",
  "source": "Harness final run usage; dedicated worker; cumulative end minus baseline",
  "reason": "",
  "input_tokens": 12000,
  "output_tokens": 8000,
  "total_tokens": 20000
}
```

The numbers above are illustrative, **not defaults**. Replace them with observed counts.

- `input_tokens`: all processed input, **including cached input** once. `output_tokens`: generated output,
  **including reasoning** once. Cache/reasoning detail counters are usually subsets: never blindly add them
  to input/output totals. If a provider excludes them, normalize using its documented semantics.
- `total_tokens`: input + output when both complete components are known. A trustworthy harness may report
  only total; then keep the two components `null`. This is usage, not price or context-window occupancy.
- `coverage: "complete"` means **all** model calls in the measured three-prompt workload are represented.
  It requires an exact total and a nonempty source. Record the source/aggregation method specifically enough
  to audit, but do not publish API keys, private transcript paths, session tokens, or full transcripts.
- `coverage: "partial"` means calls or components are missing. Keep known counts, use `null` for unknowns,
  and explain precisely what was excluded in `reason`. The UI labels partial totals, never full-run totals.
- For unavailable usage, use the `--unavailable` option below. Unknown is **null, never 0**; measured zero
  is valid. Never infer tokens from file size, character counts, model limits, or a guessed tokenizer.
- If the agent cannot observe its own final turn, use a supervising runner/final usage event. A last visible
  snapshot that omits later generation or verification calls is **partial**, not complete.

### Finish, build, verify

After **all three outputs and submission bookkeeping/verification are complete**, run:

```bash
python scripts/run_metrics.py finish openai/example-model --usage providers/openai/example-model/usage.json
# Or, when the harness exposes no trustworthy whole-run counts:
# python scripts/run_metrics.py finish openai/example-model --unavailable "This harness exposes no token usage"
python scripts/run_metrics.py build
python scripts/run_metrics.py check
```

Do not run both finish alternatives. `finish` verifies three nonempty outputs, exact prompt bytes and hashes,
and matching metadata identity; it rejects duplicate completion and invalid counts. It does not judge HTML
quality, so perform the normal output verification before finishing.

The resulting `run.json` has `schema_version: 1`, `scope: "three-prompt-run"`, all three `test_ids`,
`status: "completed"`, `started_at`, `completed_at`, `duration_ms`, and `usage`. Elapsed time is the UTC
wall-clock interval from `start` to `finish`, including tools, waits, retries, and verification, **not the sum
of parallel workers' durations**. Keep the host clock synchronized; negative/inconsistent intervals fail.
Setup before start and metric finalization/index generation, commit/push, and final reporting afterward are
outside the measured workload. Capture usage at that same workload boundary; document any mismatch as partial.

`run.json` is the source of truth. `build` creates the deterministic `run-metrics.js` snapshot used by the
static comparison page without fetch requests (including `file://`). `check` rejects stale snapshots,
unfinished runs, invalid metadata, and changed prompt artifacts. It validates only folders with `run.json`;
**historical folders remain untouched and display “not recorded.”** Do not fabricate timestamps or metrics
for an old run. A prematurely finalized run is immutable; do not quietly add further generation afterward.

## 7. Register in `manifest.js`

Append a new object to `window.ARENA.models` (do **not** delete existing entries). **Set `hosting`**
to `"api"` or `"local"` and **`weights`** to `"open"` or `"closed"` — `compare.html` shows both and the
README **Type** / **Weights** columns are derived from them.

```js
{
  provider: "openai",
  provider_display: "OpenAI",
  model: "gpt-4o",
  model_display: "GPT-4o",
  hosting: "api",
  weights: "closed",
  path: "providers/openai/gpt-4o",
  added: "2026-06-14",
  outputs: {
    "01-car-parallax":      "providers/openai/gpt-4o/01-car-parallax/output.html",
    "02-plants-vs-zombies": "providers/openai/gpt-4o/02-plants-vs-zombies/output.html",
    "03-threejs-thriller":  "providers/openai/gpt-4o/03-threejs-thriller/output.html",
  },
},
```

## 8. Update the README

The **Models tested** table in [`README.md`](./README.md) must stay in sync with `manifest.js`. After
registering your model, add one row for it (do **not** edit or remove existing rows):

```markdown
| <Provider display> | <Model display> | <Type> | <Weights> | [`providers/<provider-slug>/<model-slug>`](./providers/<provider-slug>/<model-slug>) |
```

Example:

```markdown
| OpenAI | GPT-4o | ☁️ API | 🔒 Proprietary | [`providers/openai/gpt-4o`](./providers/openai/gpt-4o) |
```

Use the same `provider_display` / `model_display` strings you put in `manifest.js` and `meta.json` so the
table matches. The table has two derived columns:
- **Type**: `☁️ API` when `hosting` is `"api"`, `🖥️ Local` when it's `"local"`.
- **Weights**: `🔓 Open-weights` when `weights` is `"open"`, `🔒 Proprietary` when it's `"closed"`.

This is the one allowed edit to `README.md`.

## 9. Commit + push

```bash
python scripts/run_metrics.py check
git add providers/<provider-slug>/<model-slug>/ manifest.js README.md run-metrics.js
git commit -m "Add <provider-slug>/<model-slug> outputs"
git push
```

Commit message convention: `Add <provider-slug>/<model-slug> outputs`.

## 10. After you're done

Tell the human it's safe to open [`compare.html`](./compare.html). Then stop. Don't touch other folders.
