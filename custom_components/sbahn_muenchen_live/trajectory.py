"""Shared background tracker for live train formation (unit count) data.

geOps only exposes how many S-Bahn units are coupled together on a train
("Zuglänge") through the trajectory/BBOX realtime feed, not through the
`GET timetable_<station_id>` endpoint used for departures. This module keeps
one persistent BBOX subscription open — shared across every config entry
regardless of how many stations are configured, since it already covers the
whole network — and caches the unit count by `train_id` for the coordinators
to look up.

Formation data comes from the `original_rake` property on trajectory
features, e.g. `"948004231676;948004231684"` for a double-traction (2-unit)
train; a single id means a single-unit train. It's only populated for
vehicles currently broadcasting live position data.
"""

from __future__ import annotations

import asyncio
import json
import logging
import ssl
import time
from typing import Any

import certifi
import websockets

_LOGGER = logging.getLogger(__name__)

# Covers the whole S-Bahn München network. The bounds are derived from the
# actual extent of the `station_schematic` feed (measured: x 156857..4795038,
# y 174534..3263878), padded a bit on each side. An earlier version of this
# bbox (copied from a dev script) only covered ~15% of the network's stations
# and missed most branches (including the airport line), which meant most
# trains never showed up here at all and `train_units` stayed null far more
# often than it should have.
_BBOX_COMMAND = "BBOX 100000 100000 4850000 3350000 5 tenant=sbm channel_prefix=schematic"

_RECV_TIMEOUT = 90.0  # reconnect if the feed goes silent for this long
_CACHE_TTL = 3600.0  # drop cached entries older than this
_RECONNECT_BASE_DELAY = 5.0
_RECONNECT_MAX_DELAY = 60.0


class TrainFormationTracker:
    """Background BBOX listener that maps train_id -> number of coupled units."""

    def __init__(self, api_key: str) -> None:
        """Initialize the tracker (does not connect until `start()` is called)."""
        self._uri = f"wss://api.geops.io/realtime-ws/v1/?key={api_key}"
        self._ssl_context = ssl.create_default_context(cafile=certifi.where())
        self._cache: dict[str, tuple[int, float]] = {}
        self._task: asyncio.Task[None] | None = None
        self._stop = False

    def start(self) -> None:
        """Start the background listener task, if not already running."""
        if self._task is None:
            self._stop = False
            self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        """Stop the background listener task."""
        self._stop = True
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    def units(self, train_id: str | None) -> int | None:
        """Return the cached number of coupled units for a train_id, if known."""
        if not train_id:
            return None
        entry = self._cache.get(train_id)
        if entry is None:
            return None
        unit_count, cached_at = entry
        if time.monotonic() - cached_at > _CACHE_TTL:
            self._cache.pop(train_id, None)
            return None
        return unit_count

    async def _run(self) -> None:
        delay = _RECONNECT_BASE_DELAY
        while not self._stop:
            try:
                async with websockets.connect(
                    self._uri, ssl=self._ssl_context, close_timeout=10, max_queue=None
                ) as websocket:
                    await websocket.send(_BBOX_COMMAND)
                    delay = _RECONNECT_BASE_DELAY
                    while not self._stop:
                        response = await asyncio.wait_for(websocket.recv(), timeout=_RECV_TIMEOUT)
                        self._handle_message(response)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # keep the tracker alive across any transient failure
                _LOGGER.debug("Train formation tracker connection error, retrying: %s", exc)
                await asyncio.sleep(delay)
                delay = min(delay * 2, _RECONNECT_MAX_DELAY)

    def _handle_message(self, raw: str) -> None:
        try:
            data: dict[str, Any] = json.loads(raw)
        except json.JSONDecodeError:
            return

        if data.get("source") != "trajectory":
            return

        content = data.get("content")
        if not isinstance(content, dict) or content.get("type") != "Feature":
            return

        props = content.get("properties", {})
        train_id = props.get("train_id")
        rake = props.get("original_rake")
        if not train_id or not rake:
            return

        unit_count = len([unit for unit in rake.split(";") if unit and unit != "0"])
        if unit_count:
            self._cache[train_id] = (unit_count, time.monotonic())
