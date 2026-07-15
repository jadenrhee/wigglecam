# Wiring & Assembly

Safety notes are in [safety-checklist.md](safety-checklist.md). The build
proceeds with the batteries out until the final step.

## Two versions of the electronics

There are two versions of the flash + controls electronics in this
repo. **v2, the
[wigglecam-controller](https://github.com/jadenrhee/wigglecam-controller)
RP2040 board, is the current design.** I'm keeping v1 documented too,
because you can build it without ordering a PCB, and it's what the
Python firmware drives today.

| | v1 (perfboard) | v2 (controller board, current) |
|---|----------------|---------------------------------|
| Flash driver | IRLZ44N MOSFET switched by Pi GPIO 18; 2.2 Ω power resistors set ~1 A per LED | op-amp constant-current sinks on the controller, settable 0-1 A per LED in 1% steps |
| Flash safety | software cap in `flash.py` | enforced in hardware on the controller: pulldown holds it off through boot, 150 ms pulse cap, 800 ms cooldown, 500 ms watchdog. Holds even if the Pi hangs |
| Shutter / mode | buttons on GPIO 17/27, debounced in software | shutter button + rotary encoder into the controller, RC + firmware debounce |
| Capture sync | software timing only | controller pulses Pi GPIO 17 once the flash is at current |
| Battery telemetry | X1202 fuel gauge (I2C 0x36) | X1202 fuel gauge, plus an in-line INA219 monitor on the controller |
| Pi connection | 3 GPIO lines + I2C | one 2x6 socket on header pins 1-12: I2C slave **0x17**, UART as fallback |
| Pi-side firmware | works today (`gpiozero`) | I2C client still to be written; register map is in the controller's [protocol doc](https://github.com/jadenrhee/wigglecam-controller/blob/main/docs/protocol.md) |

Heads up: the two versions are **mutually exclusive on the header**.
v1 *drives* GPIO 18 (flash gate) and *reads* GPIO 17 (shutter), while
v2 uses those same two pins as *inputs* from the controller (capture
sync on 17, event line on 18). Build one or the other, not both.

---

## v2: controller-board build (current)

### System block diagram

```
                 ┌─────────────┐  22-pin CSI   ┌──────────────┐
  4x IMX519 ────▶│ Camarray HAT│──────────────▶│ CAM0         │
  camera modules │ (hw sync)   │               │              │
                 └─────────────┘               │ Raspberry    │
                 ┌─────────────┐  22-pin DSI   │ Pi 5         │
  4.3" touch ◀──▶│ Rev2.2 LCD  │◀─────────────▶│ DISP1        │
                 └─────────────┘               │              │
  ┌────────────┐    5 V pack feed              │              │
  │ X1202 UPS  │═══▶ VBAT_IN ─10 mΩ─ VBAT_OUT ═▶ 5 V pins     │
  │ 4x 18650   │    (in-line INA219 telemetry) │              │
  └────────────┘                               │ GPIO 1-12    │
      ▲ USB-C (panel-mount) - charge input     └──────┬───────┘
                                                      │ 2x6 socket:
                                                      │ 5 V + GND down,
                                                      │ I2C 0x17 (UART fallback),
                                                      │ sync -> GPIO17, ATTN -> GPIO18
  top-plate ─── SHUTTER JST ──▶ ┌─────────────────────┴────────────────┐
  shutter button                │      RP2040 camera controller        │
                                │  EC11 encoder + status LED on board  │
                                │    op-amp constant-current sinks     │
                                └───────┬─────────────────┬────────────┘
                                   LED1 │ JST        LED2 │ JST
                                        ▼                 ▼
                                     XP-G3             XP-G3
                                    (1 A pulse)       (1 A pulse)
```

### The 2x6 header (Pi GPIO pins 1-12)

The controller has a 2x6 socket that seats directly on the first
twelve pins of the Pi 5 header. The Camarray HAT stacks above it on a
tall stacking header, so these pins stay reachable.

| Pi pin (physical) | Signal | Notes |
|-------------------|--------|-------|
| 1 | 3V3 | reference only, the controller doesn't use it |
| 2, 4 | 5 V | controller power in, through a 3 A polyfuse and a reverse-polarity FET; this node is also the flash rail |
| 3, 5 | SDA, SCL (GPIO 2/3) | controller is I2C slave **0x17** at 400 kHz; the Pi 5's onboard 1.8 kΩ pullups serve the bus |
| 6, 9 | GND | common ground |
| 7 | GPIO 4 | spare, unused |
| 8 | GPIO 14 (TXD) | Pi TX to controller RX, the UART fallback link (330 Ω in series) |
| 10 | GPIO 15 (RXD) | controller TX to Pi RX (330 Ω in series) |
| 11 | GPIO 17 | **capture sync, into the Pi.** Pulses high when a trigger fires; the capture loop waits on this edge |
| 12 | GPIO 18 | **ATTN, into the Pi.** High while a button/encoder event is waiting; the Pi can poll it or take an interrupt |

One shared Pi I2C bus, three different addresses, no conflicts:
Camarray HAT control, X1202 fuel gauge (0x36), controller (0x17).

### Off-board connections (all JST-XH)

| Connector | Goes to | Notes |
|-----------|---------|-------|
| LED1, LED2 | one Cree XP-G3 star each | constant-current sinks, so **no ballast resistors**. Current is set per shot over I2C (`FLASH_PCT`) |
| SHUTTER | top-plate shutter button | has a TVS (surge protector) diode at the connector, since this line leaves the enclosure |
| VBAT_IN | X1202 5 V output | pack feed in |
| VBAT_OUT | Pi 5 V pins | pack feed out, through the 10 mΩ shunt the INA219 reads. This is how the controller knows real system voltage and current |

The filter/mode selector is the rotary encoder **on the controller
board itself** (the knob pokes through the enclosure wall). v1's
second pushbutton goes away.

### Bring-up

Follow the controller repo's
[README](https://github.com/jadenrhee/wigglecam-controller#next-steps-in-order).
Short version: power the board from USB-C first (the flash rail is
intentionally dead on USB power), flash `camctrl.uf2` over BOOTSEL,
check that `i2cdetect -y 1` on the Pi shows 0x17, and bench-test the
flash sinks at 1 A per branch with a current probe **before** the LEDs
get connected. One quirk of this board revision: don't press BOOTSEL
while it's running.

**Firmware status:** `firmware/wigglecam` currently drives the v1
electronics directly (`gpiozero`). The v2 I2C client (trigger, flash
setup, encoder/button events, battery readings) still needs to be
written. The full register map is in the controller repo's
[protocol doc](https://github.com/jadenrhee/wigglecam-controller/blob/main/docs/protocol.md).

---

## v1: direct-GPIO perfboard build

The original electronics: everything hangs straight off the Pi header.
No PCB order needed, and the current Python firmware supports it
as-is.

### System block diagram

```
                 ┌─────────────┐  22-pin CSI   ┌──────────────┐
  4x IMX519 ────▶│ Camarray HAT│──────────────▶│ CAM0         │
  camera modules │ (hw sync)   │               │              │
                 └─────────────┘               │ Raspberry    │
                 ┌─────────────┐  22-pin DSI   │ Pi 5         │
  4.3" touch ◀──▶│ Rev2.2 LCD  │◀─────────────▶│ DISP1        │
                 └─────────────┘               │              │
                                               │ GPIO17 ◀── shutter button ── GND
  ┌────────────┐  5.1V/5A via GPIO 5V pins     │ GPIO27 ◀── mode button ──── GND
  │ X1202 UPS  │──────────────────────────────▶│ GPIO18 ───▶ flash gate
  │ 4x 18650   │────── 5V flash tap ──▶ flash board ──▶ 2x XP-G3 LED
  └────────────┘                               └──────────────┘
      ▲ USB-C (panel-mount, case wall): charge input
```

### GPIO map

| Pin (BCM) | Direction | Function | Notes |
|-----------|-----------|----------|-------|
| GPIO 17 | in, pull-up | Shutter button | Button shorts to GND; debounced in software |
| GPIO 18 | out | Flash MOSFET gate | Boot-default pull-down = flash stays off during boot |
| GPIO 27 | in, pull-up | Filter/mode button | Optional |
| I2C (GPIO 2/3) | bidir | Camarray HAT control + X1202 fuel gauge (0x36) | Shared bus, different addresses, no conflict |

### Flash driver schematic

```
   X1202 5V tap ──── PTC 3A ────┬──────────────┬──────────────┐
                                │              │              │
                              ═╪═ 2200µF     ═╪═ 2200µF       │
                                │  10V         │  10V         ├─────────────┐
                               GND            GND             │             │
                                                            [2.2Ω 5W]    [2.2Ω 5W]
                                                              │             │
                                                            ▼ XP-G3      ▼ XP-G3
                                                              │             │
                                                              └──────┬──────┘
                                                                     │ D
  Pi GPIO18 ────[100Ω]────┬──────────────────────────────────────── G   IRLZ44N
                          │                                          │ S
                       [100kΩ]                                       │
                          │                                          │
                         GND ────────────────────────────────────── GND (common with Pi)
```

Branch current check: (5.1 V − ~2.9 V LED Vf) / 2.2 Ω ≈ **1.0 A per LED**,
2.0 A total. Resistor dissipation I²R ≈ 2.2 W each, only during the
≤150 ms pulse (firmware-capped in `flash.py`), so 5 W parts loaf.
MOSFET dissipation at 2 A with Rds(on) ≈ 0.04 Ω at 3.3 V gate ≈ 0.16 W, no
heatsink needed. The 100 kΩ pulldown guarantees the gate is low (flash off)
whenever the Pi is booting or the firmware isn't running.

**Grounds must be common:** flash board GND, X1202 GND, and Pi GND are the
same net, starred at the X1202 output terminal.

---

## Assembly order (both versions)

The build comes up incrementally, each stage verified before the next is added:

1. **Bare Pi bench-test** (official 27 W adapter, no HATs): Raspberry Pi OS
   Bookworm 64-bit flashed, booted, updated.
2. **Cameras:** the Camarray HAT connects to CAM0 with the 22-pin cable
   (contacts on the correct side per Arducam's Pi 5 guide) and the 4
   modules mount to it. `dtoverlay=imx519,cam0` goes in
   `/boot/firmware/config.txt`, then a reboot and a check with
   `libcamera-still --list-cameras` and a test capture.
3. **Display:** connects to DISP1 with the Pi-5-specific cable, driver-free
   on Bookworm, touch verified.
4. **Flash board:** soldered per the schematic on perfboard and bench-tested
   alone before it meets the Pi: powered from a bench/USB 5 V source, the
   gate driven from 3.3 V through a resistor, ~1 A per branch confirmed with
   a multimeter in series, and the LEDs confirmed OFF with the gate floating
   (pulldown working).
5. **Buttons:** each wires between its GPIO and GND, no external resistors
   (internal pull-ups).
6. **X1202:** mounts under the Pi on its standoffs, 5 V feed set per the
   [X1202 wiki](https://wiki.geekworm.com/X1202). Each 18650's orientation
   is checked twice against the bay markings before insertion; reverse
   protection exists but isn't leaned on.
7. **First integrated boot on battery,** outside the enclosure, with a
   multimeter on the 5 V rail; `vcgencmd get_throttled` must return `0x0`.
8. **Software:** `sudo apt install python3-picamera2 python3-pyqt5
   python3-opencv`, `pip install -r firmware/requirements.txt`, then
   `python3 -m wigglecam.app`. The hotspot comes up with
   `nmcli device wifi hotspot ssid WiggleCam password <chosen>`.
9. **Enclosure:** only after everything works on the bench. Heat-set inserts
   go in, the stack seats, ribbons fold (never creased sharply), flash and
   button wiring get zip-tie strain relief, and it closes up.
