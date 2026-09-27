"""Small asynchronous client for the public NOAA CO-OPS APIs."""

import asyncio
import re
from datetime import timedelta

import aiohttp

from .const import DATA_URL, META_URL
from .model import local_window, parse_predictions


class NOAAError(Exception):
    """NOAA rejected a request or returned unusable data."""


def station_id(value):
    value = str(value).strip()
    if value.lower() in ("provincetown", "provincetown, ma"):
        return "8446121"
    if not re.fullmatch(r"\d{7}", value):
        raise ValueError("Use a seven-digit NOAA station ID")
    return value


class NOAAClient:
    def __init__(self, session: aiohttp.ClientSession, station: str):
        self.session = session
        self.station = station_id(station)

    async def _get(self, url, params=None):
        async with asyncio.timeout(25):
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                try:
                    data = await response.json()
                except ValueError as err:
                    raise NOAAError("NOAA returned invalid JSON") from err
        if not isinstance(data, dict) or "error" in data:
            raise NOAAError("NOAA returned an error; verify station prediction availability")
        return data

    async def metadata(self):
        payload = await self._get(f"{META_URL}/{self.station}.json")
        try:
            station = payload["stations"][0]
            offsets = await self._get(f"{META_URL}/{self.station}/tidepredoffsets.json")
            if offsets.get("type") not in ("R", "S"):
                raise NOAAError("Station does not support tide predictions")
            return {
                "station": self.station,
                "name": station["name"],
                "latitude": float(station["lat"]),
                "longitude": float(station["lng"]),
                "harmonic": offsets["type"] == "R",
            }
        except (KeyError, IndexError, TypeError, ValueError) as err:
            raise NOAAError("Invalid station metadata") from err

    async def predictions(self, begin, end, units, interval="hilo"):
        data = await self._get(
            DATA_URL,
            {
                "product": "predictions",
                "application": "HomeAssistant_Tideglass",
                "station": self.station,
                "begin_date": begin.strftime("%Y%m%d %H:%M"),
                "end_date": end.strftime("%Y%m%d %H:%M"),
                "datum": "MLLW",
                "time_zone": "gmt",
                "units": "english" if units == "ft" else "metric",
                "interval": interval,
                "format": "json",
            },
        )
        try:
            return parse_predictions(data, events=interval == "hilo")
        except (KeyError, ValueError, TypeError) as err:
            raise NOAAError("Malformed NOAA prediction data") from err

    async def forecast(self, now, time_zone, units, harmonic):
        start, end = local_window(now, time_zone, days=9)
        start -= timedelta(days=1)
        events = await self.predictions(start, end, units)
        samples = await self.predictions(start, end, units, "6") if harmonic else ()
        return events, samples
