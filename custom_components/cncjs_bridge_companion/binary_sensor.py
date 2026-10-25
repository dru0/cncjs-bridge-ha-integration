from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from .entity import BridgeEntity
async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([BridgeConnectionSensor(entry,"cncjs","Połączenie CNCjs","socket_connected"), BridgeConnectionSensor(entry,"serial","Połączenie USB lasera","serial_connected"), BridgeConnectionSensor(entry,"job","Zadanie aktywne","job_active")])
class BridgeConnectionSensor(BridgeEntity,BinarySensorEntity):
    def __init__(self,entry,key,name,attribute):
        super().__init__(entry,key,name)
        self._attribute=attribute
        self._attr_icon={"cncjs":"mdi:lan-connect","serial":"mdi:usb-port","job":"mdi:laser-pointer"}[key]
        if key != "job": self._attr_device_class=BinarySensorDeviceClass.CONNECTIVITY
    @property
    def is_on(self):
        s=self._source_state()
        if s is None: return None
        value=s.attributes.get(self._attribute)
        return value if isinstance(value,bool) else None
