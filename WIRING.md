# Wiring – and rewiring for the mode without console

> [!CAUTION]
> **Unplug everything before you touch a single wire.**
>
> 1. Switch the Z906 off and **pull the subwoofer's mains plug**.
> 2. **Pull the USB cable of the ESP32.**
> 3. Only then move, add or remove wires on the DE-15 adapters and the ESP32 terminals.
>
> Pin 11 carries the console's supply and pin 15 the amplifier's enable line. A wire touching the wrong terminal
> while powered can damage the amplifier, the console or the ESP32. Never rewire while anything is plugged in.

> [!WARNING]
> **Install the firmware first, rewire second.** Firmware 1.1.0 behaves exactly like 1.0.x as long as you do not add
> `amp_enable_pin` / `console_enable_pin`. Rewiring with an older firmware (or without these two options) leaves the
> amplifier without its enable signal: **no sound**.

## Two setups

| | Standard (1.0.x and later) | Mode without console (1.1.0 and later) |
|---|---|---|
| Pin 15 | straight through, amplifier ↔ console | **split**: amplifier → GPIO25, console → GPIO26 |
| Pin 7 | straight through | **not connected** |
| GPIO35 | optional diagnostics on pin 15 | **empty** |
| Firmware options | – | `amp_enable_pin: 25`, `console_enable_pin: 26`, `without_console`, `power_switch` |
| Console | switches the amplifier | in "without console" stays off and dark; otherwise works as before |

All other pins stay as in the [README](README.md#wiring) (1–6, 8–11, 14 straight through; 12/13 split through the
ESP on GPIO16/17 and GPIO22/23; GND to GND).

## Mode without console – the two wire changes

"Amplifier adapter" = the DE-15 adapter that plugs into the subwoofer. "Console adapter" = the adapter the console
cable plugs into.

```
BEFORE                                           AFTER
amplifier adapter 15 ──┬── console adapter 15    amplifier adapter 15 ───── ESP GPIO25
                       └── ESP GPIO35            console adapter 15   ───── ESP GPIO26
amplifier adapter 7  ───── console adapter 7     amplifier adapter 7        (empty)
                                                 console adapter 7          (empty)
                                                 ESP GPIO35                 (empty)
```

Step by step:

1. **Install firmware 1.1.0** with the four options below while the old wiring is still in place, and check that
   everything still works (it does – in console mode nothing changes yet).
2. **Unplug everything** (see the caution box at the top).
3. **Pin 15:** there must be no connection left between the two pin-15 terminals.
   - pin 15 of the **amplifier adapter** → ESP terminal **25**
   - pin 15 of the **console adapter** → ESP terminal **26**
   - ESP terminal **35** stays empty
4. **Pin 7:** remove the wire between the two pin-7 terminals; both stay empty.
5. Plug the ESP32 back in, then the subwoofer.
6. **Test console mode:** switch the console on as usual – sound must come as before.
7. **Test the mode without console:** switch the console off, turn on **Without console**, then **Power switch**.
   After about 1 s the amplifier answers and plays; the console stays dark.

```yaml
z906:
  # ...
  amp_enable_pin: 25
  console_enable_pin: 26
  without_console:
    name: "Without console"
  power_switch:
    name: "Power switch"
```

## Why each change

- **Pin 15** is "console presence": the amplifier only powers its speakers while this pin is held at 0 V. The ESP
  holds the amplifier's side itself (open drain – the amplifier has its own pull-up) and reads the console's side
  (internal pull-up). In console mode it simply passes the console's level on.
- **GPIO26, not GPIO35:** GPIO34–39 have no internal pull-up. With the console off its pin 15 would float there and
  the ESP would read random levels. The firmware refuses GPIO34–39 for `console_enable_pin`.
- **Pin 7:** with it connected, the switched-off console makes the amplifier restart about every 20 s and it never
  answers. The console works normally without pin 7 (tested).

## Things that will break it

| Don't | What happens |
|---|---|
| Rewire while the subwoofer or the ESP is powered | possible damage to amplifier, console or ESP |
| Split pin 15 but keep a firmware without `amp_enable_pin` / `console_enable_pin` | amplifier never switches on – no sound |
| Set the two options but leave pin 15 joined (or put both pin-15 wires on GPIO25 **and** 26 together) | the ESP pulls the joined line low and holds itself there – the amplifier no longer switches off |
| Use GPIO34–39 for the console side | no pull-up – random on/off (the firmware rejects it) |
| Connect amplifier pin 15 to 3.3 V / 5 V or to GND permanently | to 3.3 V/5 V: amplifier stays off; to GND: always on, no control |
| Leave pin 7 connected in the mode without console | amplifier restarts every ~20 s |

## Going back

First turn **Without console** off (otherwise the bridge keeps ignoring the console). Then unplug everything, put
both pin-15 wires back into the **same** terminal (e.g. both into 35) and reconnect pin 7. Remove the four options
from the YAML and install the firmware again.

## Notes

- With pin 15 through the ESP the amplifier depends on the ESP: while it restarts (e.g. a firmware update) the
  sound is off for a few seconds.
- In the mode without console the console and its remote do nothing, and there is no automatic standby – switch off
  from Home Assistant (e.g. an automation).
- Switching on works like the console and like zarpli/BreadJS: pin 15 to 0 V, ask for the status until the amplifier
  answers, then `30 11 11 <input> <effect> 39`. Without the final `39` (mute off) it runs but stays silent.

---

## Deutsch – Kurzfassung

> [!CAUTION]
> **Vor jedem Umstecken alles ausstecken:** Z906 aus, **Netzstecker des Subwoofers ziehen**, **USB-Kabel vom ESP32
> ziehen**. Erst dann Kabel umstecken. Niemals unter Spannung umbauen – ein falsch berührter Kontakt kann Verstärker,
> Konsole oder ESP beschädigen.

> [!WARNING]
> **Erst die Firmware 1.1.0 installieren, dann umstecken.** Ohne `amp_enable_pin`/`console_enable_pin` verhält sich
> 1.1.0 wie 1.0.x. Umgesteckt mit alter Firmware = **kein Ton**.

Umbau für den Modus ohne Konsole:

- Pin 15 **Verstärker-Adapter** (steckt im Subwoofer) → ESP-Klemme **25**
- Pin 15 **Konsolen-Adapter** (Konsolenkabel steckt darin) → ESP-Klemme **26**
- **keine** Verbindung mehr zwischen den beiden Pins 15, ESP-Klemme **35 leer**
- Kabel zwischen den beiden **Pins 7 entfernen**

Danach: zuerst den Modus „Konsole“ testen (an der Konsole einschalten → Ton), dann Konsole aus, **Without console**
an, **Power switch** an.
