"""HTTP client for the existing Raspberry Pi bridge. No direct CNCjs connection."""
import asyncio
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

class BridgeClient:
    def __init__(self, hass, entry):
        self.session = async_get_clientsession(hass)
        self.url = entry.options.get('bridge_api_url', 'http://ray5cam:8765').rstrip('/')
        self.token = entry.options.get('bridge_api_token', '')

    async def command(self, action, filename=None, gcode=None):
        if not self.token or len(self.token) < 24:
            raise HomeAssistantError('Ustaw token Bridge API w opcjach integracji')
        if action not in ('load', 'pause', 'stop'):
            raise HomeAssistantError('Polecenie niedostępne w trybie bridge')
        payload = {'action': action}
        if action == 'load':
            payload.update(filename=filename, gcode=gcode)
        try:
            async with self.session.post(self.url + '/v1/command', json=payload,
                headers={'Authorization':'Bearer ' + self.token}, timeout=20) as resp:
                result = await resp.json()
                if resp.status != 202:
                    raise HomeAssistantError('Bridge HTTP %s: %s' % (resp.status, result.get('error', 'error')))
                return result
        except (asyncio.TimeoutError, OSError) as exc:
            raise HomeAssistantError('Brak połączenia z Bridge API: %s' % exc) from exc
