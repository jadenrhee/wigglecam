# Wiring & Assembly

Safety notes are in [safety-checklist.md](safety-checklist.md). The build
proceeds with the batteries out until the final step.

## System block diagram

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

## GPIO map

| Pin (BCM) | Direction | Function | Notes |
|-----------|-----------|----------|-------|
| GPIO 17 | in, pull-up | Shutter button | Button shorts to GND; debounced in software |
| GPIO 18 | out | Flash MOSFET gate | Boot-default pull-down = flash stays off during boot |
| GPIO 27 | in, pull-up | Filter/mode button | Optional |
| I2C (GPIO 2/3) | bidir | Camarray HAT control + X1202 fuel gauge (0x36) | Shared bus, different addresses, no conflict |

## Flash driver schematic

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

## Assembly order

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
