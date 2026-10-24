// Run the actual event handlers without a browser or third-party packages.
const assert = require('assert').strict;
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const book = path.resolve(__dirname, '../..');
const markup = fs.readFileSync(path.join(book, '_includes/rd-activity.html'), 'utf8');
const nodes = new Map();
function element(id) {
  return {id, textContent:'', innerHTML:'', value:'', hidden:false, checked:false, attrs:{}, events:{},
    addEventListener(type, fn) { this.events[type]=fn; },
    setAttribute(name, value) { this.attrs[name]=value; },
    removeAttribute(name) { delete this.attrs[name]; },
    focus() { focused=this; }
  };
}
let focused;
for (const match of markup.matchAll(/\bid="([^"]+)"/g)) {
  assert(!nodes.has(match[1]), `Duplicate ID: ${match[1]}`);
  nodes.set(match[1], element(match[1]));
}
const el = id => nodes.get(`rd-${id}`);
const groups = {};
for (const name of ['rd-population','rd-claim-answer','rd-design-answer']) {
  groups[name] = [...markup.matchAll(new RegExp('name="'+name+'" value="([^" ]+)"','g'))].map(m => Object.assign(element(m[1]), {value:m[1]}));
  assert.equal(groups[name].length,4);
}
const radios = groups['rd-population'];
const claims = groups['rd-claim-answer'];
const designs = groups['rd-design-answer'];
el('activity').querySelectorAll = selector => groups[selector.match(/name="([^"]+)"/)[1]];
el('form').reset = () => {
  ['degree','eligibility','effect'].forEach(id => el(id).value='');
  Object.values(groups).flat().forEach(r => r.checked=false);
};
vm.runInNewContext(fs.readFileSync(path.join(book,'widgets/rd-activity.js'),'utf8'), {
  document:{getElementById(id) { assert(nodes.has(id), `Missing ID ${id}`); return nodes.get(id); }}
});
function event(id,type='click') { el(id).events[type]({preventDefault(){}}); }
function response(degree,eligibility,effect,population) {
  for (const [id,value] of Object.entries({degree,eligibility,effect})) {
    el(id).value=String(value); event(id,'input');
  }
  radios.forEach(r => r.checked=r.value===population);
  if (population) radios.find(r => r.checked).events.change();
}
function check() { event('form','submit'); }
assert.equal(el('case').textContent,'Case 1 of 2 · University A');
assert.equal(el('prob-below').textContent,'30%');
assert.equal(el('pay-above').textContent,'$45,600');
assert.equal(el('actions').hidden,false);
assert.equal(el('solution').hidden,true);
assert.equal(el('next').hidden,true);
check();
assert.equal(el('solution-button').hidden,true);
assert.match(el('status').textContent,/Complete all three/);
event('solution-button');
assert.equal(el('solution').hidden,true);
assert.equal(focused,el('degree'));
// Malformed, blank, and non-finite entries must not unlock solutions.
for (const bad of ['', '20abc','Infinity','NaN','1e309']) {
  response(bad,3600,18000,'switchers'); check();
  assert.equal(el('solution-button').hidden,true,bad);
}
// Diagnose probability units, levels instead of jumps, and the wrong denominator.
response(.2,3600,7200,'all-nearby'); check();
assert.match(el('degree-hint').textContent,/percentage points/);
assert.match(el('effect-hint').textContent,/share completing economics above/);
assert.match(el('interpretation-hint').textContent,/same degree/);
assert.equal(el('solution').hidden,true);
assert.equal(el('solution-button').hidden,false);
assert(!el('effect-hint').textContent.includes('18,000'));
response(50,3600,180,'all-majors'); check();
assert.match(el('degree-hint').textContent,/rate above/);
assert.match(el('effect-hint').textContent,/not a number of percentage points/);
response(20,3600,3600,'always'); check();
assert.match(el('effect-hint').textContent,/effect of eligibility/);
assert.match(el('interpretation-hint').textContent,/do not generate/);
// Correct arithmetic alone must not complete the activity.
response(20,3600,18000,'all-majors'); check();
assert.match(el('status').textContent,/3 of 4/);
assert.equal(el('solution').hidden,true);
event('next');
assert.match(el('case').textContent,/University A/);
// Deliberate reveal after a complete attempt allows progression, without claiming success.
event('solution-button');
assert.equal(el('solution').hidden,false);
assert.match(el('solution').innerHTML,/\$18,000/);
assert.match(el('status').textContent,/Solution revealed/);
assert.equal(el('next').hidden,false);
// Editing an answer clears stale feedback and relocks progression.
el('effect').value='18001'; event('effect','input');
assert.equal(el('solution').hidden,true);
assert.equal(el('next').hidden,true);
response('20.00','$3,600','$18,000','switchers'); check();
assert.match(el('status').textContent,/All four answers are correct/);
assert.equal(el('solution').hidden,false);
event('next');
assert.match(el('case').textContent,/University B/);
assert.equal(el('degree').value,'');
assert.equal(el('prob-below').textContent,'45%');
assert.equal(el('prob-above').textContent,'55%');
assert.equal(el('pay-below').textContent,'$48,000');
assert.equal(el('pay-above').textContent,'$51,600');
assert.equal(el('solution').hidden,true);
assert.equal(el('calculations').hidden,true);
assert.equal(el('calculations').disabled,true);
assert.equal(el('interpretation').hidden,true);
assert.equal(el('claim').hidden,false);
assert.equal(el('claim').disabled,false);
assert.equal(el('design').hidden,false);
assert.equal(el('evidence').hidden,false);
assert.equal(el('assumptions').hidden,true);
check();
assert.match(el('status').textContent,/Answer both questions/);
assert.equal(el('solution-button').hidden,true);
function assess(claim,design) {
  for (const [group,value] of [[claims,claim],[designs,design]]) {
    group.forEach(r => r.checked=r.value===value);
    const selected=group.find(r => r.checked);
    if (selected) selected.events.change();
  }
}
assess('package',null); check();
assert.equal(el('solution-button').hidden,true);
assert.equal(focused,designs[0]);
for (const [claim,design,claimHint,designHint] of [
  ['degree-ratio','narrower',/numerically correct/,/both the major and the internship/],
  ['degree-jump','larger',/only route/,/precision/],
  ['nothing','balance',/package/,/comparability/]
]) {
  assess(claim,design); check();
  assert.match(el('status').textContent,/0 of 2/);
  assert.match(el('claim-hint').textContent,claimHint);
  assert.match(el('design-hint').textContent,designHint);
  assert.equal(el('solution').hidden,true);
  assert.equal(el('solution-button').hidden,false);
}
event('solution-button');
assert.match(el('status').textContent,/Explanation revealed/);
assert.match(el('solution').innerHTML,/exclusion restriction/);
assert.match(el('solution').innerHTML,/not identified as a degree effect/);
assess('package','larger'); check();
assert.match(el('status').textContent,/1 of 2/);
assert.equal(el('solution').hidden,true);
assess('package','separate'); check();
assert.match(el('status').textContent,/Both answers are correct/);
assert.match(el('solution').innerHTML,/combined effect/);
assert.equal(el('solution').hidden,false);
assert.equal(el('next').hidden,true);
event('reset');
assert.match(el('case').textContent,/University A/);
assert.equal(el('solution').hidden,true);
assert.equal(el('solution-button').hidden,true);
assert.equal(el('degree').value,'');
assert(!Object.values(groups).flat().some(r=>r.checked));
assert.equal(el('calculations').hidden,false);
assert.equal(el('calculations').disabled,false);
assert.equal(el('claim').hidden,true);
assert.equal(el('claim').disabled,true);
assert.equal(el('assumptions').hidden,false);
assert.equal(el('evidence').hidden,true);
assert.equal(el('status').textContent,'');
// Export optional chart proofs for visual inspection; the same SVG and CSS as the activity.
if (process.env.RD_PROOF_DIR) {
  const css=fs.readFileSync(path.join(book,'widgets/rd-activity.css'),'utf8');
  for(const kind of ['degree','earnings']) {
    const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="320" height="240" viewBox="0 0 320 240"><style>${css}</style><g class="rd-charts">${el(kind+'-plot').innerHTML}</g></svg>`;
    fs.writeFileSync(path.join(process.env.RD_PROOF_DIR,`rd-${kind}.svg`),svg);
  }
}
console.log('RD activity passed: answer gates, malformed inputs, diagnostic hints, interpretation, deliberate reveal, calculation and identification cases, stale-feedback clearing, and reset.');
