"""Native Home Assistant selector for local G-code files."""
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.core import callback
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([GCodeSelect(hass.data[DOMAIN][entry.entry_id])])

class GCodeSelect(SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Plik G-code"
    _attr_icon = "mdi:file-code-outline"
    def __init__(self, manager):
        self.manager = manager
        self._attr_unique_id = f"{manager.entry.entry_id}_gcode_select"
    @property
    def options(self):
        return self.manager.files or ["(brak plików)"]
    @property
    def current_option(self):
        return self.manager.selected or "(brak plików)"
    async def async_select_option(self, option):
        if option not in self.manager.files:
            return
        self.manager.selected = option
        self.manager.notify()
    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(async_dispatcher_connect(self.hass, self.manager.signal, self._update))
    @callback
    def _update(self):
        self.async_write_ha_state()
