# Prana WiFi for Home Assistant

A custom Home Assistant integration for Prana WiFi ventilation/recuperator units. Control your Prana devices directly from Home Assistant with full support for fan speeds, presets, sensors, and more.

If you use this, open an issue and submit feedback. This is the only way to improve it.

## Features

Nearly all controls from the mobile app. Only the scheduler is missing, but it doesn't make sense to add it, you can just create automations in homeassistant.

- **Climate Control**: Turn your Prana unit on/off, set fan speeds (0-5), and activate presets
- **Environmental Sensors**: Monitor temperature (in/out), humidity, CO2 equivalent, TVOC, and atmospheric pressure
- **Preset Modes**: Night, Boost, Heating, Winter, Auto, and Auto+ modes
- **Individual Fan Control**: Set input and output fan speeds independently
- **Display Brightness**: Adjust the device display brightness (1-6)
- **Real-time Updates**: Device state is polled every 15 seconds

## Installation

### HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance
2. Open HACS in the Home Assistant sidebar
3. Search for "Prana WiFi" in HACS
4. Click **Download**
5. Restart Home Assistant

### Manual Installation

1. Download the `custom_components/prana_wifi` folder from this repository
2. Copy the `prana_wifi` folder to your Home Assistant `custom_components` directory
   ```
   <config>/custom_components/prana_wifi/
   ```
3. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services** in Home Assistant
2. Click **+ Add Integration**
3. Search for "Prana WiFi"
4. Enter your Prana cloud account credentials (the same you use in the Prana mobile app)
5. Click **Submit**

The integration will automatically discover all Prana devices associated with your account.

## How It Works

### Architecture

This integration communicates with Prana devices through the Prana cloud API. It uses a polling mechanism to fetch device state every 15 seconds and sends commands through the cloud when you interact with entities.

```
Home Assistant <---> Prana Cloud API <---> Prana WiFi Device
```

### Authentication

The integration authenticates with the Prana cloud using your account credentials. Tokens are automatically refreshed as needed to maintain the connection.

### Data Flow

1. **Polling**: The integration polls each device's state every 15 seconds
2. **State Parsing**: Raw device data is parsed into meaningful sensor values and entity states
3. **Commands**: When you change a setting (speed, preset, etc.), the command is sent to the cloud API
4. **Optimistic Updates**: The UI updates immediately while the command is being processed

### API Communication

- **Base URL**: `https://iot.sensesaytech.com/api`
- **Protocol**: HTTPS with token-based authentication
- **Polling Interval**: 15 seconds

## Entities

For each Prana device, the following entities are created:

### Climate Entity

| Entity | Description |
|--------|-------------|
| `climate.{device_name}` | Main climate entity for fan control |

**Features:**
- HVAC modes: Off, Fan Only
- Fan speeds: 0, 1, 2, 3, 4, 5
- Preset modes: Boost, Auto, Auto+, Night

### Sensors

| Entity | Description | Unit |
|--------|-------------|------|
| `sensor.{device_name}_tvoc` | Volatile Organic Compounds | ppb |
| `sensor.{device_name}_co2_equivalent` | CO2 equivalent | ppm |
| `sensor.{device_name}_humidity` | Humidity | % |
| `sensor.{device_name}_atmospheric_pressure` | Atmospheric pressure | hPa |
| `sensor.{device_name}_temperature_in` | Incoming air temperature | °C |
| `sensor.{device_name}_temperature_out` | Outgoing air temperature | °C |

### Number Controls

| Entity | Description | Range |
|--------|-------------|-------|
| `number.{device_name}_display_brightness` | Display brightness | 1-6 |
| `number.{device_name}_fan_input_speed` | Input fan speed | 0-5 |
| `number.{device_name}_fan_output_speed` | Output fan speed | 0-5 |

### Switches

| Entity | Description |
|--------|-------------|
| `switch.{device_name}_power` | Power on/off |
| `switch.{device_name}_heating_mode` | Toggle heating mode |
| `switch.{device_name}_winter_mode` | Toggle winter mode |
| `switch.{device_name}_night_mode` | Toggle night mode |
| `switch.{device_name}_boost_mode` | Toggle boost mode |
| `switch.{device_name}_auto_mode` | Toggle auto mode |
| `switch.{device_name}_auto_plus_mode` | Toggle auto+ mode |

## Contributing

Contributions are welcome! Here's how you can help:

### Reporting Issues

1. Check if the issue already exists in the [GitHub Issues](https://github.com/boot-nyxpoint/prana-wifi/issues)
2. If not, create a new issue with:
   - A clear description of the problem
   - Steps to reproduce
   - Home Assistant version
   - Integration version
   - Relevant log entries (enable debug logging if needed)

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/prana-wifi.git
   cd prana-wifi
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements.test.txt
   ```

### Running Tests

```bash
pytest tests/
```

### Code Style

This project uses:
- **Ruff** for linting
- **MyPy** for type checking

Run linting:
```bash
ruff check .
```

Run type checking:
```bash
mypy custom_components/prana_wifi
```

### Pull Requests

1. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Ensure tests pass and code style is correct
4. Commit with a descriptive message
5. Push to your fork
6. Open a Pull Request against the `main` branch

### Debug Logging

To enable debug logging for troubleshooting, add to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.prana_wifi: debug
```

## Requirements

- Home Assistant 2025.12.1 or newer
- A Prana WiFi ventilation unit
- A Prana cloud account (same credentials as the mobile app)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This integration is not officially affiliated with or endorsed by Prana. Use at your own risk. The integration relies on the Prana cloud API, which may change without notice.

## Credits

- **Code Owner**: [@boot-nyxpoint](https://github.com/boot-nyxpoint)
