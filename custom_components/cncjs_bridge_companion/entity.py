"""Entities that mirror the existing bridge's Home Assistant state."""
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change_event
from .const import CONF_SOURCE_ENTITY


class BridgeEntity(Entity):
    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, entry, key, name):
        self._source = entry.data[CONF_SOURCE_ENTITY]
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name

    @property
    def available(self):
        state = self.hass.states.get(self._source)
        return state is not None and state.state not in ("unknown", "unavailable")

    def _source_state(self):
        return self.hass.states.get(self._source)

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(async_track_state_change_event(
            self.hass, [self._source], self._on_source_change
        ))

    def _on_source_change(self, event):
        self.async_write_ha_state()
