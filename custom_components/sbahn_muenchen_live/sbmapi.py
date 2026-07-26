"""API for S-Bahn München Live timetable data."""
from __future__ import annotations

import asyncio
import json
import logging
import ssl
from datetime import datetime
from typing import Any

import certifi
import websockets

from .stations import station_by_name

_LOGGER = logging.getLogger(__name__)


class SbmApi:
    """API for retrieving SBM timetable data via WebSocket."""

    def __init__(self, station_id: int, api_key: str | None = None):
        """Initialize the API.

        Args:
            station_id: Station ID (e.g., 8004167 for München Flughafen Besucherpark)
            api_key: Optional API key (default uses public key)
        """
        self.station_id = station_id
        self.api_key = api_key or "5cc87b12d7c5370001c1d655112ec5c21e0f441792cfc2fafe3e7a1e"
        self.uri = f"wss://api.geops.io/realtime-ws/v1/?key={self.api_key}"
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

    @staticmethod
    async def station_async(station_name: str) -> dict[str, Any] | None:
        """Find station ID by name.

        Args:
            station_name: Name of the station to look up

        Returns:
            Dictionary with 'id' and 'name' keys, or None if not found
        """
        station = station_by_name(station_name)
        if station is None:
            _LOGGER.warning("Station '%s' not found", station_name)
        return station

    async def departures_async(
        self,
        station_id: int | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Get departure times for the station.

        Args:
            station_id: Station ID (uses instance station_id if not provided)
            limit: Maximum number of departures to return
            offset: Time offset in minutes

        Returns:
            List of departure dictionaries
        """
        if station_id is None:
            station_id = self.station_id

        _LOGGER.debug("Fetching departures for station %s (limit: %d)", station_id, limit)

        departures = []
        consecutive_timeouts = 0
        max_consecutive_timeouts = 2

        try:
            async with websockets.connect(
                self.uri, ssl=self.ssl_context, close_timeout=10
            ) as websocket:
                # Request timetable
                command = f"GET timetable_{station_id}"
                await websocket.send(command)
                _LOGGER.debug("Sent command: %s", command)

                # Collect departures with improved timeout handling
                while consecutive_timeouts < max_consecutive_timeouts:
                    try:
                        # Increased timeout to 5 seconds for slower responses
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        consecutive_timeouts = 0  # Reset counter on successful receive

                        data = json.loads(response)

                        # Check if it's a timetable response
                        if f"timetable_{station_id}" in data.get("source", ""):
                            content = data["content"]

                            if isinstance(content, dict):
                                departure = self._parse_departure(content, offset)
                                if departure:
                                    departures.append(departure)
                                    _LOGGER.debug(
                                        "Collected departure %d/%d: %s to %s at %s",
                                        len(departures),
                                        limit,
                                        departure["line"],
                                        departure["destination"],
                                        datetime.fromtimestamp(departure["time"]).strftime("%H:%M"),
                                    )
                                else:
                                    _LOGGER.debug("Departure filtered by time offset")

                            # Continue collecting even after reaching limit
                            # to ensure we get the best departures after filtering
                            if len(departures) >= limit * 3:
                                _LOGGER.debug("Collected enough departures (%d), stopping", len(departures))
                                break

                    except asyncio.TimeoutError:
                        consecutive_timeouts += 1
                        _LOGGER.debug(
                            "Timeout %d/%d while waiting for departures (collected: %d)",
                            consecutive_timeouts,
                            max_consecutive_timeouts,
                            len(departures),
                        )
                        # Continue loop to allow for more timeouts before giving up

                _LOGGER.debug("Finished collecting: %d departures total", len(departures))

        except Exception as e:
            _LOGGER.error("Error fetching departures: %s", e)
            return []

        # Sort by time
        departures.sort(key=lambda x: x.get("time", 0))

        result = departures[:limit]
        _LOGGER.debug("Returning %d departures after sorting and limiting", len(result))

        return result

    def _parse_departure(
        self, content: dict[str, Any], time_offset: int
    ) -> dict[str, Any] | None:
        """Parse a single departure from API response.

        Args:
            content: API response content
            time_offset: Time offset in minutes

        Returns:
            Parsed departure dictionary or None if should be filtered
        """
        # Extract departure time
        dep_time_ms = content.get("departureTime") or content.get("time")
        if not dep_time_ms:
            return None

        departure_datetime = datetime.fromtimestamp(dep_time_ms / 1000)

        # Calculate minutes until departure
        current_time = datetime.now()
        time_difference = (departure_datetime - current_time).total_seconds()
        minutes_difference = int(time_difference / 60.0)

        # Filter by time offset
        if minutes_difference < time_offset:
            return None

        # Extract line information
        line_info = content.get("line", {})
        line_name = line_info.get("name", "?")

        # Extract destination (can be a list)
        destination_raw = content.get("to", "?")
        if isinstance(destination_raw, list):
            destination = ", ".join(destination_raw) if destination_raw else "?"
        else:
            destination = destination_raw

        # Extract delay
        delay_ms = content.get("departureDelay", 0)
        delay_min = round(delay_ms / 60000) if delay_ms else 0

        # Platform
        platform = content.get("platform")

        # State
        state = content.get("state", "")

        # Determine icon based on transport type
        icon = self._get_icon(line_name)

        return {
            "time": int(dep_time_ms / 1000),  # Unix timestamp in seconds
            "line": line_name,
            "destination": destination,
            "delay": delay_min,
            "platform": str(platform) if platform else None,
            "state": state,
            "icon": icon,
            "cancelled": False,  # SBM API doesn't provide cancellation info in timetable
            "type": self._get_transport_type(line_name),
            "train_id": content.get("train_id"),
        }

    def _get_icon(self, line: str) -> str:
        """Get icon for transport line.

        Args:
            line: Line name (e.g., "S1", "S8")

        Returns:
            Material Design Icon string
        """
        if line.startswith("S"):
            return "mdi:train"
        if line.startswith("U"):
            return "mdi:subway"
        if line.startswith("Tram"):
            return "mdi:tram"
        if line.startswith("Bus"):
            return "mdi:bus"
        return "mdi:train"

    def _get_transport_type(self, line: str) -> str:
        """Get transport type from line name.

        Args:
            line: Line name

        Returns:
            Transport type string
        """
        if line.startswith("S"):
            return "S-Bahn"
        if line.startswith("U"):
            return "U-Bahn"
        if line.startswith("Tram"):
            return "Tram"
        if line.startswith("Bus"):
            return "Bus"
        return "Train"

    async def messages_async(self) -> list[dict[str, Any]]:
        """Get service messages (not implemented for SBM).

        Returns:
            Empty list (SBM API doesn't provide messages in timetable endpoint)
        """
        return []
