const {test}=require('node:test');const assert=require('node:assert/strict');const vm=require('node:vm');const fs=require('node:fs');
const context={HTMLElement:class{},customElements:{get:()=>true},window:{customCards:[]},module:{exports:{}}};vm.createContext(context);vm.runInContext(fs.readFileSync('custom_components/tideglass/frontend/tideglass-card.js','utf8'),context);
const {heightAt,forecastAt,escape,numeric}=context.module.exports;
test('NOAA interpolation preserves zero and negative values; never extrapolates',()=>{assert.equal(heightAt([[0,-1],[360000,1]],180000),0);assert.equal(heightAt([[0,0],[360000,1]],-1),null);assert.equal(heightAt([[0,0],[360000,1]],360001),null);assert.equal(heightAt([[0,0],[900000,1]],100000),null);});
test('Hourly forecasts are not carried across missing hours or beyond horizon',()=>{const rows=[{datetime:'2026-09-28T00:00:00Z',temperature:0,precipitation_probability:0}];assert.equal(forecastAt(rows,Date.parse('2026-09-28T00:59:00Z')),rows[0]);assert.equal(forecastAt(rows,Date.parse('2026-09-28T01:00:00Z')),null);assert.equal(forecastAt(rows,Date.parse('2026-09-27T23:59:00Z')),null);});
test('Absent readings stay absent and untrusted labels are escaped',()=>{assert.equal(numeric(null),false);assert.equal(numeric(''),false);assert.equal(numeric(0),true);assert.equal(escape('<img onerror="x">'), '&lt;img onerror=&quot;x&quot;&gt;');});

test('Inspecting a stationary pointer never snaps away from Now; dragging enables day snapping',()=>{const {TideglassCard}=context.module.exports;const handlers={};const classes=new Set(['free-position']);const scroller={scrollLeft:200,classList:{add:x=>classes.add(x),remove:x=>classes.delete(x)},addEventListener:(name,fn)=>handlers[name]=fn,setPointerCapture:()=>{},hasPointerCapture:()=>false};const card=Object.create(TideglassCard.prototype);card._bindPointer(scroller);handlers.pointerdown({pointerType:'mouse',button:0,clientX:100,pointerId:1});handlers.pointerup({pointerId:1});assert.equal(classes.has('free-position'),true);assert.equal(scroller.scrollLeft,200);handlers.pointerdown({pointerType:'mouse',button:0,clientX:100,pointerId:2});handlers.pointermove({clientX:70});assert.equal(scroller.scrollLeft,230);assert.equal(classes.has('free-position'),false);});

test('Next day targets the next local midnight before browser snapping can change the position',()=>{context.matchMedia=()=>({matches:false});const {TideglassCard}=context.module.exports;let target;const scroller={scrollLeft:534,scrollWidth:4836,classList:{add:()=>{},toggle:()=>{scroller.scrollLeft=680}},scrollTo:options=>target=options.left};const card=Object.create(TideglassCard.prototype);card.shadowRoot={querySelector:()=>scroller};card._g={pad:38,start:0,scale:680/86400000,x:t=>38+t*680/86400000};card._data={days:[0,1,2,3].map(i=>({start:new Date(i*86400000).toISOString()}))};card._go(1);assert.equal(target,680);scroller.scrollLeft=680;card._go(-1);assert.equal(target,0);});

test('Curve rendering and previous-day navigation work without newer array methods',()=>{
  const legacy={HTMLElement:class{},customElements:{get:()=>true},window:{customCards:[]},module:{exports:{}},matchMedia:()=>({matches:true})};
  vm.createContext(legacy);
  vm.runInContext('Array.prototype.at=undefined;Array.prototype.toReversed=undefined;',legacy);
  vm.runInContext(fs.readFileSync('custom_components/tideglass/frontend/tideglass-card.js','utf8'),legacy);
  const result=vm.runInContext(`(()=>{
    const card=Object.create(module.exports.TideglassCard.prototype);
    card._width=390;
    card._data={start:'2026-09-28T00:00:00Z',end:'2026-09-30T00:00:00Z',time_zone:'UTC',unit:'ft',events:[],days:[0,1].map(i=>({start:new Date(Date.UTC(2026,8,28+i)).toISOString(),end:new Date(Date.UTC(2026,8,29+i)).toISOString(),starts_in_daylight:true,weather_slots:[]})),samples:[[Date.UTC(2026,8,28),0],[Date.UTC(2026,8,28,0,6),1],[Date.UTC(2026,8,28,0,12),0]]};
    card._g=card._geometry();
    const svg=card._chart();
    let destination;
    card.shadowRoot={querySelector:()=>({scrollLeft:card._g.dayWidth,scrollWidth:1000,classList:{add:()=>{}},scrollTo:({left})=>destination=left})};
    card._go(-1);
    return {svg,destination};
  })()`,legacy);
  assert.match(result.svg,/class="curve"/);
  assert.doesNotMatch(result.svg,/NaN|undefined/);
  assert.equal(result.destination,0);
});
