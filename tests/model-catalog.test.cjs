const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const Catalog = require('../model-catalog.js');
const root = path.join(__dirname, '..');
const context = {window:{}};
vm.runInNewContext(fs.readFileSync(path.join(root,'manifest.js'),'utf8'),context);
const arena = context.window.ARENA;
const catalog = Catalog.create(arena.models);
const testIds = ['01-car-parallax','02-plants-vs-zombies','03-threejs-thriller'];

test('exactly three valid benchmark tests, not accidental model entries', () => {
  assert.deepEqual(Array.from(arena.tests, test => test.id),testIds);
  assert.ok(arena.tests.every(test => test.title && !test.provider && !test.outputs));
});
test('submission identities and paths are unique and canonical', () => {
  assert.equal(new Set(arena.models.map(Catalog.id)).size,arena.models.length);
  assert.equal(new Set(arena.models.map(model => model.path)).size,arena.models.length);
  for(const model of arena.models){
    assert.equal(model.path,'providers/' + Catalog.id(model));
    assert.ok(model.model_display && model.provider_display);
  }
});
test('all complete archived submissions are registered exactly once', () => {
  const archived = [];
  const providersRoot = path.join(root,'providers');
  for(const provider of fs.readdirSync(providersRoot,{withFileTypes:true}).filter(entry => entry.isDirectory())){
    for(const model of fs.readdirSync(path.join(providersRoot,provider.name),{withFileTypes:true}).filter(entry => entry.isDirectory())){
      if(testIds.every(id => fs.existsSync(path.join(providersRoot,provider.name,model.name,id,'output.html'))))
        archived.push('providers/' + provider.name + '/' + model.name);
    }
  }
  assert.deepEqual(Array.from(arena.models,model => model.path).sort(),archived.sort());
});
test('all registered outputs and metadata exist and match canonical identities', () => {
  for(const model of arena.models){
    for(const id of testIds){
      assert.equal(model.outputs[id],model.path + '/' + id + '/output.html');
      assert.ok(fs.statSync(path.join(root,model.outputs[id])).size > 0);
      const metadata = JSON.parse(fs.readFileSync(path.join(root,model.path,id,'meta.json'),'utf8'));
      assert.equal(metadata.provider,model.provider);
      assert.equal(metadata.model,model.model);
    }
  }
});
test('every provider count equals its individually selectable rows', () => {
  assert.equal(catalog.models.length,arena.models.length);
  for(const provider of catalog.providers){
    const rows = Catalog.filter(catalog,provider.slug,'');
    assert.equal(rows.length,provider.count);
    assert.equal(new Set(rows.map(Catalog.id)).size,provider.count);
  }
  assert.equal(Catalog.filter(catalog,'local','').length,arena.models.filter(model => model.provider === 'local').length);
  assert.ok(Catalog.filter(catalog,'local','').length >= 25);
});
test('families, parentheses and native variants never collapse model rows', () => {
  const local = Catalog.filter(catalog,'local','');
  const names = local.map(model => model.model_display);
  for(const slug of ['qwen3.8-27b','qwen3.8-27b-native','qwen3.8-27b-heretic','qwen3.8-27b-heretic-native'])
    assert.equal(local.filter(model => model.model === slug).length,1);
  assert.equal(new Set(names).size,names.length);
  assert.ok(names.every(name => name !== 'Standard'));
});
test('search tolerates spacing, dots, hyphens, quantization and case', () => {
  assert.equal(Catalog.filter(catalog,'local','ORCA q4_k_s')[0].model,'qwen3.8-flash-next-orca-q4-k-s');
  assert.ok(Catalog.filter(catalog,'local','qwen 3.8 heretic').length >= 2);
  assert.ok(Catalog.filter(catalog,'local','qwen3.8').length > 4);
  assert.ok(Catalog.filter(catalog,'','native harness').length > 1);
  assert.equal(Catalog.filter(catalog,'local','no-such-model-xyz').length,0);
  assert.ok(Catalog.filter(catalog,'','').some(model => model.provider === 'llamacpp'));
});
test('provider-qualified links resolve every exact submission and legacy links still work', () => {
  for(const model of arena.models){
    assert.equal(Catalog.resolve(catalog,Catalog.id(model)),model);
    if(arena.models.filter(candidate => candidate.model === model.model).length === 1)
      assert.equal(Catalog.resolve(catalog,model.model),model);
  }
  const repeated = 'deepseek-v4.1-flash-1017-uncensored-gsq-rco-iq2-xxs';
  assert.equal(Catalog.resolve(catalog,repeated).provider,'llamacpp');
  assert.equal(Catalog.resolve(catalog,'local/' + repeated).provider,'local');
  assert.equal(Catalog.resolve(catalog,'llamacpp/' + repeated).provider,'llamacpp');
  assert.equal(Catalog.resolve(catalog,'laguna-s-2.1 i3XSS').model,'laguna-s-2.1');
  assert.equal(Catalog.resolve(catalog,'local/laguna-s-2.1 i3XSS').model,'laguna-s-2.1');
  assert.equal(Catalog.resolve(catalog,'nonexistent'),undefined);
});
test('future providers sharing a bare slug cannot select the wrong model', () => {
  const sample = Catalog.create([{provider:'one',model:'same'},{provider:'two',model:'same'}]);
  assert.equal(Catalog.resolve(sample,'same'),undefined);
  assert.equal(Catalog.resolve(sample,'one/same').provider,'one');
  assert.equal(Catalog.resolve(sample,'two/same').provider,'two');
});
test('catalog does not mutate historical manifest records or add inferred family labels', () => {
  const before = JSON.stringify(arena.models);
  Catalog.create(arena.models);
  Catalog.filter(catalog,'local','qwen');
  assert.equal(JSON.stringify(arena.models),before);
  assert.ok(arena.models.every(model => !('family' in model) && !('variant' in model)));
});
test('restored historical submissions retain not-recorded metrics', () => {
  const {describe} = require('../metrics-display.js');
  const metricsContext={window:{}};
  vm.runInNewContext(fs.readFileSync(path.join(root,'run-metrics.js'),'utf8'),metricsContext);
  for(const id of ['deepseek/deepseek-v4-flash','meta/muse-spark-1.3']){
    const model=Catalog.resolve(catalog,id);
    assert.ok(model);
    assert.match(describe(metricsContext.window.ARENA_RUN_METRICS[model.path]).text,/Tokens: not recorded · Time: not recorded/);
  }
});
