from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.tideglass.api import NOAAClient, NOAAError, station_id


def test_station_validation():
    assert station_id(" Provincetown ") == "8446121"
    assert station_id("9414290") == "9414290"
    for invalid in ("123", "../../secrets", "https://example.com", "8446121?x=1"):
        with pytest.raises(ValueError):
            station_id(invalid)


async def test_request_always_uses_utc_and_mllw():
    client = NOAAClient(MagicMock(), "8446121")
    client._get = AsyncMock(
        return_value={"predictions": [{"t": "2026-09-27 12:00", "v": "-0.5", "type": "L"}]}
    )
    begin = datetime(2026, 9, 27, tzinfo=UTC)
    events = await client.predictions(begin, begin, "m")
    params = client._get.call_args.args[1]
    assert params["time_zone"] == "gmt"
    assert params["datum"] == "MLLW"
    assert params["units"] == "metric"
    assert events[0].height == -0.5


async def test_empty_prediction_response_fails():
    client = NOAAClient(MagicMock(), "8446121")
    client._get = AsyncMock(return_value={"predictions": []})
    now = datetime.now(UTC)
    with pytest.raises(NOAAError):
        await client.predictions(now, now, "ft")


async def test_subordinate_metadata():
    client = NOAAClient(MagicMock(), "8446121")
    client._get = AsyncMock(
        side_effect=[{"stations": [{"name": "Example", "lat": 42, "lng": -70}]}, {"type": "S"}]
    )
    assert (await client.metadata())["harmonic"] is False
