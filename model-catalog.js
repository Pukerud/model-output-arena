/* Shared, dependency-free catalog helpers. Classic script also works on file://. */
(function(root){
  "use strict";
  const compare = (a,b) => a.localeCompare(b, undefined, {numeric:true, sensitivity:"base"});
  const compact = value => String(value || "").normalize("NFKC").toLocaleLowerCase().replace(/[^\p{L}\p{N}]/gu, "");
  function create(models){
    // One row per recorded submission: never collapse families or native variants.
    const entries = models.slice().sort((a,b) =>
      compare(a.provider_display || a.provider, b.provider_display || b.provider) ||
      compare(a.model_display || a.model, b.model_display || b.model));
    const groups = new Map();
    for(const model of entries){
      if(!groups.has(model.provider)) groups.set(model.provider, {
        slug:model.provider, display:model.provider_display || model.provider, count:0
      });
      groups.get(model.provider).count++;
    }
    return {models:entries, providers:[...groups.values()]};
  }
  function filter(catalog, provider, query){
    const tokens = String(query || "").normalize("NFKC").toLocaleLowerCase().match(/[\p{L}\p{N}]+/gu) || [];
    return catalog.models.filter(model => {
      if(provider && model.provider !== provider) return false;
      const text = compact([
        model.model_display, model.model, model.provider_display, model.provider,
        model.hosting === "local" ? "local" : "API",
        model.weights === "open" ? "open weights" : model.weights === "closed" ? "proprietary closed" : ""
      ].join(" "));
      return tokens.every(token => text.includes(token));
    });
  }
  const id = model => model.provider + "/" + model.model;
  // This bare link identified the existing llama.cpp submission before a second
  // run of the same model was added. Preserve that established URL explicitly;
  // other ambiguous bare slugs must not be guessed.
  const legacyBareTargets = new Map([
    ["deepseek-v4.1-flash-1017-uncensored-gsq-rco-iq2-xxs", "llamacpp/deepseek-v4.1-flash-1017-uncensored-gsq-rco-iq2-xxs"]
  ]);
  function resolve(catalog, value){
    const exact = catalog.models.find(model => id(model) === value);
    if(exact) return exact;
    // Preserve old bare-slug links, but do not guess if providers share a slug.
    const matches = catalog.models.filter(model => model.model === value ||
      (model.aliases || []).some(alias => alias === value || model.provider + "/" + alias === value));
    if(matches.length === 1) return matches[0];
    const legacyTarget = legacyBareTargets.get(value);
    return legacyTarget ? matches.find(model => id(model) === legacyTarget) : undefined;
  }
  const api = {create, filter, id, resolve};
  if(typeof module !== "undefined" && module.exports) module.exports = api;
  else root.ArenaCatalog = api;
})(typeof window !== "undefined" ? window : globalThis);
