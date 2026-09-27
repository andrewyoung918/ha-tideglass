"""Locally rendered, antialiased tide graphs. No remote rendering services."""

from datetime import timedelta
from io import BytesIO
from math import ceil, floor
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

from .model import Sample, height_at, illustrative_samples, local_window

PALETTES = {
    "dark": {
        "bg": "#101f2b",
        "ink": "#edf5f2",
        "muted": "#91abb5",
        "grid": "#283e4a",
        "accent": "#73dbc7",
        "fill": "#193c45",
        "gold": "#efd19a",
        "pill": "#223c47",
    },
    "light": {
        "bg": "#f4f5ef",
        "ink": "#163d49",
        "muted": "#577580",
        "grid": "#dce4df",
        "accent": "#147c7c",
        "fill": "#d6e8df",
        "gold": "#97641e",
        "pill": "#e1e9e1",
    },
}


def render_graph(events, samples, now, settings, theme="dark", days=1):
    """Render an actual data plot with local-time ticks and a minute-level now marker."""
    p = PALETTES[theme]
    scale, width, height = 2, 1200, 650
    im = Image.new("RGB", (width * scale, height * scale), p["bg"])
    d = ImageDraw.Draw(im)

    def text(x, y, value, size=20, color="ink", anchor=None):
        d.text(
            (x * scale, y * scale),
            value,
            font=ImageFont.load_default(size=size * scale),
            fill=p.get(color, color),
            anchor=anchor,
        )

    def line(coords, color="grid", w=1):
        d.line(
            [(int(x * scale), int(y * scale)) for x, y in coords],
            fill=p[color],
            width=w * scale,
            joint="curve",
        )

    def dot(x, y, r, color):
        d.ellipse(((x - r) * scale, (y - r) * scale, (x + r) * scale, (y + r) * scale), fill=p[color])

    zone = ZoneInfo(settings["time_zone"])
    start, end = local_window(now, settings["time_zone"], days)
    actual = bool(samples)
    points = samples if actual else illustrative_samples(events)
    points = [s for s in points if start <= s.time <= end]
    for boundary in (start, end):
        value = height_at(samples if actual else illustrative_samples(events), boundary)
        if value is not None:
            points.append(Sample(boundary, value))
    points.sort(key=lambda s: s.time)
    text(44, 32, "T I D E G L A S S   /   " + ("TODAY" if days == 1 else "SEVEN DAYS"), 16, "muted")
    title = settings["name"]
    if len(title) > 35:
        title = title[:32] + "…"
    text(44, 65, title, 42)
    date_label = now.astimezone(zone).strftime("%A, %B %-d")
    text(44, 122, date_label + "  ·  " + settings["time_zone"], 17, "muted")
    next_tide = next((e for e in events if e.time > now), None)
    if next_tide:
        text(1156, 65, "NEXT " + next_tide.kind.upper(), 15, "accent", "ra")
        text(1156, 92, next_tide.time.astimezone(zone).strftime("%-I:%M %p"), 32, "ink", "ra")
        text(1156, 133, f"{next_tide.height:.2f} {settings['units']} MLLW", 17, "muted", "ra")
    if len(points) < 2:
        text(44, 280, "Prediction curve unavailable", 30, "muted")
    else:
        left, right, top, bottom = 76, 1156, 218, 466
        low, high = min(s.height for s in points), max(s.height for s in points)
        padding = max((high - low) * 0.18, 0.15)
        lo, hi = low - padding, high + padding
        duration = (end - start).total_seconds()

        def x(when):
            return left + (when - start).total_seconds() / duration * (right - left)

        def y(value):
            return bottom - (value - lo) / (hi - lo) * (bottom - top)

        tick_step = max(0.5 if settings["units"] == "m" else 2, ceil((hi - lo) / 5))
        for i in range(ceil(lo / tick_step), floor(hi / tick_step) + 1):
            value = i * tick_step
            line([(left, y(value)), (right, y(value))])
            text(left - 16, y(value), f"{value:g}", 15, "muted", "rm")
        text(44, 190, settings["units"] + " · MLLW", 13, "muted")
        coords = [(x(s.time), y(s.height)) for s in points]
        polygon = [(coords[0][0], bottom), *coords, (coords[-1][0], bottom)]
        d.polygon([(int(a * scale), int(b * scale)) for a, b in polygon], fill=p["fill"])
        line(coords, "accent", 3)
        if days == 1:
            cursor = start
            while cursor <= end:
                local = cursor.astimezone(zone)
                if local.hour % 3 == 0 and local.minute == 0:
                    label = local.strftime("%-I%p").lower()
                    text(x(cursor), bottom + 22, label, 15, "muted", "mt")
                cursor += timedelta(hours=1)
        else:
            for i in range(days):
                local = start.astimezone(zone) + timedelta(days=i, hours=12)
                text(x(local), bottom + 22, local.strftime("%a %-d"), 15, "muted", "mt")
        if start <= now < end:
            nx = x(now)
            for yy in range(top - 22, bottom, 9):
                line([(nx, yy), (nx, min(yy + 4, bottom))], "gold", 1)
            text(min(max(nx, left + 20), right - 20), top - 46, "NOW", 13, "gold", "mt")
            value = height_at(points, now)
            if value is not None:
                dot(nx, y(value), 8, "bg")
                dot(nx, y(value), 4, "gold")
        if days == 1:
            today = [e for e in events if start <= e.time < end]
            # Event labels live in an even-width strip so adjacent curve labels never collide.
            for i, event in enumerate(today):
                ex = 44 + i * (1112 / max(1, len(today)))
                text(ex, 534, event.kind.upper(), 13, "accent")
                text(ex, 557, event.time.astimezone(zone).strftime("%-I:%M %p"), 24)
                text(ex, 590, f"{event.height:.2f} {settings['units']}", 16, "muted")
                dot(x(event.time), y(event.height), 4, "accent")
        else:
            text(44, 548, "A week at the water’s edge.", 27)
            text(44, 588, "Highs, lows, and the rhythm between.", 17, "muted")
    footer = "NOAA predictions" if actual else "NOAA high/low times · illustrative curve"
    text(1156, 629, footer + "  ·  Not observed water level", 12, "muted", "ra")
    output = BytesIO()
    im.resize((width, height), Image.Resampling.LANCZOS).save(output, "PNG", optimize=True)
    return output.getvalue()
