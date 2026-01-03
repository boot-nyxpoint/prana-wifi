"""Coordinator for prana_wifi integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PranaDevice, PranaWifiClient, PranaWifiConnectionError
from .const import PRESET_NIGHT, PRESET_BOOST, PRESET_AUTO, PRESET_AUTO_PLUS

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=15)


class PranaCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for polling Prana device state."""

    def __init__(
        self, hass: HomeAssistant, client: PranaWifiClient, device: PranaDevice
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=device.name,
            update_interval=SCAN_INTERVAL,
        )
        self.client = client
        self.device = device

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch state from the API."""
        try:
            return await self.client.get_state(self.device.device_id)
        except PranaWifiConnectionError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    def set_brightness(self, brightness: int) -> None:
        if self.data:
            self.data.update({"brightness": brightness})

    def turn_on(self) -> None:
        if self.data:
            self.data.update({"on": 1})

    def turn_off(self) -> None:
        if self.data:
            self.data.update({"on": 0})

    def set_speed(self, speed: int) -> None:
        if self.data:
            self.data.get('fan').update({
                "input_on": 1,
                "input_speed": speed,
                "output_on": 1,
                "output_speed": speed
            })

    def set_preset(self, preset_mode: str) -> None:
        if self.data:
            self.data.get('presets').update({
                PRESET_NIGHT: 0,
                PRESET_BOOST: 0,
                PRESET_AUTO: 0,
                PRESET_AUTO_PLUS: 0,
                preset_mode: 1
            })

    def set_in_speed(self, speed: int) -> None:
        if self.data:
            self.data.get('fan').update({
                "input_on": 1,
                "input_speed": speed,
            })

    def set_out_speed(self, speed: int) -> None:
        if self.data:
            self.data.get('fan').update({
                "output_on": 1,
                "output_speed": speed,
            })


