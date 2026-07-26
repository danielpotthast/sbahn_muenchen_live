"""Config flow for the SBM integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode

from .const import (
    CONF_DESTINATIONS,
    CONF_LINES,
    CONF_NUMBER,
    CONF_STATION,
    CONF_STATION_ID,
    CONF_STATION_NAME,
    CONF_TIMEOFFSET,
    DEFAULT_DESTINATIONS,
    DEFAULT_LINES,
    DEFAULT_NUMBER,
    DEFAULT_TIMEOFFSET,
    DOMAIN,
)
from .stations import STATIONS, station_by_name, station_options


def _csv_to_list(value: str) -> list[str]:
    """Convert a comma-separated string to a list, matching the legacy YAML behavior."""
    items = [item.strip() for item in value.split(",")]
    return items if items else [""]


def _list_to_csv(value: list[str] | None) -> str:
    """Convert a list back to a comma-separated string for form pre-fill."""
    return ", ".join(value) if value else ""


class SbmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SBM."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        """Handle the initial step: pick a station from the known station list."""
        errors: dict[str, str] = {}
        if user_input is not None:
            station_id = int(user_input[CONF_STATION_ID])
            station_name = STATIONS[station_id]["name"]

            await self.async_set_unique_id(str(station_id))
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input.get(CONF_NAME) or station_name,
                data={
                    CONF_STATION_ID: station_id,
                    CONF_STATION_NAME: station_name,
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_STATION_ID): SelectSelector(
                    SelectSelectorConfig(options=station_options(), mode=SelectSelectorMode.DROPDOWN)
                ),
                vol.Optional(CONF_NAME): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, import_data: dict[str, Any]) -> config_entries.ConfigFlowResult:
        """Import a single `nextdeparture` entry from YAML configuration."""
        station = station_by_name(import_data[CONF_STATION])
        if station is None:
            return self.async_abort(reason="invalid_station")

        await self.async_set_unique_id(str(station["id"]))
        self._abort_if_unique_id_configured()

        options = {
            CONF_DESTINATIONS: import_data.get(CONF_DESTINATIONS, DEFAULT_DESTINATIONS),
            CONF_LINES: import_data.get(CONF_LINES, DEFAULT_LINES),
            CONF_TIMEOFFSET: import_data.get(CONF_TIMEOFFSET, DEFAULT_TIMEOFFSET),
            CONF_NUMBER: import_data.get(CONF_NUMBER, DEFAULT_NUMBER),
        }
        return self.async_create_entry(
            title=import_data.get(CONF_NAME) or station["name"],
            data={
                CONF_STATION_ID: station["id"],
                CONF_STATION_NAME: station["name"],
            },
            options=options,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SbmOptionsFlowHandler:
        """Create the options flow."""
        return SbmOptionsFlowHandler()


class SbmOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle SBM options: destinations, lines, timeoffset and number."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            options = {
                CONF_DESTINATIONS: _csv_to_list(user_input[CONF_DESTINATIONS]),
                CONF_LINES: _csv_to_list(user_input[CONF_LINES]),
                CONF_TIMEOFFSET: user_input[CONF_TIMEOFFSET],
                CONF_NUMBER: user_input[CONF_NUMBER],
            }
            return self.async_create_entry(data=options)

        current = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_DESTINATIONS,
                    default=_list_to_csv(current.get(CONF_DESTINATIONS, DEFAULT_DESTINATIONS)),
                ): str,
                vol.Optional(
                    CONF_LINES,
                    default=_list_to_csv(current.get(CONF_LINES, DEFAULT_LINES)),
                ): str,
                vol.Optional(
                    CONF_TIMEOFFSET,
                    default=current.get(CONF_TIMEOFFSET, DEFAULT_TIMEOFFSET),
                ): int,
                vol.Optional(
                    CONF_NUMBER,
                    default=current.get(CONF_NUMBER, DEFAULT_NUMBER),
                ): int,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
