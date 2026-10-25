"""G-code file selection and conservative command dispatch for CNCjs."""
from pathlib import Path
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import DOMAIN, CONF_SOURCE_ENTITY

EXTS = {".nc", ".gcode", ".gc", ".tap"}

class GCodeManager:
    def __init__(self, hass, entry, root_resolver):
        self.hass, self.entry, self.root_resolver = hass, entry, root_resolver
        self.files = []
        self.selected = None
        self.last_loaded = None
        self.signal = f"{DOMAIN}_update_{entry.entry_id}"

    def notify(self):
        async_dispatcher_send(self.hass, self.signal)

    async def async_refresh(self):
        folder = self.root_resolver(self.hass, self.entry)
        def scan():
            if not folder.is_dir():
                return []
            return sorted(f.name for f in folder.iterdir() if f.is_file() and not f.is_symlink() and f.suffix.lower() in EXTS)
        self.files = await self.hass.async_add_executor_job(scan)
        if self.selected not in self.files:
            self.selected = self.files[0] if self.files else None
        self.notify()

    def source(self):
        return self.hass.states.get(self.entry.data[CONF_SOURCE_ENTITY])

    def port(self):
        state = self.source()
        if state is None or state.attributes.get("socket_connected") is not True or state.attributes.get("serial_connected") is not True:
            raise HomeAssistantError("Brak potwierdzonego połączenia CNCjs i USB")
        port = state.attributes.get("port") or state.attributes.get("serial_port") or self.entry.options.get("serial_port", "")
        if not port:
            raise HomeAssistantError("Nie znam portu USB. Ustaw serial_port w opcjach integracji, np. /dev/ttyUSB0")
        return port

    async def async_load(self):
        await self.async_refresh()
        name = self.selected
        if not name or name not in self.files:
            raise HomeAssistantError("Najpierw wybierz plik G-code")
        state = self.source()
        if state and (state.state in ("running", "paused", "hold") or state.attributes.get("job_active") is True):
            raise HomeAssistantError("Nie można ładować podczas pracy lasera")
        folder = self.root_resolver(self.hass, self.entry)
        file = (folder / name).resolve()
        if file.parent != folder:
            raise HomeAssistantError("Niedozwolona ścieżka pliku")
        def read():
            if not file.is_file() or file.is_symlink() or file.stat().st_size > 5*1024*1024:
                raise HomeAssistantError("Plik nie istnieje lub przekracza 5 MB")
            return file.read_text(encoding="utf-8-sig")
        code = await self.hass.async_add_executor_job(read)
        from .client import CNCjsClient
        await CNCjsClient(self.hass, self.entry).command("gcode:load", self.port(), name, code, {})
        self.last_loaded = name  # sent, not a controller acknowledgment
        self.notify()

    async def async_command(self, action):
        state = self.source()
        if not state:
            raise HomeAssistantError("Brak statusu bridge")
        if action == "start":
            raise HomeAssistantError("Start z przycisku zablokowany do czasu potwierdzenia protokołu CNCjs. Użyj CNCjs bezpośrednio.")
        if action == "resume":
            raise HomeAssistantError("Wznawianie z przycisku zablokowane do czasu potwierdzenia protokołu CNCjs")
        if action == "pause" and state.state != "running":
            raise HomeAssistantError("Pauza wymaga stanu running")
        if action not in ("pause", "stop"):
            raise HomeAssistantError("Nieznane polecenie")
        from .client import CNCjsClient
        port = self.port()
        args = ("gcode:stop", port, {"force": True}) if action == "stop" else ("gcode:pause", port)
        await CNCjsClient(self.hass, self.entry).command(*args)
