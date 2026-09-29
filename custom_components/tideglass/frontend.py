"""Bundled card and authenticated, bounded prediction data for its timeline."""

from datetime import timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import voluptuous as vol
from astral import Observer
from astral.sun import elevation, sunrise, sunset
from homeassistant.auth.permissions.const import POLICY_READ
from homeassistant.components import frontend, websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .model import illustrative_samples, local_window

CARD_URL = "/tideglass/tideglass-card.js"
CARD_VERSION = "0.2.0"


async def async_setup_frontend(hass):
    """Register one public code asset; all station data requires authentication."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL, str(Path(__file__).parent / "frontend" / "tideglass-card.js"), False)]
    )
    frontend.add_extra_js_url(hass, f"{CARD_URL}?v={CARD_VERSION}")
    websocket_api.async_register_command(hass, websocket_timeline)


def timeline_data(coordinator, now):
    """Reuse NOAA cache, without extra external requests or recorder attributes."""
    settings = coordinator.settings
    zone = settings["time_zone"]
    tz = ZoneInfo(zone)
    start, end = local_window(now, zone, days=7)
    observer = Observer(settings["latitude"], settings["longitude"])
    days = []
    for i in range(7):
        midnight = start.astimezone(tz) + timedelta(days=i)
        next_midnight = midnight + timedelta(days=1)
        solar = {}
        for key, calculate in (("sunrise", sunrise), ("sunset", sunset)):
            try:
                solar[key] = calculate(observer, midnight.date(), tzinfo=tz).isoformat()
            except ValueError:  # Polar day/night has no sunrise/sunset crossing.
                solar[key] = None
        days.append(
            {
                "start": midnight.isoformat(),
                "end": next_midnight.isoformat(),
                **solar,
                "starts_in_daylight": elevation(observer, midnight) > -0.833,
                "weather_slots": [midnight.replace(hour=h).isoformat() for h in range(0, 24, 4)],
            }
        )
    samples = coordinator.samples or illustrative_samples(coordinator.events)
    return {
        "station": settings["name"],
        "station_id": settings["station"],
        "time_zone": zone,
        "unit": settings["units"],
        "datum": "MLLW",
        "start": start.isoformat(),
        "end": end.isoformat(),
        "fetched": coordinator.fetched.isoformat(),
        "status": coordinator.data["source_status"],
        "curve": "prediction" if coordinator.samples else "illustrative",
        "days": days,
        "events": [e.as_dict() for e in coordinator.events if start <= e.time < end],
        "samples": [[s.time.timestamp() * 1000, s.height] for s in samples if start <= s.time <= end],
    }


@websocket_api.websocket_command({vol.Required("type"): "tideglass/timeline", vol.Required("entity_id"): str})
@callback
def websocket_timeline(hass, connection, msg):
    """Select the correct entry by an existing readable Tideglass entity."""
    entity_id = msg["entity_id"]
    if not connection.user.permissions.check_entity(entity_id, POLICY_READ):
        connection.send_error(msg["id"], "unauthorized", "Entity is not readable")
        return
    entity = er.async_get(hass).async_get(entity_id)
    entry = hass.config_entries.async_get_entry(entity.config_entry_id) if entity else None
    coordinator = getattr(entry, "runtime_data", None) if entry and entry.domain == DOMAIN else None
    now = dt_util.utcnow()
    if (
        coordinator is None
        or not coordinator.last_update_success
        or coordinator.fetched is None
        or now - coordinator.fetched > timedelta(hours=48)
    ):
        connection.send_error(msg["id"], "unavailable", "Tide predictions are unavailable")
        return
    connection.send_result(msg["id"], timeline_data(coordinator, now))
