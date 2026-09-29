"""Build a standalone card harness: real NOAA fixture tides, labeled demo weather."""

import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

from custom_components.tideglass.frontend import timeline_data
from custom_components.tideglass.model import parse_predictions

root = Path(__file__).resolve().parents[1]
settings = dict(
    station="8446121",
    name="Provincetown",
    latitude=42.04959,
    longitude=-70.18216,
    harmonic=True,
    units="ft",
    time_zone="America/New_York",
)
now = datetime(2026, 9, 28, 16, tzinfo=UTC)
c = SimpleNamespace(settings=settings, fetched=now, data={"source_status": "fresh"})
c.events = parse_predictions(
    json.loads((root / "tests/fixtures/provincetown_hilo.json").read_text()), events=True
)
c.samples = parse_predictions(
    json.loads((root / "tests/fixtures/provincetown_6.json").read_text()), events=False
)
out = root / ".local/card-preview"
out.mkdir(exist_ok=True, parents=True)
(out / "data.json").write_text(json.dumps(timeline_data(c, now)))
(
    out / "index.html"
).write_text("""<!DOCTYPE html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tideglass interactive card preview</title>
<style>body{margin:0;background:#0b1720;color:#edf5f2;font-family:system-ui,sans-serif}main{max-width:1120px;margin:52px auto;padding:0 20px}p{font-size:12px;color:#a0b6bf;line-height:1.7}h1{font:38px Georgia,serif;letter-spacing:-.6px;margin-bottom:12px}.eyebrow{color:#73dbc7;letter-spacing:3px;font-size:10px}tideglass-card{margin-top:28px}.tools{display:flex;gap:8px;flex-wrap:wrap;margin-top:24px}.tools button{background:#19303d;border:1px solid #283e4a;color:#edf5f2;padding:12px 16px;border-radius:20px;cursor:pointer}@media(max-width:500px){main{padding:0 10px;margin:25px auto}h1{font-size:31px}}</style>
<main><div class="eyebrow">COAST / CARD PREVIEW</div><h1>A little closer to the water.</h1><p>Recorded NOAA tides · sample weather for design testing · September 28, 2026</p><tideglass-card></tideglass-card><div class="tools"><button id="normal">Normal</button><button id="missing">Weather unavailable</button><button id="cached">Stored tides</button><button id="failed">Tides unavailable</button></div></main>
<script>
class PreviewIcon extends HTMLElement {connectedCallback(){const name=this.getAttribute('icon')||'';let shape='';if(name.includes('chevron'))shape=name.includes('left')?'<path d="m15 6-6 6 6 6"/>':name.includes('right')?'<path d="m9 6 6 6-6 6"/>':'<path d="m6 9 6 6 6-6"/>';else if(name.includes('night'))shape='<path d="M19 15A8 8 0 0 1 9 5a8 8 0 1 0 10 10Z"/>';else if(name.includes('wind'))shape='<path d="M3 8h11c5 0 4-6 1-4M3 12h15c5 0 4 7 0 5M3 16h6"/>';else if(name.includes('water'))shape='<path d="M12 3C9 8 5 12 5 16a7 7 0 0 0 14 0c0-4-4-8-7-13Z"/>';else if(name.includes('thermometer'))shape='<path d="M10 14V5a2 2 0 0 1 4 0v9a4 4 0 1 1-4 0Z"/>';else shape='<path d="M6 18h12a4 4 0 0 0 0-8 6 6 0 0 0-11-1 4.5 4.5 0 0 0-1 9Z"/><path d="M7 2v2M1 7h2M3 3l2 2"/>';this.innerHTML='<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'+shape+'</svg>';}}
customElements.define('ha-icon',PreviewIcon);
</script><script src="/custom_components/tideglass/frontend/tideglass-card.js"></script>
<script type="module">
const d=await(await fetch('/.local/card-preview/data.json')).json();const card=document.querySelector('tideglass-card');let callback,failed=false;
const forecast=Array.from({length:72},(_,i)=>({datetime:new Date(Date.parse(d.start)+i*3600000).toISOString(),temperature:61+Math.round(5*Math.sin(i/5)),wind_speed:9+i%9,precipitation_probability:i%13===0?42:i%4*5,condition:i%24<6?'clear-night':i%13===0?'rainy':i%4===0?'cloudy':'partlycloudy'}));
const hass={states:{'weather.demo':{state:'partlycloudy',attributes:{temperature_unit:'°F',wind_speed_unit:'mph'}}},callWS:async()=>{if(failed)throw Error('offline');return d;},connection:{subscribeMessage:async(cb)=>{callback=cb;cb({forecast});return()=>{};}}};
card.setConfig({entity:'sensor.provincetown_tideglass_week',weather_entity:'weather.demo'});card.hass=hass;
document.querySelector('#normal').onclick=()=>{failed=false;d.status='fresh';hass.states['weather.demo'].state='partlycloudy';callback({forecast});card._fetch(true)};
document.querySelector('#missing').onclick=()=>{hass.states['weather.demo'].state='unavailable';callback({forecast:[]})};
document.querySelector('#cached').onclick=()=>{d.status='cached';card._fetch(true)};
document.querySelector('#failed').onclick=()=>{failed=true;card._fetch(true)};
</script></html>""")
print(out / "index.html")
