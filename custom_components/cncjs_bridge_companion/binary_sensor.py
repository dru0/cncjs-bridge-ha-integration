"""Connection indicators based on the existing bridge attributes."""
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from .entity import BridgeEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([
        BridgeConnectionSensor(entry, "cncjs", "Połączenie CNCjs", "socket_connected"),
        BridgeConnectionSensor(entry, "serial", "Połączenie USB lasera", "serial_connected"),
        BridgeConnectionSensor(entry, "job", "Zadanie aktywne", "job_active"),
    ])


class BridgeConnectionSensor(BridgeEntity, BinarySensorEntity):
    def __init__(self, entry, key, name, attribute):
        super().__init__(entry, key, name)
        self._attribute = attribute
        if key != "job":
            self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self):
        source = self._source_state()
        if source is None:
            return None
        value = source.attributes.get(self._attribute)
        return value if isinstance(value, bool) else None
