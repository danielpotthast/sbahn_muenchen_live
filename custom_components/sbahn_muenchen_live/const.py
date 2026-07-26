"""Constants for the S-Bahn München Live integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "sbahn_muenchen_live"

CONF_STATION = "station"
CONF_STATION_ID = "station_id"
CONF_STATION_NAME = "station_name"
CONF_DESTINATIONS = "destinations"
CONF_LINES = "lines"
CONF_TIMEOFFSET = "timeoffset"
CONF_NUMBER = "number"

DEFAULT_DESTINATIONS: list[str] = [""]
DEFAULT_LINES: list[str] = [""]
DEFAULT_TIMEOFFSET = 0
DEFAULT_NUMBER = 5

SCAN_INTERVAL = timedelta(seconds=30)
