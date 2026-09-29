"""Timeline data stays authorized, bounded, and honest across DST and outages."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from custom_components.tideglass.frontend import timeline_data, websocket_timeline


async def test_timeline_websocket(hass, loaded, hass_ws_client):
    client = await hass_ws_client(hass)
    await client.send_json(
        {"id": 1, "type": "tideglass/timeline", "entity_id": "sensor.provincetown_tideglass_week"}
    )
    response = await client.receive_json()
    assert response["success"]
    data = response["result"]
    assert len(data["days"]) == 7
    assert len(data["samples"]) == 1681
    assert data["curve"] == "prediction"
    assert data["unit"] == "ft"
    assert all(len(day["weather_slots"]) == 6 for day in data["days"])
    assert data["days"][0]["sunrise"].startswith("2026-09-27T06:")
    assert not data["days"][0]["starts_in_daylight"]


async def test_card_asset_served(hass, loaded, hass_client):
    client = await hass_client()
    response = await client.get("/tideglass/tideglass-card.js")
    assert response.status == 200
    assert "class TideglassCard" in await response.text()


@pytest.mark.parametrize("entity", ["sensor.missing", "sun.sun"])
async def test_wrong_entity(hass, loaded, hass_ws_client, entity):
    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": "tideglass/timeline", "entity_id": entity})
    assert not (await client.receive_json())["success"]


async def test_permission_before_data(hass, loaded):
    connection = MagicMock()
    connection.user.permissions.check_entity.return_value = False
    websocket_timeline(hass, connection, {"id": 1, "entity_id": "sensor.provincetown_tideglass_week"})
    connection.send_error.assert_called_once_with(1, "unauthorized", "Entity is not readable")
    connection.send_result.assert_not_called()


async def test_outage_expiry(hass, loaded, hass_ws_client):
    client = await hass_ws_client(hass)
    c = loaded.runtime_data
    c.fetched -= timedelta(hours=49)
    await client.send_json(
        {"id": 1, "type": "tideglass/timeline", "entity_id": "sensor.provincetown_tideglass_week"}
    )
    assert (await client.receive_json())["error"]["code"] == "unavailable"


@pytest.mark.parametrize(("date", "hours"), [("2026-03-08", 23), ("2026-11-01", 25)])
async def test_local_days_dst(loaded, date, hours):
    data = timeline_data(loaded.runtime_data, datetime.fromisoformat(date + "T17:00:00+00:00"))
    day = data["days"][0]
    begin, end = [datetime.fromisoformat(day[k]).astimezone(UTC) for k in ["start", "end"]]
    assert (end - begin).total_seconds() / 3600 == hours
    assert [datetime.fromisoformat(t).hour for t in day["weather_slots"]] == [0, 4, 8, 12, 16, 20]


async def test_subordinate_curve_and_polar_day(loaded):
    c = loaded.runtime_data
    c.samples = ()
    c.settings = c.settings | {"latitude": 71.29, "longitude": -156.79}
    data = timeline_data(c, datetime(2026, 6, 21, 17, tzinfo=UTC))
    assert data["curve"] == "illustrative"
    assert data["days"][0]["sunrise"] is None
    assert data["days"][0]["sunset"] is None
    assert data["days"][0]["starts_in_daylight"]
