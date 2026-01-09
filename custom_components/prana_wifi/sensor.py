"""Sensor platform for prana_wifi integration."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_BILLION,
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PranaWifiConfigEntry
from .const import DOMAIN
from .coordinator import PranaCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class PranaSensorEntityDescription(SensorEntityDescription):
    """Describes a Prana sensor entity."""

    value_key: str


SENSOR_DESCRIPTIONS: tuple[PranaSensorEntityDescription, ...] = (
    PranaSensorEntityDescription(
        key="tvoc",
        translation_key="tvoc",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_BILLION,
        device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="tvoc",
    ),
    PranaSensorEntityDescription(
        key="co2eq",
        translation_key="co2eq",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="co2eq",
    ),
    PranaSensorEntityDescription(
        key="humidity",
        translation_key="humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="humidity",
    ),
    PranaSensorEntityDescription(
        key="atm",
        translation_key="atm",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="atm",
    ),
    PranaSensorEntityDescription(
        key="inside_t_in",
        translation_key="inside_t_in",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="inside_t_in",
    ),
    PranaSensorEntityDescription(
        key="inside_t_out",
        translation_key="inside_t_out",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="inside_t_out",
    ),
    PranaSensorEntityDescription(
        key="outside_t",
        translation_key="outside_t",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="outside_t",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PranaWifiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Prana WiFi sensor entities from a config entry."""
    entities: list[PranaSensor] = []
    for coordinator in entry.runtime_data.coordinators.values():
        for description in SENSOR_DESCRIPTIONS:
            entities.append(PranaSensor(coordinator, entry.entry_id, description))

    async_add_entities(entities)


class PranaSensor(CoordinatorEntity[PranaCoordinator], SensorEntity):
    """Representation of a Prana WiFi sensor."""

    entity_description: PranaSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PranaCoordinator,
        entry_id: str,
        description: PranaSensorEntityDescription,
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator)
        self.entity_description = description
        device = coordinator.device
        self._attr_unique_id = f"{entry_id}_{device.device_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.device_id)},
            "name": device.name,
            "manufacturer": "Prana",
            "model": device.device_type,
        }

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        if self.coordinator.data is None or self.coordinator.data.get('sensors') is None:
            return None
        return self.coordinator.data.get('sensors').get(self.entity_description.value_key)
