"""The prana_wifi integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PranaWifiAuthError, PranaWifiClient, PranaWifiConnectionError
from .coordinator import PranaCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.NUMBER, Platform.CLIMATE, Platform.SWITCH]


@dataclass
class PranaWifiData:
    """Runtime data for prana_wifi integration."""

    client: PranaWifiClient
    coordinators: dict[str, PranaCoordinator]


type PranaWifiConfigEntry = ConfigEntry[PranaWifiData]


async def async_setup_entry(hass: HomeAssistant, entry: PranaWifiConfigEntry) -> bool:
    """Set up prana_wifi from a config entry."""
    session = async_get_clientsession(hass)
    client = PranaWifiClient(
        session,
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )

    try:
        await client.authenticate()
        devices = await client.get_devices()
    except PranaWifiAuthError as err:
        raise ConfigEntryAuthFailed("Invalid authentication") from err
    except PranaWifiConnectionError as err:
        raise ConfigEntryNotReady("Unable to connect to API") from err

    coordinators: dict[str, PranaCoordinator] = {}
    for device in devices:
        coordinator = PranaCoordinator(hass, client, device)
        await coordinator.async_config_entry_first_refresh()
        coordinators[device.device_id] = coordinator

    entry.runtime_data = PranaWifiData(client=client, coordinators=coordinators)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: PranaWifiConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
