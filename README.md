<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Aggro600/ESPHomeZ906/main/logo-dunkel.png">
    <img src="https://raw.githubusercontent.com/Aggro600/ESPHomeZ906/main/logo.png" alt="Z906 Bridge" width="420">
  </picture>
</p>

# Logitech Z906 for Home Assistant

An ESP32 sits between the console and the amplifier of a Logitech Z906 (DE-15 cable) and brings the speaker
system into Home Assistant – **without** replacing the console. The console keeps working exactly as before;
everything you change there is reported back, and everything you change in Home Assistant is shown on the console.

This repository has two parts:

- **ESPHome firmware** for the ESP32 (`components/z906`, example [`z906.yaml`](https://github.com/Aggro600/ESPHomeZ906/blob/main/z906.yaml)): volume, subwoofer,
  centre and rear level, input, effect and power state as ESPHome entities. No MQTT broker needed.
- **Home Assistant integration** (`custom_components/z906`, installable through HACS): combines these entities into
  one **media player** with volume, source and sound mode, plus optional on/off through IR buttons.

## Installation

### 1. Build the bridge

Wire the ESP32 (see [Wiring](#wiring)); it needs its own USB power supply. Copy [`z906.yaml`](https://github.com/Aggro600/ESPHomeZ906/blob/main/z906.yaml) into your
ESPHome folder, add `api_key_z906`, `ota_pw`, `wifi_ssid` and `wifi_password` to your `secrets.yaml` and install it.
Flash once over USB, afterwards OTA. The component comes straight from this repository (`external_components`).
Add the device in Home Assistant through the ESPHome integration.

Keep the entity names `Power`, `Volume` and `Input` (and `Effect`) from the example; the integration finds them
by these names.

### 2. Install the integration

Open HACS, search for **Logitech Z906** and download it, then restart Home Assistant. Without HACS, copy
`custom_components/z906` into your configuration folder.

Go to **Settings → Devices & services → Add integration → Logitech Z906** and choose the ESPHome device. Optionally
choose entities that switch the amplifier on and off, such as IR buttons or scripts.

## What the bridge takes care of

- Passes everything through from the very first moment, in its own task, so the console starts regardless of when
  the IR command or the power button comes.
- **Start-up protection:** level steps during the wake-up sequence are held back, and the bridge sends nothing of
  its own for 4 s after power-on.
- Commands from Home Assistant are only sent when the line is idle and no reply is pending.
- Input changes like the console does them: mute, switch input, restore the input's effect, unmute.
- Interference filter for the garbage the amplifier sends while it boots.

## Entities

| Entity | Notes |
|---|---|
| Volume, Volume Bass, Volume Center, Volume Rear | `number`, 0–100 % (100 % = level 43) |
| Input | `select`, Input 1 … Input 6 |
| Effect | `select`, 3D / 2.1 / 4.1 / None – only for inputs 1, 2, 6 (digital inputs follow the signal) |
| Power | `binary_sensor`, from the power-on/off sequence; after an ESP restart: console traffic = on, 75 s silence = off |
| Read status | `button`, reads levels/input/effects from the amplifier |

**Power on/off is not possible over the serial link** – only the console can switch the amplifier on (power
button or IR). Choose IR buttons in the integration to get on/off in the media player.

## Wiring

ESP32 (e.g. ESP32-DevKit / WROOM – on WROVER boards GPIO16/17 are used by PSRAM, pick other pins).
Pins 1–11, 14, 15 go straight through (amplifier ↔ console); only the serial lines 12/13 are split through the ESP.

| Amplifier | Console | ESP32 |
|-----------|---------|--------|
| 1–7, 10, 11, 14 | same pin | – |
| 6 + GND | 6 | GND |
| 8 | 8 | GPIO32 (diagnostics only) |
| 9 | 9 | GPIO34 (diagnostics only) |
| – | 12 | GPIO17 (TX to console) |
| – | 13 | GPIO16 (RX from console) |
| 12 | – | GPIO22 (RX from amplifier) |
| 13 | – | GPIO23 (TX to amplifier) |
| 15 | 15 | GPIO35 (diagnostics only) |

Pin 8/9/15 are optional ADC diagnostics (leave them out in normal use, see Troubleshooting). Observed: pin 8 ≈ 3.2 V console awake (standby), ≈ 1.6 V console asleep,
≈ 0.1 V running.

## Troubleshooting

```yaml
z906:
  debug_traffic: true          # every byte K>V (console→amp) / V>K (amp→console) in the log
  dump_capture:
    name: "Dump capture"       # button: first 3 minutes after boot (incl. pin voltages) from RAM to the log
```

The capture also covers the seconds after power-on, before WiFi/API are connected.

Switch `debug_traffic` off again afterwards. With it (and the optional pin 8/9/15 ADC sensors) running, the amplifier
restarted when the volume was turned up quickly; without them it stays on.

## License

GPL-3.0, like the project this is based on.

## Credits

Idea and wiring: [Jupsi/logi_z906_wifi](https://github.com/Jupsi/logi_z906_wifi).
Protocol reference: [nomis/logitech-z906](https://github.com/nomis/logitech-z906/blob/main/protocol.rst).

> Known issue on one unit: switching to an input with the 3D effect made the amplifier reset – also with older
> firmware of the bridge. If you see the same, please test once with the console plugged directly into the
> amplifier (without the bridge) and report the result.
