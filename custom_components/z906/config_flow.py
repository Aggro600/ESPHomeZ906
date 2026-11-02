"""Config flow: pick the ESPHome device of the Z906 bridge."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.selector import (
    DeviceSelector,
    DeviceSelectorConfig,
    EntitySelector,
    EntitySelectorConfig,
)

from .const import CONF_DEVICE_ID, CONF_POWER_OFF, CONF_POWER_ON, DOMAIN, REQUIRED_ROLES
from .discovery import find_entities

POWER_DOMAINS = ["button", "input_button", "script", "switch"]


def _power_schema(values: dict[str, Any]) -> dict:
    """Optional entities that switch the amplifier (for example an IR sender)."""
    selector = EntitySelector(EntitySelectorConfig(domain=POWER_DOMAINS))
    return {
        vol.Optional(key, description={"suggested_value": values.get(key)}): selector
        for key in (CONF_POWER_ON, CONF_POWER_OFF)
    }


class Z906ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the setup dialog."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Choose the device."""
        errors: dict[str, str] = {}
        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID]
            await self.async_set_unique_id(device_id)
            self._abort_if_unique_id_configured()
            found = find_entities(self.hass, device_id)
            if all(role in found for role in REQUIRED_ROLES):
                device = dr.async_get(self.hass).async_get(device_id)
                title = (device.name_by_user or device.name) if device else "Z906"
                options = {k: v for k, v in user_input.items() if k != CONF_DEVICE_ID}
                return self.async_create_entry(
                    title=title or "Z906", data={CONF_DEVICE_ID: device_id}, options=options
                )
            errors[CONF_DEVICE_ID] = "not_z906"
        schema = {
            vol.Required(CONF_DEVICE_ID): DeviceSelector(DeviceSelectorConfig(integration="esphome")),
            **_power_schema(user_input or {}),
        }
        return self.async_show_form(step_id="user", data_schema=vol.Schema(schema), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> Z906OptionsFlow:
        """Return the options flow."""
        return Z906OptionsFlow()


class Z906OptionsFlow(OptionsFlow):
    """Change the power entities."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Show the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(step_id="init", data_schema=vol.Schema(_power_schema(dict(self.config_entry.options))))
