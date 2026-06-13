# Model Output Arena

A public archive of **identical prompts run across different AI models**, so you can compare raw output quality side‑by‑side.

> ### 🤖 If you are an AI agent — go to [`PLAN.md`](./PLAN.md)
> That file is your playbook. Read it first, then execute.

---

## What this is

Every model in this repo is given the **exact same three test prompts** (see [`PROMPTS/`](./PROMPTS)).
Each model's answer is saved untouched in:

```
providers/<provider>/<model>/<test-id>/output.html
```

This gives you a permanent, dated history of how each model performs on the same tasks, and makes it
trivial to diff two models head‑to‑head.

## The tests

| # | Test | File |
|---|------|------|
| 01 | Animated car with parallax background (vanilla canvas, **no libraries**) | [`PROMPTS/01-car-parallax.md`](./PROMPTS/01-car-parallax.md) |
| 02 | Mini **Plants vs Zombies** game (single HTML, polished, menus + leaderboard) | [`PROMPTS/02-plants-vs-zombies.md`](./PROMPTS/02-plants-vs-zombies.md) |
| 03 | **Three.js** "Thriller" dance scene (cinematic) | [`PROMPTS/03-threejs-thriller.md`](./PROMPTS/03-threejs-thriller.md) |

## Compare two models

![Comparing Claude Sonnet 4.6 and GPT-5.5 on the parallax-car test in compare.html](./docs/compare-screenshot.png)

Open [`compare.html`](./compare.html) in any browser (just double‑click it — **no server needed**).
It auto‑discovers every model and lets you pick a test plus any two models to view **side‑by‑side**.

### Quick start

```bash
git clone https://github.com/Pukerud/model-output-arena
cd model-output-arena
# then open compare.html in your browser:
start compare.html      # Windows
open compare.html       # macOS
xdg-open compare.html   # Linux
```

No build, no install, no server — it's a single static page that reads [`manifest.js`](./manifest.js).

### Shareable links

The current comparison is encoded in the URL hash, so you can link straight to a matchup —
e.g. `compare.html#test=01-car-parallax&a=claude-sonnet-4-6&b=gpt-5.5` opens the view above.

## Models tested

See the [`providers/`](./providers) tree.

Two independent axes are labelled:

- **Type** — **☁️ API** (served by the vendor) or **🖥️ Local** (run on your own hardware — see `runtime` in each model's `meta.json`).
- **Weights** — **🔓 Open-weights** (weights are publicly downloadable) or **🔒 Proprietary** (closed). These don't always match Type: GLM, for instance, is open-weights but used here over an API.

| Provider | Model | Type | Weights | Path |
|----------|-------|------|---------|------|
| Anthropic | Claude Opus 4.8 | ☁️&nbsp;API | 🔒&nbsp;Proprietary | [`providers/anthropic/claude-opus-4-8`](./providers/anthropic/claude-opus-4-8) |
| Anthropic | Claude Haiku 4.5 | ☁️&nbsp;API | 🔒&nbsp;Proprietary | [`providers/anthropic/claude-haiku-4-5`](./providers/anthropic/claude-haiku-4-5) |
| Z.AI | GLM 5.2 | ☁️&nbsp;API | 🔓&nbsp;Open&#8209;weights | [`providers/z-ai/glm-5.2`](./providers/z-ai/glm-5.2) |
| Z.AI | GLM 5.1 | ☁️&nbsp;API | 🔓&nbsp;Open&#8209;weights | [`providers/z-ai/glm-5.1`](./providers/z-ai/glm-5.1) |
| Z.AI | GLM 5 Turbo | ☁️&nbsp;API | 🔒&nbsp;Proprietary | [`providers/z-ai/glm-5-turbo`](./providers/z-ai/glm-5-turbo) |
| OpenAI | GPT-5.5 | ☁️&nbsp;API | 🔒&nbsp;Proprietary | [`providers/openai/gpt-5.5`](./providers/openai/gpt-5.5) |
| Qwen | Qwen 3.6 27B Heretic v2 | 🖥️&nbsp;Local | 🔓&nbsp;Open&#8209;weights | [`providers/qwen/qwen3.6-27b-heretic-v2`](./providers/qwen/qwen3.6-27b-heretic-v2) |
| Google | Gemma 4 26B A4B QAT | 🖥️&nbsp;Local | 🔓&nbsp;Open&#8209;weights | [`providers/google/gemma-4-26b-a4b-qat`](./providers/google/gemma-4-26b-a4b-qat) |
| Google | Gemma 4 31B QAT | 🖥️&nbsp;Local | 🔓&nbsp;Open&#8209;weights | [`providers/google/gemma-4-31b-qat`](./providers/google/gemma-4-31b-qat) |
| Anthropic | Claude Sonnet 4.6 | ☁️&nbsp;API | 🔒&nbsp;Proprietary | [`providers/anthropic/claude-sonnet-4-6`](./providers/anthropic/claude-sonnet-4-6) |

## How outputs were generated

All outputs were generated inside **VS Code** — non-Anthropic models via the **Pi dev** extension, Anthropic models via **Claude Code**. Same editor, same prompts, no post-editing. What you see is what the model produced.

## For humans

- Want to add a model? Open an issue, or follow [`PLAN.md`](./PLAN.md) yourself / point your agent at this repo.
- Want to compare? Use [`compare.html`](./compare.html).
