"""CNCjs Bridge Companion: status and explicitly requested G-code actions."""
from pathlib import Path
import logging
import voluptuous as vol
from homeassistant.const import Platform
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, CONF_SOURCE_ENTITY, CONF_MEDIA_DIR, DEFAULT_MEDIA_DIR

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SELECT, Platform.BUTTON]
EXTS = {".nc", ".gcode", ".gc", ".tap"}


def _root(hass, entry):
    configured = entry.options.get(CONF_MEDIA_DIR, entry.data.get(CONF_MEDIA_DIR, DEFAULT_MEDIA_DIR))
    if not isinstance(configured, str) or not configured.strip() or "\x00" in configured:
        raise HomeAssistantError("Nieprawidłowy katalog G-code")
    media_dirs = getattr(hass.config, "media_dirs", {}) or {}
    local_media = Path(media_dirs.get("local", "/media")).resolve()
    config_dir = Path(hass.config.config_dir).resolve()
    roots = [local_media, (config_dir / "www" / "media").resolve()]
    requested = Path(configured)
    folder = (requested if requested.is_absolute() else local_media / requested).resolve()
    if not any(folder == base or base in folder.parents for base in roots):
        raise HomeAssistantError("Katalog poza dozwolonym obszarem: media lub config/www/media")
    return folder


def _entry(hass):
    entries = hass.config_entries.async_entries(DOMAIN)
    if len(entries) != 1:
        raise HomeAssistantError("Wymagana dokładnie jedna skonfigurowana integracja CNCjs Bridge Companion")
    return entries[0]


async def _handle(hass, call):
    entry = _entry(hass)
    action = call.data["action"]
    if action == "list":
        folder = _root(hass, entry)
        def get_files():
            if not folder.is_dir():
                raise HomeAssistantError(f"Katalog nie istnieje: {folder}")
            return sorted(f.name for f in folder.iterdir() if f.is_file() and f.suffix.lower() in EXTS)
        files = await hass.async_add_executor_job(get_files)
        hass.bus.async_fire("cncjs_bridge_companion_files", {"files": files, "entry_id": entry.entry_id})
        return {"files": files}

    state = hass.states.get(entry.data[CONF_SOURCE_ENTITY])
    attrs = state.attributes if state else {}
    if not state or attrs.get("socket_connected") is not True or attrs.get("serial_connected") is not True:
        raise HomeAssistantError("Bridge nie potwierdza połączenia CNCjs i USB")
    if action == "load":
        if state.state in ("running", "paused", "hold"):
            raise HomeAssistantError("Nie można ładować pliku podczas zadania")
        name = call.data.get("filename", "")
        if not name or Path(name).name != name or Path(name).suffix.lower() not in EXTS:
            raise HomeAssistantError("Podaj samą nazwę pliku G-code, bez ścieżki")
        folder = _root(hass, entry)
        file = (folder / name).resolve()
        if file.parent != folder:
            raise HomeAssistantError("Plik poza katalogiem G-code")
        def read_file():
            if not file.is_file() or file.stat().st_size > 5 * 1024 * 1024:
                raise HomeAssistantError("Plik nie istnieje lub przekracza 5 MB")
            return file.read_text(encoding="utf-8-sig")
        code = await hass.async_add_executor_job(read_file)
        from .bridge_client import BridgeClient
        await BridgeClient(hass, entry).command("load", filename=name, gcode=code)
        return {"result": "sent", "filename": name}

    if action == "start" and call.data.get("confirm") is not True:
        raise HomeAssistantError("Start wymaga confirm: true")
    if action == "start" and state.state in ("running", "paused", "hold"):
        raise HomeAssistantError("Zadanie już działa")
    if action == "pause" and state.state != "running":
        raise HomeAssistantError("Pauza wymaga statusu running")
    if action == "resume" and state.state not in ("paused", "hold"):
        raise HomeAssistantError("Wznów wymaga statusu paused/hold")
    if action in ("start", "resume"):
        raise HomeAssistantError("Zdalny Start/Wznów zablokowany do czasu testów bezpieczeństwa")
    from .bridge_client import BridgeClient
    await BridgeClient(hass, entry).command(action)
    return {"result": "sent", "action": action}


async def async_setup(hass, config):
    """Register actions even before a config entry is loaded."""
    if not hass.services.has_service(DOMAIN, "control"):
        async def handler(call):
            return await _handle(hass, call)
        hass.services.async_register(
            DOMAIN, "control", handler,
            schema=vol.Schema({
                vol.Required("action"): vol.In(["list", "load", "start", "pause", "resume", "stop"]),
                vol.Optional("filename"): cv.string,
                vol.Optional("confirm", default=False): cv.boolean,
            }), supports_response=SupportsResponse.OPTIONAL,
        )
        _LOGGER.info("Registered cncjs_bridge_companion.control")
    return True


async def async_setup_entry(hass, entry):
    from .manager import GCodeManager
    manager = GCodeManager(hass, entry, _root)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = manager
    await manager.async_refresh()
    # Ensure service exists on HA versions that initialize config entries directly.
    await async_setup(hass, {})
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry):
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unloaded
