"""Config flow: select token or CNCjs account credentials."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from .const import *

class CNCjsBridgeCompanionFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 4

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._base = user_input
            return await self.async_step_auth()
        return self.async_show_form(step_id="user", data_schema=vol.Schema({
            vol.Required(CONF_SOURCE_ENTITY, default=DEFAULT_SOURCE_ENTITY): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Required(CONF_URL, default="http://ray5cam:8000"): str,
            vol.Required(CONF_MEDIA_DIR, default=DEFAULT_MEDIA_DIR): str,
            vol.Required(CONF_AUTH_METHOD, default=AUTH_TOKEN): vol.In({AUTH_TOKEN: "Token CNCjs", AUTH_PASSWORD: "Login i hasło"}),
        }))

    async def async_step_auth(self, user_input=None):
        method = self._base[CONF_AUTH_METHOD]
        if user_input is not None:
            data = {**self._base, **user_input}
            await self.async_set_unique_id(data[CONF_SOURCE_ENTITY])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="CNCjs Bridge Companion", data=data)
        if method == AUTH_TOKEN:
            schema = vol.Schema({vol.Required(CONF_TOKEN): str})
        else:
            schema = vol.Schema({vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str})
        return self.async_show_form(step_id="auth", data_schema=schema)

    @staticmethod
    def async_get_options_flow(config_entry):
        return CNCjsBridgeOptionsFlow()


class CNCjsBridgeOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        current = self.config_entry.options.get(
            CONF_MEDIA_DIR,
            self.config_entry.data.get(CONF_MEDIA_DIR, DEFAULT_MEDIA_DIR),
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_MEDIA_DIR, default=current): str,
                vol.Optional("serial_port", default=self.config_entry.options.get("serial_port", "")): str,
            }),
        )
