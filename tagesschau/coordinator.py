from dataclasses import dataclass
from datetime import timedelta
import logging

import re

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_LOCATION,
    CONF_NAME,
    CONF_SELECTOR
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from aiohttp import ClientError
from xml.dom import minidom

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class TagesschauAPIData:
    """Class to hold api data."""

    newsitems: [any]


class TagesschauCoordinator(DataUpdateCoordinator):
    """My coordinator."""

    data: ButenunbinnenAPIData

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        # Initialise DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            # Method to call on every update interval.
            update_method=self.async_update_data,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=60),
        )
        self.connected: bool = False
        self.websession = async_get_clientsession(hass)

    async def async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            async with self.websession.get('https://www.butenunbinnen.de/feed/rss/neuste-inhalte100.xml') as response:
                response.raise_for_status()
                response_text = await response.text()
    
                dom = minidom.parseString(response_text)
                elements = dom.getElementsByTagName('entry')
    
                items = []
                for element in elements:
                    items.append({
                        "title": element.getElementsByTagName('title')[0].firstChild.data,
                        "summary": element.getElementsByTagName('summary')[0].firstChild.data,
                        "updated": element.getElementsByTagName('updated')[0].firstChild.data,
                        "link": element.getElementsByTagName('link')[0].attributes['href'].value
                    })

                self.connected = True
                return ButenunbinnenAPIData(newsitems=items)
        except ClientError as err:
            # This will show entities as unavailable by raising UpdateFailed exception
            raise UpdateFailed(f"Error communicating with API: {err}") from err
