"""Logitech Z906: a media player on top of the ESPHome z906 bridge."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_DEVICE_ID, REQUIRED_ROLES
from .discovery import find_entities

PLATFORMS = [Platform.MEDIA_PLAYER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the media player once the ESPHome entities exist."""
    found = find_entities(hass, entry.data[CONF_DEVICE_ID])
    missing = [role for role in REQUIRED_ROLES if role not in found]
    if missing:
        raise ConfigEntryNotReady(f"Z906 entities not found: {', '.join(missing)}")
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_reload))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the media player."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Apply changed options."""
    await hass.config_entries.async_reload(entry.entry_id)
