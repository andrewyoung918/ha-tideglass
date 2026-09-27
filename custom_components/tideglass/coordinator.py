"""Cache predictions separately from the once-per-minute clock updates."""

import logging
from datetime import UTC, datetime, timedelta

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import NOAAClient, NOAAError
from .const import DOMAIN
from .model import Sample, Tide, height_at, local_window, select_tides

LOGGER = logging.getLogger(__name__)


class TideCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(hass, LOGGER, name=DOMAIN, config_entry=entry, update_interval=timedelta(minutes=1))
        self.settings = entry.data | entry.options
        self.client = NOAAClient(async_get_clientsession(hass), entry.data["station"])
        self.store = Store(hass, 1, f"{DOMAIN}.{entry.entry_id}")
        self.events = ()
        self.samples = ()
        self.fetched = None
        self.retry_at = datetime.min.replace(tzinfo=UTC)
        self.last_error = False

    async def load_cache(self):
        cache = await self.store.async_load()
        if not cache or cache.get("settings") != self.settings:
            return
        try:
            self.fetched = datetime.fromisoformat(cache["fetched"])
            self.events = tuple(
                Tide(datetime.fromisoformat(e["time"]), e["height"], e["type"]) for e in cache["events"]
            )
            self.samples = tuple(Sample(datetime.fromisoformat(s[0]), s[1]) for s in cache["samples"])
        except KeyError, TypeError, ValueError:
            self.fetched, self.events, self.samples = None, (), ()

    async def _async_update_data(self):
        now = dt_util.utcnow()
        zone = self.settings["time_zone"]
        due = (
            self.fetched is None
            or now - self.fetched >= timedelta(hours=6)
            or local_window(now, zone)[0] != local_window(self.fetched, zone)[0]
        )
        if due and now >= self.retry_at:
            try:
                events, samples = await self.client.forecast(
                    now, zone, self.settings["units"], self.settings["harmonic"]
                )
                if not all(select_tides(events, now).values()):
                    raise NOAAError("Predictions do not cover the current tide cycle")
                self.events, self.samples, self.fetched = events, samples, now
                self.last_error = False
                await self.store.async_save(
                    {
                        "settings": self.settings,
                        "fetched": now.isoformat(),
                        "events": [e.as_dict() for e in events],
                        "samples": [[s.time.isoformat(), s.height] for s in samples],
                    }
                )
            except (aiohttp.ClientError, TimeoutError, NOAAError) as err:
                self.last_error = True
                self.retry_at = now + timedelta(minutes=15)
                if self.fetched is None:
                    raise UpdateFailed(str(err)) from err
                LOGGER.debug("NOAA refresh failed; retaining bounded prediction cache: %s", err)
        if self.fetched is None or now - self.fetched > timedelta(hours=48):
            raise UpdateFailed("Tide predictions expired; NOAA refresh required")
        chosen = select_tides(self.events, now)
        if not all(chosen.values()):
            raise UpdateFailed("Tide predictions no longer cover the current cycle")
        start, end = local_window(now, zone, days=7)
        week = [e.as_dict() for e in self.events if start <= e.time < end]
        return {
            "now": now,
            **chosen,
            "week": week,
            "predicted_height": height_at(self.samples, now),
            "phase": "rising" if chosen["next"].kind == "high" else "falling",
            "source_status": "cached" if self.last_error else "fresh",
        }
