"""Number platform for prana_wifi integration."""

from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PranaWifiConfigEntry
from .const import DOMAIN
from .coordinator import PranaCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PranaWifiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Prana WiFi number entities from a config entry."""
    entities = [
        PranaBrightness(coordinator, entry.entry_id)
        for coordinator in entry.runtime_data.coordinators.values()
    ] + [
        PranaFanInputSpeed(coordinator, entry.entry_id)
        for coordinator in entry.runtime_data.coordinators.values()
    ] + [
        PranaFanOutputSpeed(coordinator, entry.entry_id)
        for coordinator in entry.runtime_data.coordinators.values()
    ]
    async_add_entities(entities)


class PranaBrightness(CoordinatorEntity[PranaCoordinator], NumberEntity):
    """Representation of a Prana WiFi display brightness control."""

    _attr_has_entity_name = True
    _attr_translation_key = "brightness"
    _attr_native_min_value = 1
    _attr_native_max_value = 6
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: PranaCoordinator, entry_id: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        device = coordinator.device
        self._attr_unique_id = f"{entry_id}_{device.device_id}_brightness"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.device_id)},
            "name": device.name,
            "manufacturer": "Prana",
            "model": device.device_type,
        }

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("brightness")

    async def async_set_native_value(self, value: float) -> None:
        """Set the display brightness level."""
        brightness = int(value)
        self.coordinator.set_brightness(brightness)
        self.schedule_update_ha_state(force_refresh=False)
        await self.coordinator.client.set_brightness(
            self.coordinator.device.device_id, brightness
        )

class PranaFanInputSpeed(CoordinatorEntity[PranaCoordinator], NumberEntity):
    """Representation of a Prana WiFi display brightness control."""

    _attr_has_entity_name = True
    _attr_translation_key = "fan_input_speed"
    _attr_native_min_value = 0
    _attr_native_max_value = 5
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: PranaCoordinator, entry_id: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        device = coordinator.device
        self._attr_unique_id = f"{entry_id}_{device.device_id}_fan_input_speed"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.device_id)},
            "name": device.name,
            "manufacturer": "Prana",
            "model": device.device_type,
        }

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        if self.coordinator.data is None or self.coordinator.data.get("fan") is None:
            return None
        return self.coordinator.data.get("fan").get('input_speed')

    async def async_set_native_value(self, value: float) -> None:
        """Set the display brightness level."""
        speed = int(value)
        self.coordinator.set_in_speed(speed)
        self.schedule_update_ha_state(force_refresh=False)
        await self.coordinator.client.set_in_speed(
            self.coordinator.device.device_id, speed
        )

class PranaFanOutputSpeed(CoordinatorEntity[PranaCoordinator], NumberEntity):
    """Representation of a Prana WiFi display brightness control."""

    _attr_has_entity_name = True
    _attr_translation_key = "fan_output_speed"
    _attr_native_min_value = 0
    _attr_native_max_value = 5
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: PranaCoordinator, entry_id: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        device = coordinator.device
        self._attr_unique_id = f"{entry_id}_{device.device_id}_fan_output_speed"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.device_id)},
            "name": device.name,
            "manufacturer": "Prana",
            "model": device.device_type,
        }

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        if self.coordinator.data is None or self.coordinator.data.get("fan") is None:
            return None
        return self.coordinator.data.get("fan").get('output_speed')

    async def async_set_native_value(self, value: float) -> None:
        """Set the display brightness level."""
        speed = int(value)
        self.coordinator.set_out_speed(speed)
        self.schedule_update_ha_state(force_refresh=False)
        await self.coordinator.client.set_out_speed(
            self.coordinator.device.device_id, speed
        )
