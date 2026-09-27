"""Common device identity and attribution."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN


class TideEntity(CoordinatorEntity):
    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator, key, name):
        super().__init__(coordinator)
        s = coordinator.settings
        self._attr_unique_id = f"{s['station']}_{key}"
        self._attr_name = name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, s["station"])},
            name=f"{s['name']} Tideglass",
            manufacturer="NOAA CO-OPS",
            model="Tide predictions",
            configuration_url=f"https://tidesandcurrents.noaa.gov/noaatidepredictions.html?id={s['station']}",
        )
