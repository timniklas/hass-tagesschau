from homeassistant.config_entries import ConfigFlow
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from aiohttp import ClientError, ClientResponseError, ClientSession
from .const import DOMAIN

class EmptyConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""

    async def async_step_user(self, formdata):
        return self.async_create_entry(title="Tagesschau",data={})
