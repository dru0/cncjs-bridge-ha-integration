"""Mirror the CNCjs bridge status without altering the original entity."""
from homeassistant.components.sensor import SensorEntity
from .entity import BridgeEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([BridgeStatusSensor(entry)])


class BridgeStatusSensor(BridgeEntity, SensorEntity):
    def __init__(self, entry):
        super().__init__(entry, "status", "Status")
        self._attr_icon = "mdi:laser-pointer"

    @property
    def native_value(self):
        source = self._source_state()
        return source.state if source else None

    @property
    def extra_state_attributes(self):
        source = self._source_state()
        if not source:
            return {"source_entity": self._source}
        keys = ("detail", "job_active", "serial_connected", "socket_connected", "attached", "workflow", "grbl_state")
        return {"source_entity": self._source, **{k: source.attributes[k] for k in keys if k in source.attributes}}
