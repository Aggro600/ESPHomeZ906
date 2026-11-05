"""Constants for the Logitech Z906 integration."""

DOMAIN = "z906"

CONF_DEVICE_ID = "device_id"
CONF_POWER_ON = "power_on_entity"
CONF_POWER_OFF = "power_off_entity"

# Entity names of the ESPHome z906 component -> role in the media player
ROLES = {
    "power": ("binary_sensor", "power"),
    "volume": ("number", "volume"),
    "input": ("select", "input"),
    "effect": ("select", "effect"),
    # Mode without console (firmware 1.1.0): the bridge switches the amplifier itself
    "power_switch": ("switch", "power switch"),
    "without_console": ("switch", "without console"),
}
REQUIRED_ROLES = ("power", "volume", "input")
