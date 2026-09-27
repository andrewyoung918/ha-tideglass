"""Timezone-safe tide calculations, independent of Home Assistant."""

from bisect import bisect_right
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from math import cos, isfinite, pi
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class Tide:
    time: datetime
    height: float
    kind: str

    def as_dict(self):
        return {"time": self.time.isoformat(), "height": self.height, "type": self.kind}


@dataclass(frozen=True)
class Sample:
    time: datetime
    height: float


def parse_predictions(payload: dict, *, events: bool):
    """Reject corrupt responses rather than turning missing heights into zero."""
    rows = payload.get("predictions")
    if not isinstance(rows, list) or not rows:
        raise ValueError("NOAA returned no predictions")
    result = []
    for row in rows:
        when = datetime.strptime(row["t"], "%Y-%m-%d %H:%M").replace(tzinfo=UTC)
        height = float(row["v"])
        if not isfinite(height):
            raise ValueError("Non-finite tide height")
        if events:
            kind = {"H": "high", "L": "low"}[row["type"]]
            result.append(Tide(when, height, kind))
        else:
            result.append(Sample(when, height))
    result.sort(key=lambda item: item.time)
    if any(a.time >= b.time for a, b in zip(result, result[1:])):
        raise ValueError("Duplicate tide timestamps")
    return tuple(result)


def local_window(now: datetime, time_zone: str, days: int = 1):
    """Local midnight boundaries expressed in UTC; DST days may be 23/25 hours."""
    start = now.astimezone(ZoneInfo(time_zone)).replace(hour=0, minute=0, second=0, microsecond=0)
    return start.astimezone(UTC), (start + timedelta(days=days)).astimezone(UTC)


def select_tides(events, now):
    previous = next((e for e in reversed(events) if e.time <= now), None)
    upcoming = [e for e in events if e.time > now]
    return {
        "last": previous,
        "next": next(iter(upcoming), None),
        "next_low": next((e for e in upcoming if e.kind == "low"), None),
        "next_high": next((e for e in upcoming if e.kind == "high"), None),
    }


def height_at(samples, now):
    """Interpolate only between genuine NOAA samples. Never extrapolate."""
    if len(samples) < 2 or now < samples[0].time or now > samples[-1].time:
        return None
    i = min(bisect_right([s.time for s in samples], now), len(samples) - 1)
    a, b = samples[i - 1], samples[i]
    if b.time - a.time > timedelta(minutes=7):
        return None
    fraction = (now - a.time).total_seconds() / (b.time - a.time).total_seconds()
    return a.height + (b.height - a.height) * fraction


def illustrative_samples(events):
    """For subordinate stations: an explicitly illustrative cosine curve only."""
    result = []
    for a, b in zip(events, events[1:]):
        count = max(2, int((b.time - a.time).total_seconds() / 360))
        for i in range(count):
            f = i / count
            result.append(
                Sample(
                    a.time + (b.time - a.time) * f, a.height + (b.height - a.height) * (1 - cos(pi * f)) / 2
                )
            )
    if events:
        result.append(Sample(events[-1].time, events[-1].height))
    return tuple(result)
