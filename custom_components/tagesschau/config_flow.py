import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from aiohttp import ClientError, ClientResponseError, ClientSession

from homeassistant.const import (
    CONF_REGION
)

from .const import (
    DOMAIN,
    REGIONS
)

class EmptyConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 2

    def __init__(self) -> None:
        """Initialize the config flow."""

    async def async_step_user(self, formdata):
        if formdata is not None:
            region_id = formdata[CONF_REGION]
            region_name = REGIONS[region_id]
            return self.async_create_entry(title=f"Tagesschau {region_name}",data=formdata)

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(
                {vol.Required(CONF_REGION): vol.In(REGIONS)}
            ),
        )
