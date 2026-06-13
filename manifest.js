/*
 * Model Output Arena — manifest.
 * Loaded by compare.html via a <script> tag (works on file:// — no server needed).
 *
 * ADDING A MODEL: append a new entry to `models` below. Keep the same `outputs` keys
 * (the test ids). See PLAN.md for the full slug rules.
 */
window.ARENA = {
  tests: [
    { id: "01-car-parallax",      title: "01 · Animated Car — Parallax (vanilla canvas)" },
    { id: "02-plants-vs-zombies", title: "02 · Mini Plants vs Zombies (single HTML)" },
    { id: "03-threejs-thriller",  title: "03 · Three.js \"Thriller\" Dance Scene" },
  ],
  models: [
    {
      provider: "anthropic",
      provider_display: "Anthropic",
      model: "claude-opus-4-8",
      model_display: "Claude Opus 4.8",
      path: "providers/anthropic/claude-opus-4-8",
      added: "2026-06-13",
      outputs: {
        "01-car-parallax":      "providers/anthropic/claude-opus-4-8/01-car-parallax/output.html",
        "02-plants-vs-zombies": "providers/anthropic/claude-opus-4-8/02-plants-vs-zombies/output.html",
        "03-threejs-thriller":  "providers/anthropic/claude-opus-4-8/03-threejs-thriller/output.html",
      },
    },
    {
      provider: "z-ai",
      provider_display: "Z.AI",
      model: "glm-5.2",
      model_display: "GLM 5.2",
      path: "providers/z-ai/glm-5.2",
      added: "2026-06-13",
      outputs: {
        "01-car-parallax":      "providers/z-ai/glm-5.2/01-car-parallax/output.html",
        "02-plants-vs-zombies": "providers/z-ai/glm-5.2/02-plants-vs-zombies/output.html",
        "03-threejs-thriller":  "providers/z-ai/glm-5.2/03-threejs-thriller/output.html",
      },
    },
    {
      provider: "z-ai",
      provider_display: "Z.AI",
      model: "glm-5.1",
      model_display: "GLM 5.1",
      path: "providers/z-ai/glm-5.1",
      added: "2026-06-13",
      outputs: {
        "01-car-parallax":      "providers/z-ai/glm-5.1/01-car-parallax/output.html",
        "02-plants-vs-zombies": "providers/z-ai/glm-5.1/02-plants-vs-zombies/output.html",
        "03-threejs-thriller":  "providers/z-ai/glm-5.1/03-threejs-thriller/output.html",
      },
    },
  ],
};
