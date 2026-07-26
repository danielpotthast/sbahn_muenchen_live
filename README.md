# S-Bahn München Live Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Home Assistant integration for S-Bahn München public transport departures, covering all 152 known S-Bahn stations.

## Features

- Real-time departure information
- Config flow with a searchable station dropdown — no more guessing station IDs
- Filter by destination and line
- Delay information
- Platform information
- Multiple stations, each as its own config entry
- Shared polling per station via a `DataUpdateCoordinator`

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL
6. Category: Integration
7. Click "Install"
8. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/sbahn_muenchen_live` directory to your Home Assistant `config/custom_components` directory
2. Restart Home Assistant

### Verify

- Go to **Developer Tools → States**
- Look for the new `sensor.*` entity for the station you added
- The state should show minutes until next departure

## Configuration

Go to **Settings → Devices & Services → Add Integration** and search for
"S-Bahn München Live". Pick a station from the dropdown and, optionally, a
custom name for the sensor.

After setup, use the integration's **Configure** button to adjust:

| Option | Default | Description |
|--------|---------|--------------|
| `destinations` | All | Comma-separated list of destinations to filter |
| `lines` | All | Comma-separated list of lines to filter (e.g. `S1, S8`) |
| `timeoffset` | 0 | Minimum minutes until departure |
| `number` | 5 | Maximum number of departures to show |

> **Note:** `destinations` and `lines` must match the *exact* text the live
> feed reports, not the shortened station names used for the dropdown above.
> The airport, for example, appears as a destination named
> `"Flughafen/Airport ✈"`, not `"Flughafen Terminal"`. Set up the sensor
> without filters first, check its `departures` attribute in **Developer
> Tools → States** to see the real strings, then fill in the filter.

### Legacy YAML configuration

Existing `configuration.yaml` entries under `sensor: - platform: sbahn_muenchen_live` are
automatically imported as config entries on startup (with a repair
notification asking you to remove the YAML block afterwards). New YAML
configuration is not needed — use the UI going forward.

```yaml
sensor:
  - platform: sbahn_muenchen_live
    nextdeparture:
      - station: "Flughafen Besucherpark"
        name: "Airport Departures"
```

## Sensor Attributes

The sensor provides the following state and attributes:

**State:** Minutes until next departure

**Attributes:**

- `destination`: Destination of the next departure
- `line`: Line name (e.g., "S1", "S8")
- `type`: Transport type (e.g., "S-Bahn")
- `platform`: Platform number
- `delay`: Delay in minutes
- `icon`: Material Design Icon
- `departures`: List of all upcoming departures
- `messages`: Service messages (currently empty — the geOps timetable endpoint doesn't provide any)

## Example Lovelace Card

```yaml
type: entities
title: Munich Airport S-Bahn
entities:
  - entity: sensor.airport_departures
    secondary_info: last-updated
```

### Advanced Lovelace Card with Departures List

```yaml
type: custom:auto-entities
card:
  type: entities
  title: Airport Departures
filter:
  template: |
    {% for departure in state_attr('sensor.airport_departures', 'departures') %}
      {{
        {
          'entity': 'sensor.airport_departures',
          'name': departure.line + ' → ' + departure.destination,
          'secondary_info': departure.time_in_mins | string + ' min' + (' +' + departure.delay | string + ' min' if departure.delay > 0 else '')
        }
      }},
    {% endfor %}
```

## Troubleshooting

### No Departures Showing

1. Check that the selected station has current S-Bahn traffic
2. Verify your internet connection
3. Check Home Assistant logs for errors: `Settings > System > Logs`
4. Try increasing the `number` option to fetch more departures

### Integration Not Loading

1. Ensure all dependencies are installed (websockets, certifi)
2. Check Python version (requires Python 3.11+)
3. Restart Home Assistant after installation
4. Check for errors in the logs

### Sensor State is "Unknown"

1. Check if the API is reachable: `wss://api.geops.io/realtime-ws/v1/`
2. Verify there are departures at the current time for that station

## Data Source

This integration uses data from the **S-Bahn München Live Map** provided by geOps.

### Why this integration?

The timetable data from the geOps Live Map API is **more accurate and reliable** than other public transport APIs because:

- **Real-time updates**: Direct connection to the live tracking system
- **Precise timing**: Actual timetable data with delay information
- **High reliability**: Used by the official S-Bahn München live map
- **WebSocket connection**: Instant updates without polling delays

The integration specifically uses only the **timetable endpoint** (`GET timetable_{station_id}`) for optimal performance and accuracy, rather than map/trajectory data. The station list (`custom_components/sbahn_muenchen_live/stations.py`) was generated once from the `GET station_schematic` endpoint, since geOps has no by-name station search API.

## License

MIT License

## Credits

- Data: geOps.io
- Integration structure inspired by the MVG integration

## Support

For issues, feature requests, or questions, please open an issue on GitHub.
