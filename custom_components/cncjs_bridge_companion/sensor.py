from homeassistant.components.sensor import SensorEntity
from .entity import BridgeEntity
async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([BridgeStatusSensor(entry)])
class BridgeStatusSensor(BridgeEntity, SensorEntity):
    def __init__(self, entry):
        super().__init__(entry, "status", "Status")
        self._attr_icon = "mdi:printer-3d-nozzle"
    @property
    def native_value(self):
        s = self._source_state()
        return s.state if s else None
    @property
    def extra_state_attributes(self):
        s = self._source_state()
        keys = ("detail", "job_active", "serial_connected", "socket_connected", "attached", "workflow", "grbl_state", "filename", "progress")
        return {"source_entity": self._source, **({k:s.attributes[k] for k in keys if k in s.attributes} if s else {})}
