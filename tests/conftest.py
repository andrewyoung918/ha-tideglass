"""Tests use real NOAA response fixtures, never the network."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.tideglass.model import parse_predictions

SETTINGS = {
    "station": "8446121",
    "name": "Provincetown",
    "latitude": 42.04959,
    "longitude": -70.18216,
    "harmonic": True,
    "units": "ft",
    "time_zone": "America/New_York",
}


@pytest.fixture(autouse=True)
def custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture
def predictions():
    directory = Path(__file__).parent / "fixtures"
    return (
        parse_predictions(json.loads((directory / "provincetown_hilo.json").read_text()), events=True),
        parse_predictions(json.loads((directory / "provincetown_6.json").read_text()), events=False),
    )


@pytest.fixture
def entry():
    return MockConfigEntry(domain="tideglass", title="Provincetown", unique_id="8446121", data=SETTINGS)


@pytest.fixture
async def loaded(hass, entry, predictions, freezer):
    freezer.move_to("2026-09-27T17:00:00+00:00")
    entry.add_to_hass(hass)
    with patch("custom_components.tideglass.api.NOAAClient.forecast", return_value=predictions):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        yield entry
        await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
