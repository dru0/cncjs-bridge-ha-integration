"""Configuration flow for the existing CNCjs bridge companion."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from .const import CONF_SOURCE_ENTITY, DEFAULT_SOURCE_ENTITY, DOMAIN


class CNCjsBridgeCompanionFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            source = user_input[CONF_SOURCE_ENTITY]
            await self.async_set_unique_id(source)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=f"CNCjs Bridge ({source})", data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SOURCE_ENTITY, default=DEFAULT_SOURCE_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                )
            }),
        )
