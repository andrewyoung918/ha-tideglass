from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.tideglass.api import NOAAError
from custom_components.tideglass.coordinator import TideCoordinator

from .conftest import SETTINGS


async def test_full_setup_entities_and_unload(hass, loaded):
    registry = er.async_get(hass)
    entries = er.async_entries_for_config_entry(registry, loaded.entry_id)
    assert len(entries) == 20
    time = hass.states.get("sensor.provincetown_tideglass_next_high_time")
    assert time.attributes["device_class"] == "timestamp"
    assert datetime.fromisoformat(time.state).tzinfo is not None
    low = hass.states.get("sensor.provincetown_tideglass_next_low_height")
    assert float(low.state) == pytest.approx(-0.539)
    assert low.attributes["unit_of_measurement"] == "ft"
    week = hass.states.get("sensor.provincetown_tideglass_week")
    assert 24 <= int(week.state) <= 30
    assert len(week.attributes["tides"]) == int(week.state)
    assert hass.states.get("binary_sensor.provincetown_tideglass_tide_rising").state == "off"
    assert hass.states.get("image.provincetown_tideglass_today_dark").state != "unknown"


async def test_cached_outage_then_expiry(hass, loaded, freezer):
    c = loaded.runtime_data
    with patch.object(c.client, "forecast", side_effect=NOAAError("offline")) as fetch:
        freezer.tick(timedelta(hours=7))
        data = await c._async_update_data()
        assert data["source_status"] == "cached"
        assert data["next"].time > data["now"]
        await c._async_update_data()
        assert fetch.call_count == 1
        freezer.tick(timedelta(hours=42))
        with pytest.raises(UpdateFailed, match="expired"):
            await c._async_update_data()


async def test_offline_startup_uses_saved_cache(hass, loaded, freezer):
    c = TideCoordinator(hass, loaded)
    await c.load_cache()
    assert c.events == loaded.runtime_data.events
    freezer.tick(timedelta(hours=7))
    with patch.object(c.client, "forecast", side_effect=NOAAError("offline")):
        assert (await c._async_update_data())["source_status"] == "cached"


async def test_options_change_does_not_reuse_wrong_units(hass, loaded):
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    changed = MockConfigEntry(
        domain="tideglass", entry_id=loaded.entry_id, data=SETTINGS, options={"units": "m"}
    )
    c = TideCoordinator(hass, changed)
    await c.load_cache()
    assert c.fetched is None


async def test_config_flow(hass, predictions, freezer):
    freezer.move_to("2026-09-27T17:00:00+00:00")
    with (
        patch("custom_components.tideglass.api.NOAAClient.metadata", return_value=SETTINGS),
        patch("custom_components.tideglass.api.NOAAClient.forecast", return_value=predictions),
    ):
        flow = await hass.config_entries.flow.async_init("tideglass", context={"source": "user"})
        assert flow["type"] == FlowResultType.FORM
        result = await hass.config_entries.flow.async_configure(
            flow["flow_id"], {"station": "Provincetown", "units": "ft", "time_zone": "America/New_York"}
        )
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["data"]["station"] == "8446121"
        await hass.async_block_till_done()


@pytest.mark.parametrize(
    ("input", "field", "error"),
    [
        ({"station": "nope", "units": "ft", "time_zone": "America/New_York"}, "station", "invalid_station"),
        ({"station": "8446121", "units": "ft", "time_zone": "Narnia/Sea"}, "time_zone", "invalid_time_zone"),
    ],
)
async def test_bad_config_input(hass, input, field, error):
    result = await hass.config_entries.flow.async_init("tideglass", context={"source": "user"}, data=input)
    assert result["errors"] == {field: error}


async def test_calendar_boundaries_and_external_window(hass, loaded):
    from custom_components.tideglass.calendar import TideCalendar

    calendar = TideCalendar(loaded.runtime_data)
    event = loaded.runtime_data.events[5]
    assert len(await calendar.async_get_events(hass, event.time, event.time + timedelta(minutes=1))) == 1
    assert (
        await calendar.async_get_events(
            hass, event.time + timedelta(minutes=1), event.time + timedelta(minutes=2)
        )
        == []
    )
    with patch.object(loaded.runtime_data.client, "predictions", return_value=[]) as fetch:
        assert (
            await calendar.async_get_events(
                hass, datetime(2026, 12, 1, tzinfo=UTC), datetime(2027, 1, 1, tzinfo=UTC)
            )
            == []
        )
        assert fetch.call_count == 2


async def test_image_is_served_by_home_assistant(hass, loaded, hass_client):
    client = await hass_client()
    state = hass.states.get("image.provincetown_tideglass_today_dark")
    response = await client.get(state.attributes["entity_picture"])
    assert response.status == 200
    assert response.content_type == "image/png"
    assert (await response.read()).startswith(b"\x89PNG")


async def test_clock_rolls_forward_without_network(hass, loaded, freezer):
    c = loaded.runtime_data
    with patch.object(c.client, "forecast") as fetch:
        old = c.data["next"]
        freezer.move_to(old.time + timedelta(seconds=1))
        data = await c._async_update_data()
        assert data["last"] == old
        assert data["next"].time > old.time
        fetch.assert_not_called()


async def test_offline_first_install_fails_safely(hass, entry, freezer):
    freezer.move_to("2026-09-27T17:00:00+00:00")
    c = TideCoordinator(hass, entry)
    with patch.object(c.client, "forecast", side_effect=NOAAError("offline")):
        with pytest.raises(UpdateFailed):
            await c._async_update_data()


async def test_duplicate_station_aborts(hass, entry):
    entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        "tideglass",
        context={"source": "user"},
        data={"station": "8446121", "units": "ft", "time_zone": "America/New_York"},
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"
