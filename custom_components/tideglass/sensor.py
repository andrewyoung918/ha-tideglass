"""Typed timestamps and numeric heights for automations."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.entity import EntityCategory

from .entity import TideEntity

DESCRIPTIONS = (
    ("last_type", "Most recent tide", "last", "kind"),
    ("last_time", "Most recent tide time", "last", "time"),
    ("last_height", "Most recent tide height", "last", "height"),
    ("next_type", "Next tide", "next", "kind"),
    ("next_time", "Next tide time", "next", "time"),
    ("next_low_time", "Next low time", "next_low", "time"),
    ("next_high_time", "Next high time", "next_high", "time"),
    ("next_low_height", "Next low height", "next_low", "height"),
    ("next_high_height", "Next high height", "next_high", "height"),
    ("phase", "Tide direction", None, None),
    ("predicted_height", "Predicted height", None, "height"),
    ("week", "Week", None, None),
    ("source_status", "Prediction status", None, None),
    ("fetched", "Last NOAA update", None, "time"),
)


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(TideSensor(entry.runtime_data, *description) for description in DESCRIPTIONS)


class TideSensor(TideEntity, SensorEntity):
    def __init__(self, coordinator, key, name, event_key, field):
        super().__init__(coordinator, key, name)
        self.key, self.event_key, self.field = key, event_key, field
        self._attr_icon = "mdi:waves"
        if field == "time":
            self._attr_device_class = SensorDeviceClass.TIMESTAMP
        elif field == "height":
            self._attr_device_class = SensorDeviceClass.DISTANCE
            self._attr_native_unit_of_measurement = coordinator.settings["units"]
            self._attr_suggested_unit_of_measurement = coordinator.settings["units"]
            self._attr_suggested_display_precision = 2
        elif field == "kind" or key in ("phase", "source_status"):
            self._attr_device_class = SensorDeviceClass.ENUM
            self._attr_options = (
                ["high", "low"]
                if field == "kind"
                else ["rising", "falling"]
                if key == "phase"
                else ["fresh", "cached"]
            )
        if key in ("source_status", "fetched"):
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self):
        return super().available and (
            self.key != "predicted_height" or self.coordinator.data["predicted_height"] is not None
        )

    @property
    def native_value(self):
        data = self.coordinator.data
        if self.event_key:
            return getattr(data[self.event_key], self.field)
        if self.key == "week":
            return len(data["week"])
        if self.key == "fetched":
            return self.coordinator.fetched
        return data[self.key]

    @property
    def extra_state_attributes(self):
        attrs = {"station_id": self.coordinator.settings["station"], "datum": "MLLW"}
        attrs["data_type"] = "prediction"
        if self.key == "week":
            attrs.update(
                {
                    "tides": self.coordinator.data["week"],
                    "time_zone": self.coordinator.settings["time_zone"],
                    "height_unit": self.coordinator.settings["units"],
                    "forecast_start": self.coordinator.events[0].time.isoformat(),
                    "forecast_end": self.coordinator.events[-1].time.isoformat(),
                }
            )
        if self.key == "predicted_height":
            attrs["method"] = "NOAA six-minute predictions; linear interpolation between samples"
        return attrs
