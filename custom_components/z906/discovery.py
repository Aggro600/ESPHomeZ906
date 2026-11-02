"""Find the entities of a Z906 bridge on an ESPHome device."""

from __future__ import annotations

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er

from .const import ROLES


@callback
def find_entities(hass: HomeAssistant, device_id: str) -> dict[str, str]:
    """Return role -> entity_id, using the names set in the ESPHome configuration."""
    found: dict[str, str] = {}
    for entry in er.async_entries_for_device(er.async_get(hass), device_id):
        if entry.platform != "esphome":
            continue
        name = (entry.original_name or "").strip().lower()
        for role, (domain, wanted) in ROLES.items():
            if entry.domain == domain and name == wanted:
                found[role] = entry.entity_id
    return found
