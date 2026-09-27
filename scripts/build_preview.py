"""Build a portable design preview from NOAA fixtures and an optional NWS snapshot."""

import json
import math
from datetime import UTC, datetime, timedelta
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw

from custom_components.tideglass.graph import render_graph
from custom_components.tideglass.model import parse_predictions, select_tides

ROOT = Path(__file__).resolve().parents[1]
now = datetime(2026, 9, 27, 21, 50, tzinfo=UTC)
zone = ZoneInfo("America/New_York")
settings = {"name": "Provincetown", "time_zone": str(zone), "units": "ft"}
events = parse_predictions(
    json.loads((ROOT / "tests/fixtures/provincetown_hilo.json").read_text()), events=True
)
samples = parse_predictions(
    json.loads((ROOT / "tests/fixtures/provincetown_6.json").read_text()), events=False
)
for theme in ("dark", "light"):
    for days in (1, 7):
        (ROOT / f"docs/tide-{days}-{theme}.png").write_bytes(
            render_graph(events, samples, now, settings, theme, days)
        )

# A code-native wave mark; bundled as PNG for HA's local integration brand support.
icon = Image.new("RGBA", (512, 512), "#101f2b")
draw = ImageDraw.Draw(icon)

for row, color in ((190, "#73dbc7"), (270, "#efd19a"), (350, "#73dbc7")):
    coords = [(x, row + 34 * math.sin((x - 70) / 370 * 2 * math.pi)) for x in range(70, 443)]
    draw.line(coords, fill=color, width=18)
icon.save(ROOT / "custom_components/tideglass/brand/icon.png")

tides = select_tides(events, now)


def time(tide):
    return tide.time.astimezone(zone).strftime("%-I:%M %p")


stats = "".join(
    f'<div class="stat"><span>{label}</span><strong>{time(tide)}</strong><small>{tide.height:.2f} ft · MLLW</small></div>'
    for label, tide in (("NEXT LOW", tides["next_low"]), ("NEXT HIGH", tides["next_high"]))
)
forecast = ""
path = ROOT / ".local/nws-forecast.json"
if path.exists():
    periods = json.loads(path.read_text())["properties"]["periods"][:5]
    forecast = "".join(
        f"<div><span>{escape(p['name'])}</span><b>{p['temperature']}°</b><small>{escape(p['shortForecast'])}</small></div>"
        for p in periods
    )
week = ""
for day in range(27, 34):
    date = now.astimezone(zone).date() + timedelta(days=day - 27)
    today = [e for e in events if e.time.astimezone(zone).date() == date]
    week += (
        '<div class="day"><b>'
        + date.strftime("%a %d")
        + "</b><div>"
        + "".join(
            f"<span><i>{'↗' if e.kind == 'high' else '↘'}</i> {time(e)} <small>{e.height:.2f} ft</small></span>"
            for e in today
        )
        + "</div></div>"
    )

html = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tideglass · Coast preview</title>
<style>
:root{color-scheme:dark;--bg:#0b1720;--card:#101f2b;--ink:#edf5f2;--muted:#91abb5;--line:#263b46;--sea:#73dbc7;--gold:#efd19a}
body.light{color-scheme:light;--bg:#ebeee7;--card:#f4f5ef;--ink:#163d49;--muted:#577580;--line:#dce4df;--sea:#147c7c;--gold:#97641e}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:inherit;text-decoration:none}button{font:inherit;color:var(--ink);border:1px solid var(--line);background:var(--card);border-radius:100px;padding:9px 18px;cursor:pointer}header{border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:20px 5vw;gap:12px}.brand{letter-spacing:.23em;font-size:15px}.brand i{color:var(--sea);font-size:25px;vertical-align:middle;font-style:normal;margin-right:10px}nav{display:flex;align-items:center;gap:28px;font-size:14px;color:var(--muted)}main{max-width:1260px;margin:auto;padding:38px 28px 70px}.intro{display:flex;align-items:end;justify-content:space-between;gap:20px;margin-bottom:26px}.eyebrow{color:var(--sea);font-size:11px;letter-spacing:.2em;font-weight:600}h1{font-size:clamp(30px,4vw,48px);line-height:1.1;font-weight:450;letter-spacing:-.035em;margin:12px 0}p{margin:8px 0;color:var(--muted)}.stamp{font-size:12px;max-width:230px;text-align:right;color:var(--muted)}.card{background:var(--card);border:1px solid var(--line);border-radius:22px;overflow:hidden}.weather{padding:26px 30px;display:flex;gap:30px;margin-bottom:20px}.current{min-width:235px;border-right:1px solid var(--line);padding-right:28px}.current b{font-size:62px;font-weight:350;letter-spacing:-.05em;display:inline-block;margin-right:16px}.current span{color:var(--muted)}.current p{font-size:12px}.forecast{flex:1;display:grid;grid-template-columns:repeat(5,1fr);gap:18px;align-items:center}.forecast div{display:flex;flex-direction:column;gap:5px}.forecast span{font-size:12px;color:var(--muted)}.forecast b{font-weight:500;font-size:27px}.forecast small{font-size:11px;color:var(--muted)}.graph{width:100%;height:auto;display:block}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px}.stat{padding:22px 25px}.stat span{font-size:11px;letter-spacing:.16em;color:var(--sea);display:block}.stat strong{font-size:31px;font-weight:450;display:block;margin:8px 0}.stat small{color:var(--muted)}.stats{display:grid;grid-template-columns:repeat(3,1fr);margin-top:20px}.stats .stat+.stat{border-left:1px solid var(--line)}.map-head{padding:21px 24px;display:flex;align-items:center;justify-content:space-between}.map-head h2{font-size:20px;margin:0;font-weight:450}.tag{font-size:10px;letter-spacing:.1em;color:var(--sea);border:1px solid var(--line);border-radius:30px;padding:4px 9px}iframe{display:block;width:100%;height:390px;border:0;background:var(--card)}.section-head{display:flex;align-items:center;justify-content:space-between;margin:35px 2px 18px}.section-head h2{font-size:26px;font-weight:450;margin:0}.section-head p{font-size:12px}.calendar{padding:4px 24px;margin-top:20px}.day{display:grid;grid-template-columns:85px 1fr;padding:15px 0;border-bottom:1px solid var(--line);align-items:center}.day:last-child{border:0}.day b{font-size:14px;font-weight:500}.day>div{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.day span{font-size:13px}.day i{font-style:normal;color:var(--sea)}.day small{color:var(--muted);margin-left:5px;font-size:11px}footer{font-size:12px;color:var(--muted);margin-top:24px;display:flex;justify-content:space-between;gap:20px}
@media(max-width:800px){main{padding:25px 16px}header{padding:15px 18px}nav a{display:none}.intro{display:block}.stamp{text-align:left;max-width:none;margin-top:15px}.weather{display:block;padding:22px}.current{border:0;padding:0 0 18px}.forecast{display:flex;gap:18px;overflow:auto}.forecast div{flex:0 0 86px}.grid{grid-template-columns:1fr}.stats{grid-template-columns:1fr 1fr}.stats .stat:last-child{grid-column:1/-1;border-left:0;border-top:1px solid var(--line)}.stat{padding:18px}.day{grid-template-columns:65px 1fr}.day>div{grid-template-columns:1fr 1fr;gap:8px}.day small{display:block;margin-left:15px}iframe{height:340px}.section-head{align-items:start;gap:18px}.section-head p{text-align:right}footer{display:block}.graph-wrap{overflow:auto}.graph-wrap img{min-width:0}button{font-size:12px;padding:8px 12px}}
</style></head><body><header><a href="#" class="brand"><i>≈</i>TIDEGLASS</a><nav><a href="#today">Today</a><a href="#maps">Radar & wind</a><a href="#week">The week</a><button id="theme">Light appearance</button></nav></header><main><div class="intro"><div><span class="eyebrow">PROVINCETOWN, MASSACHUSETTS</span><h1>At the water’s edge.</h1><p>Weather, wind & the rhythm of the harbor.</p></div><div class="stamp">Design preview · September 27, 2026<br>Tide snapshot at 5:50 PM EDT</div></div>
<section class="card weather"><div class="current"><span>Provincetown · NWS</span><div><b>61°</b><span>Fog</span></div><p>Weather snapshot · Humidity 100%</p></div><div class="forecast">FORECAST</div></section>
<section id="today" class="card graph-wrap"><img class="graph" data-days="1" src="tide-1-dark.png" alt="NOAA tide curve for Provincetown with a now marker"></section>
<section class="card stats">STATS<div class="stat"><span>THE TIDE IS</span><strong>Falling ↘</strong><small>NOAA station 8446121</small></div></section>
<div id="maps" class="grid"><section class="card"><div class="map-head"><h2>Weather radar</h2><span class="tag">LIVE MAP</span></div><iframe title="Provincetown weather radar" src="https://embed.windy.com/embed.html?type=map&amp;location=coordinates&amp;metricRain=in&amp;metricTemp=%C2%B0F&amp;metricWind=mph&amp;zoom=8&amp;overlay=radar&amp;product=radar&amp;level=surface&amp;lat=42.05&amp;lon=-70.18&amp;marker=true"></iframe></section><section class="card"><div class="map-head"><h2>Wind over the Cape</h2><span class="tag">WINDY</span></div><iframe title="Provincetown wind forecast" src="https://embed.windy.com/embed.html?type=map&amp;location=coordinates&amp;metricRain=in&amp;metricTemp=%C2%B0F&amp;metricWind=mph&amp;zoom=8&amp;overlay=wind&amp;product=ecmwf&amp;level=surface&amp;lat=42.05&amp;lon=-70.18&amp;marker=true"></iframe></section></div>
<div id="week" class="section-head"><h2>A week by the water.</h2><p>Highs, lows, and the rhythm between.</p></div><section class="card graph-wrap"><img class="graph" data-days="7" src="tide-7-dark.png" alt="Seven-day NOAA tide prediction curve"></section><section class="card calendar">WEEK</section><footer><span>NOAA tide predictions · NWS weather · Windy maps</span><span>Layout preview. Live HA installation is pending.</span></footer></main><script>document.getElementById('theme').onclick=()=>{const light=document.body.classList.toggle('light');document.querySelectorAll('[data-days]').forEach(el=>el.src=`tide-${el.dataset.days}-${light?'light':'dark'}.png`);document.getElementById('theme').textContent=light?'Dark appearance':'Light appearance'}</script></body></html>"""
(ROOT / "docs/preview.html").write_text(
    html.replace("FORECAST", forecast).replace("STATS", stats).replace("WEEK", week)
)
print("Wrote graph assets, integration icon, and docs/preview.html")
