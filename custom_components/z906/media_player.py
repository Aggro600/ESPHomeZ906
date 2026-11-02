"""Media player for the Logitech Z906, backed by the entities of the ESPHome bridge."""

from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import CONF_DEVICE_ID, CONF_POWER_OFF, CONF_POWER_ON
from .discovery import find_entities

VOLUME_STEP = 0.03


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add the media player."""
    async_add_entities([Z906MediaPlayer(hass, entry, find_entities(hass, entry.data[CONF_DEVICE_ID]))])


class Z906MediaPlayer(MediaPlayerEntity):
    """The Z906 as one media player."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False
    _attr_device_class = MediaPlayerDeviceClass.SPEAKER
    _attr_volume_step = VOLUME_STEP

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, entities: dict[str, str]) -> None:
        """Remember the entities of the bridge and join its device."""
        self._entities = entities
        self._power_on = entry.options.get(CONF_POWER_ON)
        self._power_off = entry.options.get(CONF_POWER_OFF)
        self._attr_unique_id = f"{entry.entry_id}_media_player"
        device = dr.async_get(hass).async_get(entry.data[CONF_DEVICE_ID])
        if device:
            self._attr_device_info = DeviceInfo(connections=device.connections, identifiers=device.identifiers)
        features = (
            MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_STEP
            | MediaPlayerEntityFeature.SELECT_SOURCE
        )
        if "effect" in entities:
            features |= MediaPlayerEntityFeature.SELECT_SOUND_MODE
        if self._power_on:
            features |= MediaPlayerEntityFeature.TURN_ON
        if self._power_off:
            features |= MediaPlayerEntityFeature.TURN_OFF
        self._attr_supported_features = features

    async def async_added_to_hass(self) -> None:
        """Follow the entities of the bridge."""
        self.async_on_remove(
            async_track_state_change_event(self.hass, list(self._entities.values()), self._changed)
        )
        self._refresh()

    @callback
    def _changed(self, _event: Event[EventStateChangedData]) -> None:
        self._refresh()
        self.async_write_ha_state()

    def _usable(self, role: str):
        """Return the state object of a role if it has a value."""
        state = self.hass.states.get(self._entities.get(role, ""))
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None
        return state

    @callback
    def _refresh(self) -> None:
        power = self._usable("power")
        self._attr_available = power is not None
        self._attr_state = None
        if power is not None:
            self._attr_state = MediaPlayerState.ON if power.state == STATE_ON else MediaPlayerState.OFF

        volume = self._usable("volume")
        self._attr_volume_level = None
        if volume is not None:
            try:
                self._attr_volume_level = float(volume.state) / float(volume.attributes.get("max", 100))
            except ValueError:
                pass

        source = self._usable("input")
        self._attr_source = source.state if source else None
        self._attr_source_list = source.attributes.get("options") if source else None

        effect = self._usable("effect")
        self._attr_sound_mode = effect.state if effect else None
        self._attr_sound_mode_list = effect.attributes.get("options") if effect else None

    async def async_set_volume_level(self, volume: float) -> None:
        """Set the main volume (0..1)."""
        state = self._usable("volume")
        maximum = float(state.attributes.get("max", 100)) if state else 100.0
        await self.hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": self._entities["volume"], "value": round(volume * maximum)},
            blocking=True,
        )

    async def async_select_source(self, source: str) -> None:
        """Select the input."""
        await self._select("input", source)

    async def async_select_sound_mode(self, sound_mode: str) -> None:
        """Select the effect (the amplifier applies it on inputs 1, 2 and 6)."""
        await self._select("effect", sound_mode)

    async def _select(self, role: str, option: str) -> None:
        await self.hass.services.async_call(
            "select", "select_option", {"entity_id": self._entities[role], "option": option}, blocking=True
        )

    async def async_turn_on(self) -> None:
        """Run the configured power-on entity."""
        await self._run(self._power_on)

    async def async_turn_off(self) -> None:
        """Run the configured power-off entity."""
        await self._run(self._power_off)

    async def _run(self, entity_id: str | None) -> None:
        if not entity_id:
            return
        domain = entity_id.split(".", 1)[0]
        service = "press" if domain in ("button", "input_button") else "turn_on"
        await self.hass.services.async_call(domain, service, {"entity_id": entity_id}, blocking=True)
