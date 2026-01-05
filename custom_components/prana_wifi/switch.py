"""Number platform for prana_wifi integration."""

from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PranaWifiConfigEntry
from .const import DOMAIN, PRESET_NIGHT, PRESET_BOOST, PRESET_HEATING, PRESET_WINTER, PRESET_AUTO, PRESET_AUTO_PLUS
from .coordinator import PranaCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PranaWifiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Prana WiFi number entities from a config entry."""
    entities = [
        PranaPowerSwitch(coordinator, entry.entry_id)
        for coordinator in entry.runtime_data.coordinators.values()
    ] + [
        PranaHeatingSwitch(coordinator, entry.entry_id)
        for coordinator in entry.runtime_data.coordinators.values()
    ] + [
        PranaWinterSwitch(coordinator, entry.entry_id)
        for coordinator in entry.runtime_data.coordinators.values()
    ] + [
        PranaNightSwitch(coordinator, entry.entry_id)
        for coordinator in entry.runtime_data.coordinators.values()
    ] + [
        PranaBoostSwitch(coordinator, entry.entry_id)
        for coordinator in entry.runtime_data.coordinators.values()
    ] + [
        PranaAutoSwitch(coordinator, entry.entry_id)
        for coordinator in entry.runtime_data.coordinators.values()
    ] + [
        PranaAutoPlusSwitch(coordinator, entry.entry_id)
        for coordinator in entry.runtime_data.coordinators.values()
    ]
    async_add_entities(entities)


class PranaPowerSwitch(CoordinatorEntity[PranaCoordinator], SwitchEntity):
    """Representation of a Prana WiFi heating mode control."""

    _attr_has_entity_name = True
    _attr_translation_key = "power_on"
    _attr_is_on = False

    def __init__(self, coordinator: PranaCoordinator, entry_id: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        device = coordinator.device
        self._attr_unique_id = f"{entry_id}_{device.device_id}_power_on"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.device_id)},
            "name": device.name,
            "manufacturer": "Prana",
            "model": device.device_type,
        }

    @property
    def is_on(self) -> bool | None:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        return bool(self.coordinator.data.get("on"))

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        self.coordinator.turn_on()
        self.schedule_update_ha_state(force_refresh=False)
        await self.coordinator.client.turn_on(self.coordinator.device.device_id)

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        self.coordinator.turn_off()
        self.schedule_update_ha_state(force_refresh=False)
        await self.coordinator.client.turn_off(self.coordinator.device.device_id)

class PranaHeatingSwitch(CoordinatorEntity[PranaCoordinator], SwitchEntity):
    """Representation of a Prana WiFi heating mode control."""

    _attr_has_entity_name = True
    _attr_translation_key = "heating_on"
    _attr_is_on = False

    def __init__(self, coordinator: PranaCoordinator, entry_id: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        device = coordinator.device
        self._attr_unique_id = f"{entry_id}_{device.device_id}_heating_on"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.device_id)},
            "name": device.name,
            "manufacturer": "Prana",
            "model": device.device_type,
        }

    @property
    def is_on(self) -> bool | None:
        """Return the sensor value."""
        if self.coordinator.data is None or self.coordinator.data.get("presets") is None:
            return None
        return bool(self.coordinator.data.get("presets").get("heating"))

    async def async_toggle(self, **kwargs):
        """Toggle the entity."""
        self.coordinator.set_preset(PRESET_HEATING)
        self.schedule_update_ha_state(force_refresh=False)
        await self.coordinator.client.set_preset(self.coordinator.device.device_id, PRESET_HEATING)

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self.async_toggle(**kwargs)

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.async_toggle(**kwargs)

class PranaWinterSwitch(CoordinatorEntity[PranaCoordinator], SwitchEntity):
    """Representation of a Prana WiFi winter mode control."""

    _attr_has_entity_name = True
    _attr_translation_key = "winter_on"
    _attr_is_on = False

    def __init__(self, coordinator: PranaCoordinator, entry_id: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        device = coordinator.device
        self._attr_unique_id = f"{entry_id}_{device.device_id}_winter_on"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.device_id)},
            "name": device.name,
            "manufacturer": "Prana",
            "model": device.device_type,
        }

    @property
    def is_on(self) -> bool | None:
        """Return the sensor value."""
        if self.coordinator.data is None or self.coordinator.data.get("presets") is None:
            return None
        return bool(self.coordinator.data.get("presets").get("winter"))

    async def async_toggle(self, **kwargs):
        """Toggle the entity."""
        self.coordinator.set_preset(PRESET_WINTER)
        self.schedule_update_ha_state(force_refresh=False)
        await self.coordinator.client.set_preset(self.coordinator.device.device_id, PRESET_WINTER)

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self.async_toggle(**kwargs)

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.async_toggle(**kwargs)

class PranaNightSwitch(CoordinatorEntity[PranaCoordinator], SwitchEntity):
    """Representation of a Prana WiFi night mode control."""

    _attr_has_entity_name = True
    _attr_translation_key = "night_on"
    _attr_is_on = False

    def __init__(self, coordinator: PranaCoordinator, entry_id: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        device = coordinator.device
        self._attr_unique_id = f"{entry_id}_{device.device_id}_night_on"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.device_id)},
            "name": device.name,
            "manufacturer": "Prana",
            "model": device.device_type,
        }

    @property
    def is_on(self) -> bool | None:
        """Return the sensor value."""
        if self.coordinator.data is None or self.coordinator.data.get("presets") is None:
            return None
        return bool(self.coordinator.data.get("presets").get("night"))

    async def async_toggle(self, **kwargs):
        """Toggle the entity."""
        self.coordinator.set_preset(PRESET_NIGHT)
        self.schedule_update_ha_state(force_refresh=False)
        await self.coordinator.client.set_preset(self.coordinator.device.device_id, PRESET_NIGHT)

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self.async_toggle(**kwargs)

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.async_toggle(**kwargs)

class PranaBoostSwitch(CoordinatorEntity[PranaCoordinator], SwitchEntity):
    """Representation of a Prana WiFi boost mode control."""

    _attr_has_entity_name = True
    _attr_translation_key = "boost_on"
    _attr_is_on = False

    def __init__(self, coordinator: PranaCoordinator, entry_id: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        device = coordinator.device
        self._attr_unique_id = f"{entry_id}_{device.device_id}_boost_on"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.device_id)},
            "name": device.name,
            "manufacturer": "Prana",
            "model": device.device_type,
        }

    @property
    def is_on(self) -> bool | None:
        """Return the sensor value."""
        if self.coordinator.data is None or self.coordinator.data.get("presets") is None:
            return None
        return bool(self.coordinator.data.get("presets").get("boost"))

    async def async_toggle(self, **kwargs):
        """Toggle the entity."""
        self.coordinator.set_preset(PRESET_BOOST)
        self.schedule_update_ha_state(force_refresh=False)
        await self.coordinator.client.set_preset(self.coordinator.device.device_id, PRESET_BOOST)

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self.async_toggle(**kwargs)

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.async_toggle(**kwargs)

class PranaAutoSwitch(CoordinatorEntity[PranaCoordinator], SwitchEntity):
    """Representation of a Prana WiFi auto mode control."""

    _attr_has_entity_name = True
    _attr_translation_key = "auto_on"
    _attr_is_on = False

    def __init__(self, coordinator: PranaCoordinator, entry_id: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        device = coordinator.device
        self._attr_unique_id = f"{entry_id}_{device.device_id}_auto_on"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.device_id)},
            "name": device.name,
            "manufacturer": "Prana",
            "model": device.device_type,
        }

    @property
    def is_on(self) -> bool | None:
        """Return the sensor value."""
        if self.coordinator.data is None or self.coordinator.data.get("presets") is None:
            return None
        return bool(self.coordinator.data.get("presets").get("auto"))

    async def async_toggle(self, **kwargs):
        """Toggle the entity."""
        self.coordinator.set_preset(PRESET_AUTO)
        self.schedule_update_ha_state(force_refresh=False)
        await self.coordinator.client.set_preset(self.coordinator.device.device_id, PRESET_AUTO)

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self.async_toggle(**kwargs)

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.async_toggle(**kwargs)

class PranaAutoPlusSwitch(CoordinatorEntity[PranaCoordinator], SwitchEntity):
    """Representation of a Prana WiFi auto plus mode control."""

    _attr_has_entity_name = True
    _attr_translation_key = "auto_plus_on"
    _attr_is_on = False

    def __init__(self, coordinator: PranaCoordinator, entry_id: str) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        device = coordinator.device
        self._attr_unique_id = f"{entry_id}_{device.device_id}_auto_plus_on"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.device_id)},
            "name": device.name,
            "manufacturer": "Prana",
            "model": device.device_type,
        }

    @property
    def is_on(self) -> bool | None:
        """Return the sensor value."""
        if self.coordinator.data is None or self.coordinator.data.get("presets") is None:
            return None
        return bool(self.coordinator.data.get("presets").get("auto_plus"))

    async def async_toggle(self, **kwargs):
        """Toggle the entity."""
        self.coordinator.set_preset(PRESET_AUTO_PLUS)
        self.schedule_update_ha_state(force_refresh=False)
        await self.coordinator.client.set_preset(self.coordinator.device.device_id, PRESET_AUTO_PLUS)

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self.async_toggle(**kwargs)

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.async_toggle(**kwargs)