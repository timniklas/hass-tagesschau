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

from homeassistant.const import (
    CONF_REGION
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class TagesschauAPIData:
    """Class to hold api data."""

    newsitems: [any]


class TagesschauCoordinator(DataUpdateCoordinator):
    """My coordinator."""

    data: TagesschauAPIData

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        # Set variables from values entered in config flow setup
        self.region_id = config_entry.data[CONF_REGION]

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
            async with self.websession.get(f'https://www.tagesschau.de/api2u/news/?regions={self.region_id}') as response:
                response.raise_for_status()
                response_json = await response.json()
    
                items = []
                for element in response_json['news']:
                    if 'firstSentence' in element:
                        items.append({
                            "title": element['title'],
                            "summary": element['firstSentence'],
                            "updated": element['date'],
                            "link": element['shareURL']
                        })

                self.connected = True
                return TagesschauAPIData(newsitems=items)
        except ClientError as err:
            # This will show entities as unavailable by raising UpdateFailed exception
            raise UpdateFailed(f"Error communicating with API: {err}") from err
