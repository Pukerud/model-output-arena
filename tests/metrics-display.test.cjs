const {test} = require('node:test');
const assert = require('node:assert/strict');
const {describe} = require('../metrics-display.js');

const run = (usage, duration_ms = 123456) => ({status: 'completed', duration_ms, usage});
test('historical records do not imply zero', () => {
  assert.match(describe().text, /Tokens: not recorded · Time: not recorded/);
});
test('whole-run total and wall time are labelled', () => {
  const result = describe(run({coverage: 'complete', total_tokens: 12345, input_tokens: 12000,
    output_tokens: 345, source: 'real API export'}));
  assert.equal(result.text, 'Whole run · Tokens: 12,345 · Time: 2m 3.5s');
  assert.match(result.detail, /Input \(incl. cached\): 12000/);
  assert.match(result.detail, /real API export/);
});
test('partial cannot masquerade as complete usage', () => {
  assert.match(describe(run({coverage: 'partial', total_tokens: 123})).text, /123 \(partial\)/);
  assert.match(describe(run({coverage: 'partial', total_tokens: null})).text, /partial breakdown/);
});
test('unavailable remains unknown while measured zero is displayed', () => {
  assert.match(describe(run({coverage: 'unavailable', total_tokens: null})).text, /Tokens: unavailable/);
  assert.match(describe(run({coverage: 'complete', total_tokens: 0}, 0)).text, /Tokens: 0 · Time: 0.0 s/);
});
test('invalid numbers and unfinished runs do not become final totals', () => {
  assert.match(describe(run({total_tokens: -1}, -2)).text, /Tokens: unavailable · Time: unavailable/);
  assert.equal(describe({status: 'running'}).text, 'Whole run · In progress');
});
test('rounded durations carry into the next minute', () => {
  assert.match(describe(run({coverage: 'complete', total_tokens: 1}, 119999)).text, /Time: 2m 0.0s/);
});
