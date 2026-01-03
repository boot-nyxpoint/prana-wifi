"""Climate platform for prana_wifi integration."""

from __future__ import annotations

import logging

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PranaWifiConfigEntry
from .const import DOMAIN, PRESET_NIGHT, PRESET_BOOST, PRESET_HEATING, PRESET_WINTER, PRESET_AUTO, PRESET_AUTO_PLUS
from .coordinator import PranaCoordinator

_LOGGER = logging.getLogger(__name__)

PRESET_MODES = [
    PRESET_BOOST,
    PRESET_AUTO,
    PRESET_AUTO_PLUS,
    PRESET_NIGHT,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PranaWifiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Prana WiFi climate entities from a config entry."""
    entities = [
        PranaClimate(coordinator, entry.entry_id)
        for coordinator in entry.runtime_data.coordinators.values()
    ]
    async_add_entities(entities)


class PranaClimate(CoordinatorEntity[PranaCoordinator], ClimateEntity):
    """Representation of a Prana WiFi climate device."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.FAN_ONLY]
    _attr_preset_modes = PRESET_MODES
    _attr_supported_features = (
        ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )
    _attr_fan_modes = ["0", "1", "2", "3", "4", "5"]
    _enable_turn_on_off_backwards_compat = False

    def __init__(
        self,
        coordinator: PranaCoordinator,
        entry_id: str,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        device = coordinator.device
        self._attr_unique_id = f"{entry_id}_{device.device_id}_climate"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.device_id)},
            "name": device.name,
            "manufacturer": "Prana",
            "model": device.device_type,
        }

    @property
    def _is_on(self) -> bool | None:
        """Determine if the climate is on."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("on")

    @property
    def _fan_mode(self) -> str | None:
        """Determine if the climate is on."""
        if self.coordinator.data is None or self.coordinator.data.get("fan") is None:
            return None
        return str(self.coordinator.data.get("fan").get("input_speed"))

    @property
    def preset_mode(self) -> str | None:
        """Determine if the climate is on."""
        if self.coordinator.data is None or self.coordinator.data.get("presets") is None:
            return None

        for key, value in self.coordinator.data.get("presets").items():
            if value:
                return key

        return None

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature from temp_in sensor."""
        if self.coordinator.data is None or self.coordinator.data.get('sensors') is None:
            return None
        return self.coordinator.data.get('sensors').get("temp_out")

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode."""
        return HVACMode.FAN_ONLY if self._is_on else HVACMode.OFF

    @property
    def fan_mode(self) -> str | None:
        """Return the current fan mode."""
        return self._fan_mode

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set the HVAC mode."""
        device_id = self.coordinator.device.device_id
        if hvac_mode == HVACMode.OFF:
            self.coordinator.turn_off()
            self.schedule_update_ha_state(force_refresh=False)
            await self.coordinator.client.turn_off(device_id)
        elif hvac_mode == HVACMode.FAN_ONLY:
            self.coordinator.turn_on()
            self.schedule_update_ha_state(force_refresh=False)
            await self.coordinator.client.turn_on(device_id)

    async def async_turn_on(self) -> None:
        """Turn on the climate device."""
        await self.async_set_hvac_mode(HVACMode.FAN_ONLY)

    async def async_turn_off(self) -> None:
        """Turn off the climate device."""
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set the fan mode."""
        speed = int(fan_mode)
        self.coordinator.turn_on()
        self.coordinator.set_speed(speed)
        self.schedule_update_ha_state(force_refresh=False)
        await self.coordinator.client.set_speed(self.coordinator.device.device_id, speed)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode."""
        device_id = self.coordinator.device.device_id
        if preset_mode != self.preset_mode:
            self.coordinator.turn_on()
            self.coordinator.set_preset(preset_mode)
            self.schedule_update_ha_state(force_refresh=False)
            await self.coordinator.client.set_preset(device_id, preset_mode)
