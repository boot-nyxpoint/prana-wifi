"""API client for Prana WiFi devices."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from math import log2
import struct

from aiohttp import ClientError, ClientResponseError, ClientSession, ContentTypeError

from .const import API_BASE_URL, PRESET_NIGHT, PRESET_BOOST, PRESET_HEATING, PRESET_WINTER, PRESET_AUTO, PRESET_AUTO_PLUS


@dataclass
class PranaDevice:
    """Representation of a Prana device."""

    device_id: str
    name: str
    prana_name: str
    device_type: str
    additional_info: dict[str, Any]


class PranaWifiAuthError(Exception):
    """Exception for authentication errors."""


class PranaWifiConnectionError(Exception):
    """Exception for connection errors."""


class PranaWifiUnsupportedSpeedError(Exception):
    """Exception for unsupported speed errors."""


class PranaWifiUnsupportedPresetError(Exception):
    """Exception for unsupported speed errors."""


class PranaWifiUnsupportedBrightnessError(Exception):
    """Exception for unsupported speed errors."""


class PranaWifiClient:
    """API client for Prana WiFi devices."""

    def __init__(self, session: ClientSession, username: str, password: str, refresh_token: str = None) -> None:
        """Initialize the API client."""
        self._session = session
        self._username = username
        self._password = password
        self._refresh_token: str | None = refresh_token
        self._token: str | None = None

    async def authenticate(self) -> bool:
        """Authenticate with the API and obtain an access token and a refresh token."""
        url = f"{API_BASE_URL}/auth/login"
        payload = {
            "username": self._username,
            "password": self._password,
        }

        try:
            async with self._session.post(url, json=payload) as response:
                if response.status == 401:
                    raise PranaWifiAuthError("Invalid username or password")
                response.raise_for_status()
                data = await response.json()
        except ClientResponseError as err:
            if err.status == 401:
                raise PranaWifiAuthError("Invalid username or password") from err
            raise PranaWifiConnectionError(
                f"Error communicating with API: {err}"
            ) from err
        except ClientError as err:
            raise PranaWifiConnectionError(
                f"Error communicating with API: {err}"
            ) from err

        self._token = data.get("token")
        self._refresh_token = data.get("refreshToken")
        if not self._token:
            raise PranaWifiAuthError("No token received from API")

        return True

    async def refresh_token(self) -> bool:
        """Obtain an access token using the refresh token."""
        url = f"{API_BASE_URL}/auth/token"
        payload = {
            "refreshToken": self._refresh_token,
        }
        data = None

        try:
            async with self._session.post(url, json=payload) as response:
                if response.status != 401:
                    response.raise_for_status()
                    data = await response.json()
        except ClientResponseError as err:
            pass
        except ClientError as err:
            pass

        if data:
            self._token = data.get("token")
            self._refresh_token = data.get("refreshToken")
            return True

        return False

    async def _api_get(self, url, params):
        if not self._token and self._refresh_token:
            if not await self.refresh_token():
                await self.authenticate()
        elif not self._token and not self._refresh_token:
            await self.authenticate()

        full_url = f"{API_BASE_URL}/{url}"
        headers = {
            "Authorization": f"Bearer {self._token}",
        }

        try:
            async with self._session.get(
                full_url, params=params, headers=headers
            ) as response:
                if response.status == 401:
                    # Token might be expired, try to obtain one
                    # using the refresh token first, else reauthenticate
                    if not await self.refresh_token():
                        await self.authenticate()

                    headers["Authorization"] = f"Bearer {self._token}"

                    async with self._session.get(
                        full_url, params=params, headers=headers
                    ) as retry_response:
                        retry_response.raise_for_status()
                        data = await retry_response.json()
                else:
                    response.raise_for_status()
                    data = await response.json()
        except ClientResponseError as err:
            if err.status == 401:
                raise PranaWifiAuthError("Authentication failed") from err
            raise PranaWifiConnectionError(
                f"Error communicating with API: {err}"
            ) from err
        except ClientError as err:
            raise PranaWifiConnectionError(
                f"Error communicating with API: {err}"
            ) from err

        return data

    async def _api_post(self, url, body):
        if not self._token and self._refresh_token:
            if not await self.refresh_token():
                await self.authenticate()
        elif not self._token and not self._refresh_token:
            await self.authenticate()

        data = None
        full_url = f"{API_BASE_URL}/{url}"
        headers = {
            "Authorization": f"Bearer {self._token}",
        }

        try:
            async with self._session.post(
                full_url, json=body, headers=headers
            ) as response:
                if response.status == 401:
                    # Token might be expired, try to obtain one
                    # using the refresh token first, else reauthenticate
                    if not await self.refresh_token():
                        await self.authenticate()

                    headers["Authorization"] = f"Bearer {self._token}"

                    async with self._session.post(
                        full_url, json=body, headers=headers
                    ) as retry_response:
                        retry_response.raise_for_status()
                        try:
                            data = await retry_response.json()
                        except ContentTypeError:
                            pass
                else:
                    response.raise_for_status()
                    try:
                        data = await response.json()
                    except ContentTypeError:
                        pass
        except ClientResponseError as err:
            if err.status == 401:
                raise PranaWifiAuthError("Authentication failed") from err
            raise PranaWifiConnectionError(
                f"Error communicating with API: {err}"
            ) from err
        except ClientError as err:
            raise PranaWifiConnectionError(
                f"Error communicating with API: {err}"
            ) from err

        return data

    async def get_devices(self) -> list[PranaDevice]:
        params = {
            "pageSize": "0",
            "page": "10",
            "type": "",
        }
        return self._parse_devices(await self._api_get('user/devices', params))

    def _parse_devices(self, data: dict[str, Any]) -> list[PranaDevice]:
        """Parse device data from API response."""
        devices: list[PranaDevice] = []

        for device_data in data.get("data"):
            if not isinstance(device_data, dict):
                continue

            device_id = device_data.get("id").get("id")
            if not device_id:
                continue

            label = device_data.get("label")
            if not label:
                continue

            device_type = device_data.get("type", "unknown")
            if device_data.get("additionalInfo") and device_data.get("additionalInfo").get("pranaType"):
                device_type = device_data.get("additionalInfo").get("pranaType").replace("Prana", "").strip()

            devices.append(
                PranaDevice(
                    device_id=device_id,
                    name=label.strip(),
                    device_type=device_type,
                    prana_name=device_data.get("name", "unknown"),
                    additional_info=device_data.get("additionalInfo", {}),
                )
            )

        return devices

    async def button_clicked(self, device_id: str, button_number: int, args: dict[str, Any] | None = None):
        url = f"rpc/twoway/{device_id}"
        params = {
            "buttonNumber": button_number,
            **(args or {}),
        }
        return await self._api_post(url, {
            "method": "buttonClicked",
            "params": params
        })

    async def toggle_on_off(self, device_id: str) -> None:
        """Turn on a device."""
        return await self.button_clicked(device_id, 1)

    async def turn_on(self, device_id: str, speed: int = 1) -> None:
        """Turn on a device."""
        return await self.set_speed(device_id, speed)

    async def turn_off(self, device_id: str) -> None:
        """Turn off a device."""
        return await self.set_speed(device_id, 0)

    async def set_out_speed(self, device_id: str, speed: int) -> None:
        """Set out speed for a device."""
        if speed == 0:
            return await self.button_clicked(device_id, 16)
        if 1 <= speed <= 5:
            return await self.button_clicked(device_id, 40 + speed)
        raise PranaWifiUnsupportedSpeedError("speed must be between 0 and 5")

    async def set_in_speed(self, device_id: str, speed: int) -> None:
        """Set in speed for a device."""
        if speed == 0:
            return await self.button_clicked(device_id, 13)
        if 1 <= speed <= 5:
            return await self.button_clicked(device_id, 30 + speed)
        raise PranaWifiUnsupportedSpeedError("speed must be between 0 and 5")

    async def set_speed(self, device_id: str, speed: int) -> None:
        """Set the in and out speed of a device."""
        if speed == 0:
            return await self.button_clicked(device_id, 10)
        if 1 <= speed <= 5:
            return await self.button_clicked(device_id, 50 + speed)
        raise PranaWifiUnsupportedSpeedError("speed must be between 0 and 5")

    async def set_preset(self, device_id: str, preset: str) -> None:
        """Set a preset mode on/off for a device."""
        if preset == PRESET_NIGHT:
            return await self.button_clicked(device_id, 6)
        if preset == PRESET_BOOST:
            return await self.button_clicked(device_id, 7)
        if preset == PRESET_HEATING:
            # this toggles heating on/off
            return await self.button_clicked(device_id, 5)
        if preset == PRESET_WINTER:
            # this toggles winter on/off
            return await self.button_clicked(device_id, 22)
        if preset == PRESET_AUTO:
            return await self.button_clicked(device_id, 67)
        if preset == PRESET_AUTO_PLUS:
            return await self.button_clicked(device_id, 68)

        raise PranaWifiUnsupportedPresetError("preset {preset} is not supported".format(preset=preset))

    async def set_brightness(self, device_id: str, brightness: int) -> dict[str, Any] | None:
        """Set the display brightness level for a device."""
        if 1 <= brightness <= 6:
            return await self.button_clicked(device_id, 110 + brightness)
        raise PranaWifiUnsupportedBrightnessError("brightness must be between 1 and 6")

    async def toggle_lock_in_out_speeds(self, device_id: str) -> dict[str, Any] | None:
        """Lock in/out speeds for a device."""
        return await self.button_clicked(device_id, 9)

    async def get_raw_state(self, device_id: str, keys: list[str]) -> dict[str, Any] | None:
        """Get the current raw state of a device."""
        params = {
            "keys": ",".join(keys),
        }
        data = await self._api_get(f"plugins/telemetry/DEVICE/{device_id}/values/attributes", params)

        if data:
            ret = {}
            for item in data:
                ret[item["key"]] = {
                    "value": item["value"],
                    "last_updated": item["lastUpdateTs"],
                }
            return ret
        return None

    async def get_state(self, device_id: str) -> dict[str, Any]:
        """Get the current state of a device."""
        return self._parse_state(await self.get_raw_state(device_id, ["state"]))

    def _parse_state(self, data: dict[str, Any] | None) -> dict[str, Any]:
        """Parse the state into a dict."""
        if data:
            raw_state = data['state']['value']
            last_updated = data['state']['last_updated']
            state = bytes.fromhex(raw_state)
            return {
                "presets": self._parse_state_presets(state),
                "sensors": self._parse_state_sensors(state),
                "fan": self._parse_state_fan(state),
                "brightness": int(log2(state[3]) + 1),
                "on": int(state[1]),
                "last_updated": last_updated,
            }
        return {}

    def _parse_state_presets(self, state: bytes) -> dict[str, Any]:
        """Parse the state presets into a dict."""
        return {
            PRESET_BOOST: int(state[9]),
            PRESET_HEATING: int(state[5]),
            PRESET_WINTER: int(state[33]),
            PRESET_AUTO: 1 if int(state[11]) == 1 else 0,
            PRESET_AUTO_PLUS: 1 if int(state[11]) == 2 else 0,
            PRESET_NIGHT: int(state[7]),
        }

    def _parse_state_sensors(self, state: bytes) -> dict[str, Any] | None:
        """Parse the state sensors into a dict."""
        humidity = int(state[51] - 128)
        if humidity > 0:
            co2eq = int(struct.unpack_from(">h", state, 52)[0] & 0b0011111111111111)
            if 0 < co2eq < 10000:
                inside_t_in = float(struct.unpack_from(">h", state, 45)[0] & 0b0011111111111111) / 10.0
                inside_t_out = float(struct.unpack_from(">h", state, 39)[0] & 0b0011111111111111) / 10.0
                outside_t = float(struct.unpack_from(">h", state, 42)[0] & 0b0011111111111111) / 10.0
            else:
                inside_t_in = float(state[46]) / 10
                inside_t_out = float(state[40]) / 10
                outside_t = None
            return {
                "tvoc": int(struct.unpack_from(">h", state, 54)[0] & 0b0011111111111111),
                "co2eq": co2eq,
                "humidity": humidity,
                "atm": 512 + int(state[69]),
                "inside_t_in": inside_t_in,
                "inside_t_out": inside_t_out,
                "outside_t": outside_t,
            }
        return None

    def _parse_state_fan(self, state: bytes) -> dict[str, Any]:
        """Parse the state of the fan into a dict."""
        input_on = int(state[19])
        output_on = int(state[23])
        input_speed = int(state[21] / 10) if input_on else 0
        output_speed = int(state[25] / 10) if output_on else 0
        return {
            "input_on": input_on,
            "input_speed": 5 if input_speed > 5 else input_speed,
            "output_on": output_on,
            "output_speed": 5 if output_speed > 5 else output_speed,
            "locked": int(state[13]),
        }

