# ESPHome Z906

Logitech Z906 in Home Assistant with **ESPHome** – an ESP32 sits between the original console and the amplifier
(DE-15 cable) and **keeps the console fully working**.

Volume, subwoofer, centre, rear, input and effect show up as normal ESPHome entities (no MQTT broker needed);
everything you change on the console is reported back, everything you change in Home Assistant is shown on the
console.

Based on the idea and wiring of [Jupsi/logi_z906_wifi](https://github.com/Jupsi/logi_z906_wifi) (Arduino + MQTT),
rewritten as an ESPHome external component. Protocol: [nomis/logitech-z906](https://github.com/nomis/logitech-z906).

## What is different from the Arduino/MQTT version

- **Console starts reliably after a power cut.** While console and amplifier boot, both serial lines carry about one
  second of garbage. By chance it contains valid commands (speaker test `22`, headphones `10`, input selection …).
  A plain cable would just carry noise – an ESP in between turned it into clean bytes, after which the console
  ignored the power button / IR (only a 2–5 s window after power-on worked). An **interference filter** now passes
  only protocol bytes and mutes a direction for 300 ms after any invalid byte.
- **Forwarding always runs**, in its own FreeRTOS task, from the first second after boot – independent of WiFi,
  the API or logging. No more gating via pin 8/15.
- **No endless waits.** An incomplete `AA …` reply is dropped after 300 ms (the old code could hang until power was
  cut). Checksums are verified.
- **Commands from Home Assistant are only sent when the line is idle** and no reply is pending; state changes in
  HA only after the amplifier echoed the command.
- Fixes: `0x10` is *headphones connected*, not *power off* (power off = `0x36`); effect codes in the status reply
  are decoded correctly.

## Entities

| Entity | Notes |
|---|---|
| Volume, Volume Bass, Volume Center, Volume Rear | `number`, 0–100 % (100 % = level 43) |
| Input | `select`, Input 1 … Input 6 |
| Effect | `select`, 3D / 2.1 / 4.1 / None – only for inputs 1, 2, 6 (digital inputs follow the signal) |
| Power | `binary_sensor`, from the power-on/off sequence; after an ESP restart: console traffic = on, 75 s silence = off |
| Read status | `button`, reads levels/input/effects from the amplifier |

**Power on/off from Home Assistant is not possible over the serial link** – only the console can switch the
amplifier on (power button or IR). Use an IR sender for that.

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

Pin 8/9/15 are optional ADC diagnostics. Observed: pin 8 ≈ 3.2 V console awake (standby), ≈ 1.6 V console asleep,
≈ 0.1 V running.

## Installation

1. Copy [`z906.yaml`](z906.yaml) into your ESPHome configuration (it pulls the component from this repository
   via `external_components`) and add the secrets.
2. Flash once over USB, afterwards OTA.
3. Optional: [`homeassistant/z906_mediaplayer.yaml`](homeassistant/z906_mediaplayer.yaml) as a package makes the
   Z906 a `media_player` (volume set/up/down, source; add your IR script for on/off).

## Troubleshooting

```yaml
z906:
  debug_traffic: true          # every byte K>V (console→amp) / V>K (amp→console) in the log
  dump_capture:
    name: "Dump capture"       # button: first 3 minutes after boot (incl. pin voltages) from RAM to the log
```

The capture also covers the seconds after power-on, before WiFi/API are connected.

## License

GPL-3.0, like the project this is based on.
