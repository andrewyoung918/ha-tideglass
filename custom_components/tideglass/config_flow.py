"""UI setup and options; station IDs are validated against NOAA."""

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util

from .api import NOAAClient, NOAAError, station_id
from .const import DEFAULT_STATION, DEFAULT_TIME_ZONE, DOMAIN
from .model import select_tides


def settings_schema(values):
    return {
        vol.Required("units", default=values.get("units", "ft")): vol.In(["ft", "m"]),
        vol.Required("time_zone", default=values.get("time_zone", DEFAULT_TIME_ZONE)): str,
    }


class TideglassFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                station = station_id(user_input["station"])
                ZoneInfo(user_input["time_zone"])
                await self.async_set_unique_id(station)
                self._abort_if_unique_id_configured()
                client = NOAAClient(async_get_clientsession(self.hass), station)
                metadata = await client.metadata()
                now = dt_util.utcnow()
                events, _ = await client.forecast(now, user_input["time_zone"], user_input["units"], False)
                if not all(select_tides(events, now).values()):
                    raise NOAAError("Incomplete forecast")
            except ZoneInfoNotFoundError:
                errors["time_zone"] = "invalid_time_zone"
            except ValueError:
                errors["station"] = "invalid_station"
            except NOAAError:
                errors["base"] = "no_predictions"
            except aiohttp.ClientError, TimeoutError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title=metadata["name"], data={**user_input, **metadata})
        values = user_input or {}
        return self.async_show_form(
            step_id="user",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required("station", default=values.get("station", DEFAULT_STATION)): str,
                    **settings_schema(values),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TideglassOptions()


class TideglassOptions(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                ZoneInfo(user_input["time_zone"])
            except ZoneInfoNotFoundError, ValueError:
                errors["time_zone"] = "invalid_time_zone"
            else:
                return self.async_create_entry(data=user_input)
        return self.async_show_form(
            step_id="init",
            errors=errors,
            data_schema=vol.Schema(
                settings_schema(user_input or (self.config_entry.data | self.config_entry.options))
            ),
        )
