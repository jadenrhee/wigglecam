# Wiring & Assembly

Read [safety-checklist.md](safety-checklist.md) first. Work with the
batteries OUT until the final step.

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
      ▲ USB-C (panel-mount, case wall) — charge input
```

## GPIO map

| Pin (BCM) | Direction | Function | Notes |
|-----------|-----------|----------|-------|
| GPIO 17 | in, pull-up | Shutter button | Button shorts to GND; debounced in software |
| GPIO 18 | out | Flash MOSFET gate | Boot-default pull-down = flash stays off during boot |
| GPIO 27 | in, pull-up | Filter/mode button | Optional |
| I2C (GPIO 2/3) | — | Camarray HAT control + X1202 fuel gauge (0x36) | Shared bus, different addresses — no conflict |

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
2.0 A total. Resistor dissipation I²R ≈ 2.2 W each — only during the
≤150 ms pulse (firmware-capped in `flash.py`), so 5 W parts loaf.
MOSFET dissipation at 2 A with Rds(on) ≈ 0.04 Ω at 3.3 V gate ≈ 0.16 W — no
heatsink needed. The 100 kΩ pulldown guarantees the gate is low (flash off)
whenever the Pi is booting or the firmware isn't running.

**Grounds must be common:** flash board GND, X1202 GND, and Pi GND are the
same net. Star the grounds at the X1202 output terminal.

## Assembly order

1. **Bench-test the Pi bare** (official 27 W adapter, no HATs): flash
   Raspberry Pi OS Bookworm 64-bit, boot, update.
2. **Cameras:** connect Camarray HAT to CAM0 with the 22-pin cable
   (contacts facing the correct side — check Arducam's Pi 5 guide). Mount
   the 4 modules. Add `dtoverlay=imx519,cam0` to `/boot/firmware/config.txt`,
   reboot, verify with `libcamera-still --list-cameras` then a test capture.
3. **Display:** connect to DISP1 with the Pi-5-specific cable. Should work
   driver-free on Bookworm. Verify touch.
4. **Flash board:** solder per schematic on perfboard. Before connecting to
   the Pi: power the board alone from a bench/USB 5 V source, drive the gate
   from 3.3 V through a resistor by hand, confirm ~1 A per branch with a
   multimeter in series, and confirm the LEDs are OFF with the gate floating
   (pulldown working).
5. **Buttons:** wire each between its GPIO and GND. No external resistors
   needed (internal pull-ups).
6. **X1202:** mount under the Pi with its standoffs. Set the correct 5 V
   feed per the [X1202 wiki](https://wiki.geekworm.com/X1202). **Check each
   18650 orientation twice against the bay markings before insertion** —
   reverse protection exists, but don't lean on it.
7. **First integrated boot on battery**, outside the enclosure, with a
   multimeter on the 5 V rail. `vcgencmd get_throttled` must return `0x0`.
8. **Software:** `sudo apt install python3-picamera2 python3-pyqt5
   python3-opencv`, `pip install -r firmware/requirements.txt`, run
   `python3 -m wigglecam.app`. Enable the hotspot:
   `nmcli device wifi hotspot ssid WiggleCam password <pick-one>`.
9. **Enclosure:** only after everything works on the bench. Heat-set
   inserts in, stack in, ribbons folded (never creased sharply), zip-tie
   strain relief on the flash and button wiring, close it up.
