"""Buttons for file operations and explicitly requested CNCjs commands."""
from homeassistant.components.button import ButtonEntity
from .const import DOMAIN

ACTIONS = (
    ("refresh", "Odśwież pliki", "mdi:refresh"),
    ("load", "Załaduj plik", "mdi:upload"),
    ("start", "Start (zablokowany)", "mdi:play"),
    ("pause", "Pauza", "mdi:pause"),
    ("resume", "Wznów (zablokowany)", "mdi:play-pause"),
    ("stop", "Stop", "mdi:stop"),
)
async def async_setup_entry(hass, entry, async_add_entities):
    manager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GCodeButton(manager, action, name, icon) for action,name,icon in ACTIONS])

class GCodeButton(ButtonEntity):
    _attr_has_entity_name = True
    def __init__(self, manager, action, name, icon):
        self.manager, self.action = manager, action
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{manager.entry.entry_id}_gcode_{action}"
    async def async_press(self):
        if self.action == "refresh":
            await self.manager.async_refresh()
        elif self.action == "load":
            await self.manager.async_load()
        else:
            await self.manager.async_command(self.action)
