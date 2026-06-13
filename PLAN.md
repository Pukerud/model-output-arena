# PLAN.MD — Agent Playbook

> You are an AI coding agent. This repository is a **model comparison archive**. Your job: run the three
> test prompts with *your* model, save the raw output, and commit. Follow this file top to bottom.

## 0. TL;DR

1. Work out **who you are** (your provider + model).
2. Create `providers/<provider-slug>/<model-slug>/01-car-parallax/`, `02-plants-vs-zombies/`, `03-threejs-thriller/`.
3. For **each** of the three prompts in [`PROMPTS/`](./PROMPTS): generate the complete answer exactly as
   the prompt asks, save it as `output.html`, copy the prompt text into `prompt.md`, and fill in `meta.json`.
4. Append your model to [`manifest.js`](./manifest.js) so `compare.html` can show it.
5. Add your model as a row in the **Models tested** table in [`README.md`](./README.md).
6. Commit + push. Done.

**Do not modify other models' folders, `PLAN.md`, or `PROMPTS/`. The only edits you make outside your
own `providers/<provider>/<model>/` folder are: append one entry to `manifest.js` and add one row to the
Models tested table in `README.md`. Never touch other models' rows/entries.**

## 1. The goal

Identical prompts, many models, untouched outputs, side‑by‑side comparison. Never edit a prompt to suit
your model — that defeats the comparison.

## 2. Folder layout

```
providers/
└── <provider-slug>/          # e.g. z-ai, openai, anthropic, google, deepseek, xai
    └── <model-slug>/         # e.g. glm-5.2, gpt-4o, claude-3.5-sonnet
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
git add providers/ manifest.js README.md
git commit -m "Add <provider-slug>/<model-slug> outputs"
git push
```

Commit message convention: `Add <provider-slug>/<model-slug> outputs`.

## 10. After you're done

Tell the human it's safe to open [`compare.html`](./compare.html). Then stop. Don't touch other folders.
