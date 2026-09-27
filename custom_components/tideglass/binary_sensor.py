"""Simple rising-tide signal."""

from homeassistant.components.binary_sensor import BinarySensorEntity

from .entity import TideEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([RisingTide(entry.runtime_data)])


class RisingTide(TideEntity, BinarySensorEntity):
    _attr_icon = "mdi:waves-arrow-up"

    def __init__(self, coordinator):
        super().__init__(coordinator, "rising", "Tide rising")

    @property
    def is_on(self):
        return self.coordinator.data["phase"] == "rising"
