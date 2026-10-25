"""One-shot CNCjs Socket.IO v2 controller client. No automatic job recovery."""
import asyncio
import socketio
from homeassistant.exceptions import HomeAssistantError

class CNCjsClient:
    def __init__(self,hass,entry):
        self.hass=hass
        self.url=entry.data["cncjs_url"].rstrip("/")
        self.username=entry.data.get("username","")
        self.password=entry.data.get("password","")
        self.auth_method=entry.data.get("auth_method", "password")
        self.token=entry.data.get("cncjs_token", "")

    async def _token(self):
        if self.auth_method == "token":
            if not self.token.strip():
                raise HomeAssistantError("Brak tokenu CNCjs")
            return self.token.strip()
        if not self.username:
            raise HomeAssistantError("Podaj login i hasło CNCjs w konfiguracji integracji")
        session = __import__('homeassistant.helpers.aiohttp_client',fromlist=['async_get_clientsession']).async_get_clientsession(self.hass)
        try:
            async with session.post(self.url+"/api/signin",json={"name":self.username,"password":self.password},timeout=12) as resp:
                if resp.status != 200: raise HomeAssistantError(f"Logowanie CNCjs: HTTP {resp.status}")
                result=await resp.json()
                token=result.get("token") or result.get("accessToken")
                if not token: raise HomeAssistantError("CNCjs nie zwrócił tokenu")
                return token
        except asyncio.TimeoutError as exc:
            raise HomeAssistantError("CNCjs nie odpowiada") from exc

    async def command(self,command,*args):
        token=await self._token()
        client=socketio.AsyncClient(reconnection=False,request_timeout=10)
        try:
            await asyncio.wait_for(client.connect(self.url + '?token=' + __import__('urllib.parse', fromlist=['quote']).quote(token, safe=''),transports=['polling'],socketio_path='socket.io',headers={'Authorization':'Bearer '+token}),timeout=15)
            # CNCjs command event: command(commandName, port, ...args)
            # Serial port is retrieved from the source bridge attributes when possible.
            await client.emit('command',(command,*args))
            await asyncio.sleep(0.4)
        except Exception as exc:
            raise HomeAssistantError(f"Błąd komendy CNCjs: {exc}") from exc
        finally:
            if client.connected: await client.disconnect()
