"""Dashboard-ready light and dark tide image entities."""

from functools import partial

from homeassistant.components.image import ImageEntity
from homeassistant.core import callback

from .entity import TideEntity
from .graph import render_graph


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    async_add_entities(
        TideImage(hass, coordinator, theme, days) for days in (1, 7) for theme in ("dark", "light")
    )


class TideImage(TideEntity, ImageEntity):
    _attr_content_type = "image/png"

    def __init__(self, hass, coordinator, theme, days):
        ImageEntity.__init__(self, hass)
        label = "Today" if days == 1 else "Week"
        TideEntity.__init__(self, coordinator, f"{label.lower()}_{theme}", f"{label} {theme}")
        self.theme, self.days = theme, days
        self._rendered = None
        self._attr_image_last_updated = coordinator.data["now"]

    @callback
    def _handle_coordinator_update(self):
        if self.coordinator.last_update_success:
            self._attr_image_last_updated = self.coordinator.data["now"]
        self._rendered = None
        super()._handle_coordinator_update()

    async def async_image(self):
        if not self.available:
            return None
        if self._rendered is None:
            now = self.coordinator.data["now"]
            data = await self.hass.async_add_executor_job(
                partial(
                    render_graph,
                    self.coordinator.events,
                    self.coordinator.samples,
                    now,
                    self.coordinator.settings,
                    self.theme,
                    self.days,
                )
            )
            if self.coordinator.data["now"] == now:
                self._rendered = data
            return data
        return self._rendered
