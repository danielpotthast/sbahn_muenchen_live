"""DataUpdateCoordinator for the SBM integration."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL
from .sbmapi import SbmApi

_LOGGER = logging.getLogger(__name__)


@dataclass
class SbmData:
    """Raw departures and messages for a station."""

    departures: list[dict[str, Any]]
    messages: list[dict[str, Any]]


class SbmDataUpdateCoordinator(DataUpdateCoordinator[SbmData]):
    """Coordinator that polls departures and messages for one station."""

    def __init__(self, hass: HomeAssistant, api: SbmApi, timeoffset: int, number: int) -> None:
        """Initialize the coordinator."""
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self._api = api
        self._timeoffset = timeoffset
        # Overfetch: destinations/lines filtering in the sensor happens after this,
        # so a raw limit equal to `number` could leave fewer than `number` results.
        self._limit = min(number * 3, 50)

    async def _async_update_data(self) -> SbmData:
        """Fetch departures and messages from the SBM API.

        Departures and messages are treated independently: a failure fetching one
        doesn't blank out the other. If a previous successful poll exists, its data
        is kept as a fallback; only a departures failure on the very first refresh
        (no fallback data available) fails the whole update.
        """
        previous = self.data

        departures_result, messages_result = await asyncio.gather(
            self._api.departures_async(
                station_id=self._api.station_id,
                offset=self._timeoffset,
                limit=self._limit,
            ),
            self._api.messages_async(),
            return_exceptions=True,
        )

        if isinstance(departures_result, BaseException):
            _LOGGER.warning("Could not update SBM departures: %s", departures_result)
            if previous is None:
                raise UpdateFailed(f"Error fetching departures: {departures_result}") from departures_result
            departures = previous.departures
        else:
            departures = departures_result

        if isinstance(messages_result, BaseException):
            _LOGGER.warning("Could not update SBM messages: %s", messages_result)
            messages = previous.messages if previous is not None else []
        else:
            messages = messages_result

        return SbmData(departures=departures, messages=messages)
