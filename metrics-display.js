/* Shared, dependency-free formatting for whole-run metrics (also testable in Node). */
(function(root) {
  function describe(run) {
    if (!run) return {text: "Whole run · Tokens: not recorded · Time: not recorded", detail: "Historical run: metrics were not collected."};
    if (run.status !== "completed") return {text: "Whole run · In progress", detail: "Final metrics are not available yet."};
    const usage = run.usage || {};
    const count = usage.total_tokens;
    let tokens = "unavailable";
    if (Number.isSafeInteger(count) && count >= 0 && usage.coverage !== "unavailable") {
      tokens = count.toLocaleString("en-US") + (usage.coverage === "complete" ? "" : " (partial)");
    } else if (usage.coverage === "partial") tokens = "unavailable (partial breakdown)";
    let duration = "unavailable";
    if (Number.isFinite(run.duration_ms) && run.duration_ms >= 0) {
      const seconds = Math.round(run.duration_ms / 100) / 10;
      duration = seconds < 60 ? seconds.toFixed(1) + " s" :
        Math.floor(seconds / 60) + "m " + (seconds % 60).toFixed(1) + "s";
    }
    const detail = ["All three prompts, including tools, retries, verification and run bookkeeping; excludes commit/push.",
      usage.source && "Token source: " + usage.source,
      usage.reason,
      Number.isSafeInteger(usage.input_tokens) && "Input (incl. cached): " + usage.input_tokens,
      Number.isSafeInteger(usage.output_tokens) && "Output (incl. reasoning): " + usage.output_tokens,
      run.started_at && "Started: " + run.started_at,
      run.completed_at && "Completed: " + run.completed_at].filter(Boolean).join("\n");
    return {text: "Whole run · Tokens: " + tokens + " · Time: " + duration, detail};
  }
  root.ArenaMetrics = {describe};
  if (typeof module !== "undefined" && module.exports) module.exports = {describe};
})(typeof window !== "undefined" ? window : globalThis);
