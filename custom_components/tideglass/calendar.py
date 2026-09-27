"""Read-only tide calendar, including reliable native calendar triggers."""

from datetime import timedelta

import aiohttp
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util

from .api import NOAAError
from .entity import TideEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([TideCalendar(entry.runtime_data)])


class TideCalendar(TideEntity, CalendarEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator, "tides", "Tides")

    def _event(self, tide):
        s = self.coordinator.settings
        return CalendarEvent(
            start=tide.time,
            end=tide.time + timedelta(minutes=1),
            summary=f"{tide.kind.title()} tide · {tide.height:.2f} {s['units']}",
            description=f"NOAA {s['station']} · predicted {tide.kind} tide · MLLW",
            location=s["name"],
            uid=f"{s['station']}-{tide.time.isoformat()}",
        )

    @property
    def event(self):
        now = dt_util.utcnow()
        tide = next((t for t in self.coordinator.events if t.time + timedelta(minutes=1) > now), None)
        return self._event(tide) if tide else None

    async def async_get_events(self, hass, start_date, end_date):
        if not self.available:
            raise HomeAssistantError("Tide predictions are unavailable")
        if end_date <= start_date:
            return []
        # Fetch any requested window rather than silently truncating a calendar month.
        # NOAA allows up to one year of high/low predictions; cap our requests to 31 days.
        events = []
        cursor = dt_util.as_utc(start_date) - timedelta(minutes=1)
        end = dt_util.as_utc(end_date)
        if end - cursor > timedelta(days=367):
            raise HomeAssistantError("Request at most one year of tides at a time")
        if self.coordinator.events[0].time <= cursor and end <= self.coordinator.events[-1].time:
            events = self.coordinator.events
        else:
            while cursor < end:
                limit = min(end, cursor + timedelta(days=31))
                try:
                    events.extend(
                        await self.coordinator.client.predictions(
                            cursor, limit, self.coordinator.settings["units"]
                        )
                    )
                except (aiohttp.ClientError, TimeoutError, NOAAError) as err:
                    raise HomeAssistantError("Unable to load NOAA tide calendar") from err
                cursor = limit
        unique = {e.time: e for e in events}
        return [
            self._event(e)
            for e in sorted(unique.values(), key=lambda e: e.time)
            if e.time < end_date and e.time + timedelta(minutes=1) > start_date
        ]
