"""The S-Bahn München Live integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_NUMBER, CONF_STATION_ID, CONF_TIMEOFFSET, DEFAULT_NUMBER, DEFAULT_TIMEOFFSET, DOMAIN
from .coordinator import SbmDataUpdateCoordinator
from .sbmapi import SbmApi
from .trajectory import TrainFormationTracker

PLATFORMS = [Platform.SENSOR]

_TRACKER_KEY = "trajectory_tracker"
_TRACKER_REFCOUNT_KEY = "trajectory_tracker_refcount"


def _acquire_tracker(hass: HomeAssistant, api_key: str) -> TrainFormationTracker:
    """Get the shared train-formation tracker, starting it on first use.

    One BBOX subscription already covers the whole S-Bahn network, so it's
    shared across every config entry instead of opened once per station.
    """
    domain_data = hass.data.setdefault(DOMAIN, {})
    tracker: TrainFormationTracker | None = domain_data.get(_TRACKER_KEY)
    if tracker is None:
        tracker = TrainFormationTracker(api_key)
        domain_data[_TRACKER_KEY] = tracker
        domain_data[_TRACKER_REFCOUNT_KEY] = 0
    tracker.start()
    domain_data[_TRACKER_REFCOUNT_KEY] += 1
    return tracker


async def _release_tracker(hass: HomeAssistant) -> None:
    """Release one reference to the shared tracker, stopping it once unused."""
    domain_data = hass.data.get(DOMAIN, {})
    domain_data[_TRACKER_REFCOUNT_KEY] = domain_data.get(_TRACKER_REFCOUNT_KEY, 1) - 1
    if domain_data[_TRACKER_REFCOUNT_KEY] <= 0:
        tracker: TrainFormationTracker | None = domain_data.pop(_TRACKER_KEY, None)
        domain_data.pop(_TRACKER_REFCOUNT_KEY, None)
        if tracker is not None:
            await tracker.stop()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry[SbmDataUpdateCoordinator]) -> bool:
    """Set up SBM from a config entry."""
    api = SbmApi(entry.data[CONF_STATION_ID])
    tracker = _acquire_tracker(hass, api.api_key)
    coordinator = SbmDataUpdateCoordinator(
        hass,
        api,
        tracker,
        entry.options.get(CONF_TIMEOFFSET, DEFAULT_TIMEOFFSET),
        entry.options.get(CONF_NUMBER, DEFAULT_NUMBER),
    )
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await _release_tracker(hass)
        raise

    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry[SbmDataUpdateCoordinator]) -> None:
    """Reload the config entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry[SbmDataUpdateCoordinator]) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await _release_tracker(hass)
    return unload_ok
