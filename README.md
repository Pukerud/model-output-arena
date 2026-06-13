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

Open [`compare.html`](./compare.html) in any browser (just double‑click it — **no server needed**).
It auto‑discovers every model and lets you pick any two to view **side‑by‑side**.

The model list lives in [`manifest.js`](./manifest.js).

## Models tested

See the [`providers/`](./providers) tree.

Models are either **☁️ API** (served by the vendor) or **🖥️ Local** (open weights run on your own hardware — see `runtime` in each model's `meta.json`). Comparing a quantized local model to a frontier API model is useful context, so it's labelled.

| Provider | Model | Type | Path |
|----------|-------|------|------|
| Anthropic | Claude Opus 4.8 | ☁️ API | [`providers/anthropic/claude-opus-4-8`](./providers/anthropic/claude-opus-4-8) |
| Anthropic | Claude Haiku 4.5 | ☁️ API | [`providers/anthropic/claude-haiku-4-5`](./providers/anthropic/claude-haiku-4-5) |
| Z.AI | GLM 5.2 | ☁️ API | [`providers/z-ai/glm-5.2`](./providers/z-ai/glm-5.2) |
| Z.AI | GLM 5.1 | ☁️ API | [`providers/z-ai/glm-5.1`](./providers/z-ai/glm-5.1) |
| Z.AI | GLM 5 Turbo | ☁️ API | [`providers/z-ai/glm-5-turbo`](./providers/z-ai/glm-5-turbo) |
| OpenAI | GPT-5.5 | ☁️ API | [`providers/openai/gpt-5.5`](./providers/openai/gpt-5.5) |
| Qwen | Qwen 3.6 27B Heretic v2 | 🖥️ Local | [`providers/qwen/qwen3.6-27b-heretic-v2`](./providers/qwen/qwen3.6-27b-heretic-v2) |
| Google | Gemma 4 26B A4B QAT | 🖥️ Local | [`providers/google/gemma-4-26b-a4b-qat`](./providers/google/gemma-4-26b-a4b-qat) |
| Google | Gemma 4 31B QAT | 🖥️ Local | [`providers/google/gemma-4-31b-qat`](./providers/google/gemma-4-31b-qat) |
| Anthropic | Claude Sonnet 4.6 | ☁️ API | [`providers/anthropic/claude-sonnet-4-6`](./providers/anthropic/claude-sonnet-4-6) |

## How outputs were generated

All outputs were generated inside **VS Code**. Non-Anthropic models were run via the **Pi dev harness** — a local agent loop that feeds each prompt to the target model's API and writes the raw response to disk. Anthropic models were run with **Claude Code** (the VS Code extension), acting as the agent. Same editor, same prompt, same output contract — just a different harness per provider.

No post-editing. What you see is what the model produced.

## For humans

- Want to add a model? Open an issue, or follow [`PLAN.md`](./PLAN.md) yourself / point your agent at this repo.
- Want to compare? Use [`compare.html`](./compare.html).
