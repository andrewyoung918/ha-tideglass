/* Tideglass 0.2.3 • MIT • Bundled, dependency-free Home Assistant card. */
(() => {
  const HOUR = 3600000;
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const numeric = value => value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value));
  const stamp = value => new Date(value).getTime();
  const clock = (time, zone, minutes = false) => new Intl.DateTimeFormat('en-US', {timeZone:zone,hour:'numeric',...(minutes ? {minute:'2-digit'} : {})}).format(time);
  const dateLabel = (time, zone, short = false) => new Intl.DateTimeFormat('en-US', {timeZone:zone,weekday:short?'short':'long',month:'short',day:'numeric'}).format(time);
  const icons = {sunny:'weather-sunny','clear-night':'weather-night',partlycloudy:'weather-partly-cloudy',cloudy:'weather-cloudy',rainy:'weather-rainy',pouring:'weather-pouring',windy:'weather-windy','windy-variant':'weather-windy',fog:'weather-fog',snowy:'weather-snowy','snowy-rainy':'weather-snowy-rainy',hail:'weather-hail',lightning:'weather-lightning','lightning-rainy':'weather-lightning-rainy',exceptional:'alert-circle-outline'};
  const icon = (name, label = '') => `<ha-icon icon="mdi:${name}" ${label ? `role="img" aria-label="${escape(label)}"` : 'aria-hidden="true"'}></ha-icon>`;
  function heightAt(samples, time) {
    let lo = 0, hi = samples.length - 1;
    if (hi < 1 || time < samples[0][0] || time > samples[hi][0]) return null;
    while (lo + 1 < hi) { const mid = (lo + hi) >> 1; if (samples[mid][0] <= time) lo = mid; else hi = mid; }
    const [a,b] = [samples[lo],samples[hi]];
    if (b[0]-a[0] > 7*60000) return null;
    return a[1] + (b[1]-a[1]) * (time-a[0])/(b[0]-a[0]);
  }
  function forecastAt(forecasts, time) {
    // An hourly prediction is valid only for its own hour. Never extend the last row.
    const f = forecasts.find(row => stamp(row.datetime) <= time && time < stamp(row.datetime)+HOUR);
    return f || null;
  }
  const css = `
    :host{display:block;min-width:0;container-type:inline-size;--ink:#edf5f2;--muted:#a0b6bf;--sea:#73dbc7;--gold:#efd19a;--edge:#283e4a;--panel:#101f2b;color:var(--ink);font-family:var(--primary-font-family,system-ui,sans-serif)}
    *{box-sizing:border-box}ha-card{display:block;overflow:hidden;background:var(--panel);color:var(--ink);border:1px solid var(--edge);border-radius:24px;box-shadow:0 8px 32px #00000016}
    button{font:inherit;color:inherit;cursor:pointer;border:0;background:transparent;min-height:44px;touch-action:manipulation}button:focus-visible,.scroller:focus-visible{outline:2px solid var(--sea);outline-offset:-3px}button:disabled{opacity:.3;cursor:default}ha-icon{width:20px;height:20px;--mdc-icon-size:20px;display:inline-flex;align-items:center;justify-content:center}
    .header{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:start;gap:12px;padding:26px 28px 18px}.eyebrow{font-size:10px;text-transform:uppercase;letter-spacing:2.2px;color:var(--sea);font-weight:700;line-height:1.6}.title{font:400 clamp(27px,4cqw,36px)/1.15 Georgia,'Times New Roman',serif;letter-spacing:-.6px;margin:8px 0 7px}.sub{font-size:12px;color:var(--muted);line-height:1.6}.status{display:flex;gap:7px;align-items:center}.dot{background:var(--sea);height:5px;width:5px;border-radius:50%}.bad{color:var(--gold)}.bad .dot{background:var(--gold)}
    .toggle{border:1px solid var(--edge);border-radius:24px;display:flex;align-items:center;gap:8px;padding:0 14px;white-space:nowrap;font-size:12px;flex-shrink:0}.toggle:hover,.nav button:hover{background:#1b3340}.toggle[aria-expanded=true]{border-color:#73dbc755;color:var(--sea)}.toggle .chevron{transition:transform .2s}.toggle[aria-expanded=true] .chevron{transform:rotate(180deg)}
    .current-row{grid-column:1/-1;display:flex;align-items:flex-start;justify-content:space-between;gap:16px}.summary{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;min-width:0}.current-weather{text-align:right;min-width:0;max-width:50%}.current-weather[hidden]{display:none}.weather-reading{display:flex;align-items:center;justify-content:flex-end;gap:9px}.weather-reading ha-icon{color:var(--gold);flex-shrink:0}.current-temp{font:400 30px Georgia,serif;letter-spacing:-.7px;white-space:nowrap}.current-temp small{font:12px system-ui;color:var(--muted);margin-left:3px}.current-condition{font-size:12px;color:var(--muted);margin-top:4px;line-height:1.4;overflow-wrap:anywhere}.height{font:400 30px Georgia,serif;letter-spacing:-.7px}.height small{font:12px system-ui;color:var(--muted);margin-left:3px}.direction{font-size:12px;color:var(--sea)}
    .toolbar{display:flex;align-items:center;justify-content:space-between;gap:6px;padding:0 22px 8px}.range{font-size:13px;font-weight:500}.nav{display:flex;gap:2px;align-items:center}.nav button{min-width:44px;border-radius:50%}.nav .today{font-size:11px;border-radius:20px;padding:0 10px}.legend{display:flex;gap:13px;color:var(--muted);font-size:10px;align-items:center;padding:0 28px 15px;flex-wrap:wrap}.legend i{display:inline-block;width:14px;height:1px;background:var(--gold);vertical-align:middle;margin-right:5px}.legend .night{height:8px;background:#697ead44;border-radius:2px}.legend .now{background:var(--ink)}
    .viewport{position:relative;display:grid;grid-template-columns:38px minmax(0,1fr)}.axis{position:relative;pointer-events:none;z-index:2;background:var(--panel);font-size:10px;color:var(--muted)}.axis span{position:absolute;right:8px;transform:translateY(-50%)}.axis .unit{top:24px;font-size:9px}.rowlabel{position:absolute;right:9px;color:var(--muted)}.rowlabel ha-icon{width:17px;height:17px;--mdc-icon-size:17px}
    .scroller{overflow-x:auto;overflow-y:hidden;scroll-snap-type:x proximity;overscroll-behavior-x:contain;scrollbar-width:thin;scrollbar-color:#46616c transparent;-webkit-overflow-scrolling:touch;cursor:grab;touch-action:pan-x pan-y}.scroller.free-position{scroll-snap-type:none}.scroller.dragging{cursor:grabbing;scroll-snap-type:none;user-select:none}.track{position:relative;min-height:282px}.snap{position:absolute;top:0;bottom:0;pointer-events:none;scroll-snap-align:start}.daylabel{position:absolute;top:3px;white-space:nowrap;font-size:11px;color:var(--muted);letter-spacing:.3px}.daylabel strong{color:var(--ink);font-weight:500}.chart{display:block;overflow:visible}.chart text{font-family:var(--primary-font-family,system-ui,sans-serif)}.grid{stroke:var(--edge);stroke-width:1;stroke-dasharray:2 6}.curve{fill:none;stroke:var(--sea);stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}.event-label{fill:var(--ink);font-size:11px}.event-time{fill:var(--muted);font-size:10px}.hour{fill:var(--muted);font-size:10px}.sun-label{fill:var(--gold);font-size:9px}.sun-line{stroke:var(--gold);stroke-opacity:.4;stroke-width:1;stroke-dasharray:3 5}.now-line{stroke:var(--ink);stroke-opacity:.65;stroke-width:1;stroke-dasharray:3 4}.now-tag{fill:var(--ink);font-size:9px;letter-spacing:1px}.inspection{pointer-events:none}.inspection line{stroke:var(--ink);stroke-opacity:.7}.inspection circle{fill:var(--sea);stroke:var(--panel);stroke-width:3}
    .weather{height:194px;border-top:1px solid var(--edge);position:relative}.weather[hidden]{display:none}.column{position:absolute;top:0;width:68px;transform:translateX(-50%);text-align:center;font-size:11px;color:var(--muted);padding:10px 0;border-radius:8px}.column .time{font-size:10px;height:25px}.column .condition{height:32px;color:var(--gold)}.column .temp{height:31px;font-size:17px;color:var(--ink);font-weight:500}.column .wind{height:28px;font-size:11px}.column .rain{height:27px;font-size:12px;color:#8cbede}.column abbr{text-decoration:none}.column.current{background:#73dbc709}.column .wind small{font-size:9px;margin-left:2px}.column:focus-visible{outline:1px solid var(--sea)}
    .footer{display:flex;justify-content:space-between;gap:10px;padding:15px 27px 19px;font-size:10px;color:var(--muted);line-height:1.6}.footer .hint{color:var(--sea);white-space:nowrap}.weather-note{padding:10px 27px 0;font-size:11px;color:var(--muted)}.weather-note[hidden]{display:none}.empty{padding:32px 28px;color:var(--muted);font-size:14px;line-height:1.7}.empty strong{display:block;color:var(--ink);font:26px Georgia,serif;margin-bottom:9px}.retry{color:var(--sea);text-decoration:underline;padding:0 6px;margin-left:-6px}.readout{min-height:26px;margin:0 28px 9px;font-size:12px;color:var(--sea)}
    @container(max-width:500px){.header{padding:21px 18px 14px;gap:8px}.title{font-size:29px}.toggle{padding:0 11px;gap:5px}.toggle .word{display:none}.toolbar{padding:0 12px 8px}.legend{padding:0 18px 12px;gap:10px}.footer{padding:13px 18px 17px;display:block}.footer .hint{display:block;margin-top:4px}.weather-note{padding-left:18px}.readout{margin-left:18px}.sub{font-size:11px}.current-row{gap:12px}.summary{display:block}.direction{display:block;margin-top:4px;line-height:1.4}.height,.current-temp{font-size:28px}.current-condition{font-size:11px}.weather-reading{gap:6px}}
    @media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
  `;
  class TideglassCard extends HTMLElement {
    constructor() { super(); this.attachShadow({mode:'open'}); this._expanded = false; this._forecast = []; this._generation=0; this._width=0; }
    setConfig(config) {
      if (!config.entity?.startsWith('sensor.')) throw new Error('Choose a Tideglass sensor, for example its Week sensor.');
      const changed = this._config && (this._config.entity !== config.entity || this._config.weather_entity !== config.weather_entity);
      this._config = {...config}; this._expanded = config.expanded ?? this._expanded;
      if(changed){this._stop();this._data=null;this._forecast=[];this._lastFetch=0;}
      this._render(); this._start();
    }
    static getStubConfig(hass) { return {entity:Object.keys(hass.states).find(k=>k.startsWith('sensor.')&&hass.states[k].attributes.tides) || 'sensor.provincetown_tideglass_week',weather_entity:Object.keys(hass.states).find(k=>k.startsWith('weather.'))}; }
    static getConfigForm() { return {schema:[{name:'entity',required:true,selector:{entity:{domain:'sensor'}}},{name:'weather_entity',selector:{entity:{domain:'weather'}}},{name:'title',selector:{text:{}}},{name:'expanded',selector:{boolean:{}}}]}; }
    getCardSize() { return this._expanded?12:8; }
    getGridOptions() { return {columns:'full',min_columns:6}; }
    set hass(hass) { const prior=this._hass;this._hass=hass;if(prior?.connection!==hass.connection){this._stop();this._lastFetch=0;}this._start();this._renderCurrentWeather(); }
    connectedCallback() { this._observer=new ResizeObserver(entries=>{const w=Math.round(entries[0].contentRect.width);if(w!==this._width){this._width=w;if(w)this._render();}});this._observer.observe(this);this._start(); }
    disconnectedCallback() {this._observer?.disconnect();this._stop();}
    _stop() {this._generation++;cancelAnimationFrame(this._layoutFrame);clearInterval(this._timer);this._timer=null;this._unsubscribe?.();this._unsubscribe=null;this._subscribing=false;this._fetching=false;this._weatherAttempt=0;}
    _start() {
      if(!this.isConnected||!this._config||!this._hass) return;
      if(!this._timer) this._timer=setInterval(()=>{this._fetch();this._subscribeWeather();this._updateClock();},60000);
      this._fetch();this._subscribeWeather();
    }
    async _fetch(force=false) {
      if(this._fetching||!this._hass||(!force&&Date.now()-(this._lastFetch||0)<300000))return;
      this._fetching=true;const generation=this._generation;this._lastFetch=Date.now();
      try {const data=await this._hass.callWS({type:'tideglass/timeline',entity_id:this._config.entity});if(generation!==this._generation)return;this._data=data;this._error=null;this._render();}
      catch(e){if(generation!==this._generation)return;this._error='Tide predictions are unavailable. Tideglass will retry automatically.';this._data=null;this._render();}
      finally{if(generation===this._generation)this._fetching=false;}
    }
    async _subscribeWeather() {
      if(!this._config.weather_entity||this._unsubscribe||this._subscribing||Date.now()-(this._weatherAttempt||0)<300000)return;
      this._weatherAttempt=Date.now();
      this._subscribing=true;const generation=this._generation;
      try {const unsubscribe=await this._hass.connection.subscribeMessage(message=>{if(generation!==this._generation)return;this._forecast=Array.isArray(message.forecast)?message.forecast:[];this._weatherError=false;this._weatherReceived=Date.now();this._renderWeather();},{type:'weather/subscribe_forecast',entity_id:this._config.weather_entity,forecast_type:'hourly'});
        if(generation!==this._generation)unsubscribe();else this._unsubscribe=unsubscribe;
      }catch(e){if(generation===this._generation){this._weatherError=true;this._renderWeather();}}
      finally{if(generation===this._generation)this._subscribing=false;}
    }
    _geometry() {
      const d=this._data, dayWidth=Math.max(432,Math.min(680,(this._width||680)-74));
      const start=stamp(d.start),end=stamp(d.end),scale=dayWidth/(24*HOUR),pad=38;
      const values=[...d.samples.map(s=>s[1]),...d.events.map(e=>e.height)].filter(Number.isFinite);
      const min=Math.floor(Math.min(...values,0)),max=Math.ceil(Math.max(...values,1));
      return {dayWidth,start,end,scale,pad,width:(end-start)*scale+pad*2,min,max,x:t=>pad+(t-start)*scale,y:h=>218-(h-min)/(max-min)*142};
    }
    _render() {
      if(!this._config)return;
            const oldTime=this._viewTime??(Date.now()-4*HOUR);this._viewTime=oldTime;
      const focused=this.shadowRoot.activeElement?.dataset?.action;
      const d=this._data;
      if(!d){this.shadowRoot.innerHTML=`<style>${css}</style><ha-card><div class="empty"><div class="eyebrow">Tideglass</div><strong>${escape(this._config.title||'The rhythm of the harbor')}</strong>${escape(this._error||'Bringing in the tides…')}${this._error?'<br><button class="retry">Try again</button>':''}</div></ha-card>`;this.shadowRoot.querySelector('.retry')?.addEventListener('click',()=>this._fetch(true));return;}
      this._g=this._geometry();const g=this._g;
      this.shadowRoot.innerHTML=`<style>${css}</style><ha-card>
        <header class="header"><div><div class="eyebrow">Tideglass / ${escape(d.station)}</div><h2 class="title">${escape(this._config.title||'The rhythm of the harbor')}</h2><div class="sub status ${d.status==='cached'?'bad':''}"><span class="dot"></span>${d.status==='cached'?'Stored predictions · connection delayed':'Seven days at the water’s edge'}</div></div>
        <button class="toggle" data-action="expand" aria-label="${this._expanded?'Hide':'Show'} four-hour weather forecast" aria-expanded="${this._expanded}" aria-controls="weather"><span>${icon('weather-partly-cloudy')}</span><span class="word">Weather</span><span class="chevron">${icon('chevron-down')}</span></button><div class="current-row"><div class="summary"></div><div class="current-weather" role="group" aria-label="Current weather"></div></div></header>
        <div class="toolbar"><div class="range" aria-live="polite"></div><nav class="nav" aria-label="Tide days"><button data-action="previous" aria-label="Previous day">${icon('chevron-left')}</button><button class="today" data-action="today">Now</button><button data-action="next" aria-label="Next day">${icon('chevron-right')}</button></nav></div>
        <div class="legend"><span><i></i>Sunrise & sunset</span><span><i class="night"></i>Night</span><span><i class="now"></i>Now</span></div>
        <div class="viewport"><div class="axis"><span class="unit">${escape(d.unit)}</span>${[g.min,(g.min+g.max)/2,g.max].map(h=>`<span style="top:${g.y(h)}px">${Number(h.toFixed(1))}</span>`).join('')}<div class="weather-axis" ${this._expanded?'':'hidden'}><div class="rowlabel" style="top:327px">${icon('weather-partly-cloudy','Conditions')}</div><div class="rowlabel" style="top:359px">${icon('thermometer','Temperature')}</div><div class="rowlabel" style="top:389px">${icon('weather-windy','Wind speed')}</div><div class="rowlabel" style="top:417px">${icon('water-outline','Rain probability')}</div></div></div>
        <div class="scroller free-position" tabindex="0" data-action="timeline" role="region" aria-label="Seven-day tide and weather timeline. Swipe horizontally, or use left and right arrow keys to move by day. Press Enter to inspect the center time."><div class="track" style="width:${g.width}px">
        ${d.days.map((day,i)=>`<div class="snap" style="left:${g.x(stamp(day.start))-g.pad}px;width:${g.x(stamp(day.end))-g.x(stamp(day.start))}px"></div><div class="daylabel" style="left:${g.x(stamp(day.start))}px"><strong>${i===0?'Today':dateLabel(stamp(day.start),d.time_zone,true)}</strong>${i===0?' · '+dateLabel(stamp(day.start),d.time_zone,true):''}</div>`).join('')}
        ${this._chart()}<div class="weather" id="weather" ${this._expanded?'':'hidden'}></div></div></div></div>
        <div class="weather-note" ${this._expanded?'':'hidden'}></div><div class="readout" aria-live="polite">Tap the curve to explore a time</div>
        <footer class="footer"><span>NOAA predictions · ${escape(d.unit)} above ${escape(d.datum)} · ${escape(d.time_zone.replace(/_/g,' '))}${d.curve==='illustrative'?'<br>Illustrative curve between high and low tides':''}</span><span class="hint">Swipe to follow the tide →</span></footer></ha-card>`;
      const scroller=this.shadowRoot.querySelector('.scroller');
      cancelAnimationFrame(this._layoutFrame);this._layoutFrame=requestAnimationFrame(()=>{scroller.scrollLeft=Math.max(0,(oldTime-g.start)*g.scale);this._updateRange();});
      scroller.addEventListener('scroll',()=>{this._viewTime=g.start+scroller.scrollLeft/g.scale;this._updateRange();},{passive:true});
      scroller.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();this._go(e.key==='ArrowLeft'?-1:e.key==='ArrowRight'?1:e.key==='Home'?'today':'end');}else if(e.key==='Enter'){e.preventDefault();const rect=scroller.getBoundingClientRect();scroller.dispatchEvent(new MouseEvent('click',{clientX:rect.left+scroller.clientWidth/2,clientY:rect.top+140,bubbles:true}));}});
      this.shadowRoot.querySelector('[data-action=expand]').onclick=()=>this._toggle();
      for(const action of ['previous','next','today'])this.shadowRoot.querySelector(`[data-action=${action}]`).onclick=()=>this._go(action==='previous'?-1:action==='next'?1:'today');
      this._bindPointer(scroller);this._updateClock();this._updateRange();this._renderWeather();
      if(focused)this.shadowRoot.querySelector(`[data-action=${focused}]`)?.focus({preventScroll:true});
    }
    _chart() {
      const d=this._data,g=this._g;let background='',solar='',grid='',events='';
      for(const day of d.days){const a=stamp(day.start),b=stamp(day.end),crossings=[['sunrise',day.sunrise],['sunset',day.sunset]].filter(([,t])=>t).map(([k,t])=>[k,stamp(t)]).sort((a,b)=>a[1]-b[1]);let cursor=a,daylight=day.starts_in_daylight;
        for(const [kind,t] of [...crossings,['end',b]]){if(!daylight)background+=`<rect x="${g.x(cursor)}" y="31" width="${(t-cursor)*g.scale}" height="218" fill="#667aa7" opacity=".08"/>`;cursor=t;daylight=kind==='sunrise';}
        for(const [kind,t] of crossings)solar+=`<line class="sun-line" x1="${g.x(t)}" x2="${g.x(t)}" y1="55" y2="247"/><text class="sun-label" x="${g.x(t)}" y="43" text-anchor="middle">${kind==='sunrise'?'↑':'↓'} ${clock(t,d.time_zone,true)}</text>`;
        grid+=`<line x1="${g.x(a)}" x2="${g.x(a)}" y1="30" y2="277" stroke="#283e4a"/>`;
        for(const slot of day.weather_slots)grid+=`<text class="hour" x="${g.x(stamp(slot))}" y="268" text-anchor="middle">${clock(stamp(slot),d.time_zone)}</text>`;
      }
      for(const h of [g.min,(g.min+g.max)/2,g.max])grid+=`<line class="grid" x1="${g.pad}" x2="${g.width-g.pad}" y1="${g.y(h)}" y2="${g.y(h)}"/>`;
      const segments=[];let segment=[];
      for(const sample of d.samples){if(segment.length&&sample[0]-segment.at(-1)[0]>7*60000){segments.push(segment);segment=[];}segment.push(sample);}if(segment.length)segments.push(segment);
      const paths=segments.map(segment=>{const line=segment.map((s,i)=>`${i?'L':'M'}${g.x(s[0]).toFixed(2)},${g.y(s[1]).toFixed(2)}`).join(' ');return `<path d="${line} L${g.x(segment.at(-1)[0])},247 L${g.x(segment[0][0])},247 Z" fill="url(#water)"/><path class="curve" d="${line}"/>`;}).join('');
      for(const e of d.events){const x=g.x(stamp(e.time)),y=g.y(e.height),high=e.type==='high',labelY=y+(high?-27:22);events+=`<circle cx="${x}" cy="${y}" r="3" fill="${high?'#efd19a':'#73dbc7'}" stroke="#101f2b" stroke-width="2"/><text class="event-label" x="${x}" y="${labelY}" text-anchor="middle">${high?'High':'Low'} · ${Number(e.height).toFixed(1)} ${escape(d.unit)}</text><text class="event-time" x="${x}" y="${labelY+14}" text-anchor="middle">${clock(stamp(e.time),d.time_zone,true)}</text>`;}
      return `<svg class="chart" width="${g.width}" height="282" viewBox="0 0 ${g.width} 282" role="img" aria-label="Tide curve with high and low tides, sunrise, sunset and nighttime shading"><defs><linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#73dbc7" stop-opacity=".16"/><stop offset="1" stop-color="#73dbc7" stop-opacity=".01"/></linearGradient></defs>${background}${grid}${solar}${paths}${events}<g class="now-marker"></g><g class="inspection"></g></svg>`;
    }
    _updateClock(){
      if(!this._data||!this._g)return;
      if(Date.now()-stamp(this._data.fetched)>48*HOUR){this._data=null;this._error='Stored tide predictions have expired. Waiting for NOAA.';this._render();return;}
      const now=Date.now(),g=this._g,d=this._data,h=heightAt(d.samples,now),future=heightAt(d.samples,now+60000);
      const summary=this.shadowRoot.querySelector('.summary');if(summary)summary.innerHTML=`<span class="height">${h===null?'—':h.toFixed(1)}<small>${escape(d.unit)}</small></span><span class="direction">${d.curve==='illustrative'?'Illustrative tide curve':h===null?'Prediction unavailable':future===null?'Predicted height':future>=h?'↗ Rising tide':'↘ Falling tide'}</span>`;
      const marker=this.shadowRoot.querySelector('.now-marker');if(marker)marker.innerHTML=now>=g.start&&now<=g.end?`<line class="now-line" x1="${g.x(now)}" x2="${g.x(now)}" y1="55" y2="248"/><text class="now-tag" x="${g.x(now)}" y="54" text-anchor="middle">NOW</text>`:'';
      this._renderWeather();
    }
    _toggle(){this._expanded=!this._expanded;const button=this.shadowRoot.querySelector('.toggle');button.setAttribute('aria-expanded',String(this._expanded));button.setAttribute('aria-label',`${this._expanded?'Hide':'Show'} four-hour weather forecast`);for(const selector of ['.weather','.weather-axis','.weather-note'])this.shadowRoot.querySelector(selector).hidden=!this._expanded;this.dispatchEvent(new Event('iron-resize',{bubbles:true,composed:true}));this.dispatchEvent(new Event('card-size-changed',{bubbles:true,composed:true}));}
    _renderCurrentWeather(){
      const element=this.shadowRoot.querySelector('.current-weather');if(!element)return;
      element.hidden=!this._config.weather_entity;if(element.hidden)return;
      const weather=this._hass?.states[this._config.weather_entity],available=weather&&!['unavailable','unknown'].includes(weather.state),a=weather?.attributes||{};
      const unit=['°F','°C'].includes(a.temperature_unit)?a.temperature_unit:'°';
      const temperature=available&&numeric(a.temperature)?Math.round(Number(a.temperature)):'—';
      const names={partlycloudy:'Partly cloudy','clear-night':'Clear night','windy-variant':'Windy','snowy-rainy':'Snow and rain','lightning-rainy':'Thunderstorms'};
      const condition=available?(names[weather.state]||weather.state.replace(/-/g,' ').replace(/^./,c=>c.toUpperCase())):'Weather unavailable';
      const html=`<div class="weather-reading">${available&&icons[weather.state]?icon(icons[weather.state]):''}<span class="current-temp">${temperature}${temperature==='—'?'':`<small>${escape(unit)}</small>`}</span></div><div class="current-condition">${escape(condition)}</div>`;
      if(element.innerHTML!==html)element.innerHTML=html;
    }
    _renderWeather(){
      this._renderCurrentWeather();
      const element=this.shadowRoot.querySelector('.weather');if(!element||!this._g)return;
      const weather=this._hass?.states[this._config.weather_entity];const available=weather&&!['unavailable','unknown'].includes(weather.state)&&!this._weatherError&&Date.now()-(this._weatherReceived||0)<2*HOUR;
      const forecasts=available?this._forecast:[],a=weather?.attributes||{},tempUnit=['°F','°C'].includes(a.temperature_unit)?a.temperature_unit:'°',windUnit=['mph','km/h','m/s','kn','ft/s'].includes(a.wind_speed_unit)?a.wind_speed_unit:'';
      element.innerHTML=this._data.days.flatMap(day=>day.weather_slots.map(slot=>{const time=stamp(slot),f=forecastAt(forecasts,time),temp=f&&numeric(f.temperature)?Math.round(f.temperature)+tempUnit:'—',wind=f&&numeric(f.wind_speed)?Math.round(f.wind_speed):'—',rain=f&&numeric(f.precipitation_probability)&&f.precipitation_probability>=0&&f.precipitation_probability<=100?Math.round(f.precipitation_probability)+'%':'—',condition=f?.condition?.replace(/-/g,' ')||'Forecast unavailable';
        return `<div class="column ${Date.now()>=time&&Date.now()<time+4*HOUR?'current':''}" style="left:${this._g.x(time)}px" role="group" aria-label="${escape(dateLabel(time,this._data.time_zone)+' '+clock(time,this._data.time_zone)+'. '+condition+'. Temperature '+temp+'. Wind '+wind+' '+windUnit+'. Rain chance '+rain)}"><div class="time">${clock(time,this._data.time_zone)}</div><div class="condition">${f&&icons[f.condition]?icon(icons[f.condition],condition):'—'}</div><div class="temp">${temp}</div><div class="wind">${wind}${wind==='—'?'':`<small>${escape(windUnit)}</small>`}</div><div class="rain">${rain}</div></div>`;})).join('');
      const note=this.shadowRoot.querySelector('.weather-note');note.textContent=!this._config.weather_entity?'Choose a weather entity to add a forecast.':!available?'Weather unavailable · tide predictions remain visible.':'Weather every 4 hours · temperature / wind / rain chance. Dashes mean no hourly forecast for that time.';
    }
    _updateRange(){const scroller=this.shadowRoot.querySelector('.scroller');if(!scroller||!this._data)return;const time=this._g.start+scroller.scrollLeft/this._g.scale;this.shadowRoot.querySelector('.range').textContent=dateLabel(Math.min(time+1,this._g.end-1),this._data.time_zone);this.shadowRoot.querySelector('[data-action=previous]').disabled=scroller.scrollLeft<2;this.shadowRoot.querySelector('[data-action=next]').disabled=scroller.scrollLeft>=scroller.scrollWidth-scroller.clientWidth-2;}
    _go(direction){const scroller=this.shadowRoot.querySelector('.scroller'),g=this._g;if(!scroller)return;const starts=this._data.days.map(d=>g.x(stamp(d.start))-g.pad);let left;if(direction==='today')left=Math.max(0,(Date.now()-g.start-4*HOUR)*g.scale);else if(direction==='end')left=scroller.scrollWidth;else if(direction>0)left=starts.find(x=>x>scroller.scrollLeft+4)??scroller.scrollWidth;else left=starts.toReversed().find(x=>x<scroller.scrollLeft-4)??0;scroller.classList.add('free-position');scroller.scrollTo({left,behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth'});}
    _bindPointer(scroller){
      let drag=null,moved=false,touchStart=null;
      scroller.addEventListener('wheel',()=>scroller.classList.remove('free-position'),{passive:true});
      scroller.addEventListener('pointerdown',e=>{touchStart=e.clientX;moved=false;if(e.pointerType==='mouse'&&e.button===0){drag={x:e.clientX,left:scroller.scrollLeft};scroller.setPointerCapture(e.pointerId);}});
      scroller.addEventListener('pointermove',e=>{if(!drag){if(touchStart!==null&&Math.abs(e.clientX-touchStart)>5){moved=true;scroller.classList.remove('free-position');}return;}const delta=e.clientX-drag.x;if(Math.abs(delta)>5)moved=true;if(moved){scroller.classList.add('dragging');scroller.classList.remove('free-position');scroller.scrollLeft=drag.left-delta;}});
      const finish=e=>{drag=null;touchStart=null;scroller.classList.remove('dragging');if(scroller.hasPointerCapture(e.pointerId))scroller.releasePointerCapture(e.pointerId);};
      scroller.addEventListener('pointerup',finish);scroller.addEventListener('pointercancel',finish);
      scroller.addEventListener('click',e=>{const chartRect=this.shadowRoot.querySelector('.chart').getBoundingClientRect();if((moved&&e.detail!==0)||e.clientY<chartRect.top||e.clientY>chartRect.bottom)return;const rect=scroller.getBoundingClientRect(),x=e.clientX-rect.left+scroller.scrollLeft,time=this._g.start+(x-this._g.pad)/this._g.scale,h=heightAt(this._data.samples,time);if(h===null)return;const d=this._data;this.shadowRoot.querySelector('.readout').textContent=`${dateLabel(time,d.time_zone,true)} · ${clock(time,d.time_zone,true)} · ${h.toFixed(2)} ${d.unit}${d.curve==='illustrative'?' · illustrative':''}`;this.shadowRoot.querySelector('.inspection').innerHTML=`<line x1="${x}" x2="${x}" y1="64" y2="247"/><circle cx="${x}" cy="${this._g.y(h)}" r="5"/>`;});
    }
  }
  if(!customElements.get('tideglass-card'))customElements.define('tideglass-card',TideglassCard);
  window.customCards=window.customCards||[];if(!window.customCards.some(c=>c.type==='tideglass-card'))window.customCards.push({type:'tideglass-card',name:'Tideglass',description:'An interactive tide timeline with sunrise, sunset, and a shared four-hour weather forecast.',preview:true,documentationURL:'https://github.com/andrewyoung918/ha-tideglass/blob/codex/tideglass/docs/INTERACTIVE-CARD.md'});
  // Pure helpers are exported only in Node's isolated test harness.
  if(typeof module!=='undefined')module.exports={heightAt,forecastAt,escape,numeric,TideglassCard};
})();
