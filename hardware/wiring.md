# Wiring & Assembly

Read [safety-checklist.md](safety-checklist.md) first. Keep the
batteries out until the final step.

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
      ▲ USB-C (panel-mount, case wall) - charge input
```

### GPIO map

| Pin (BCM) | Direction | Function | Notes |
|-----------|-----------|----------|-------|
| GPIO 17 | in, pull-up | Shutter button | button shorts to GND; debounced in software |
| GPIO 18 | out | Flash MOSFET gate | boot-default pull-down means the flash stays off while the Pi boots |
| GPIO 27 | in, pull-up | Filter/mode button | optional |
| I2C (GPIO 2/3) | - | Camarray HAT control + X1202 fuel gauge (0x36) | shared bus, different addresses, no conflict |

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

Checking the branch current: (5.1 V - ~2.9 V LED forward voltage) /
2.2 Ω = about **1 A per LED**, 2 A total. Each resistor dissipates
about 2.2 W, but only during the pulse (150 ms max, capped in
`flash.py`), so 5 W parts barely warm up. The MOSFET at 2 A with an
on-resistance around 0.04 Ω at a 3.3 V gate burns about 0.16 W, so no
heatsink. The 100 kΩ pulldown makes sure the gate sits low (flash off)
whenever the Pi is booting or the firmware isn't running.

**Grounds must be common.** Flash board GND, X1202 GND, and Pi GND are
all one net. Star the grounds at the X1202 output terminal.

---

## Assembly order (both versions)

1. **Bench-test the Pi bare** (official 27 W adapter, no HATs): flash
   Raspberry Pi OS Bookworm 64-bit, boot, update.
2. **Cameras:** connect the Camarray HAT to CAM0 with the 22-pin cable
   (contacts facing the right way; check Arducam's Pi 5 guide). Mount
   the 4 modules. Add `dtoverlay=imx519,cam0` to
   `/boot/firmware/config.txt`, reboot, verify with
   `libcamera-still --list-cameras`, then take a test capture.
3. **Display:** connect to DISP1 with the Pi-5-specific cable. Works
   without extra drivers on Bookworm. Verify touch.
4. **Flash electronics:**
   - *v2:* assemble and bring up the controller board per its README
     (USB-C first, sinks bench-tested at 1 A) before it ever touches
     the Pi or the LEDs. Then seat the 2x6 socket on header pins 1-12.
   - *v1:* solder the flash board per the schematic above. Before it
     touches the Pi: power it alone from a bench or USB 5 V source,
     drive the gate from 3.3 V through a resistor by hand, confirm
     about 1 A per branch with a multimeter in series, and confirm the
     LEDs stay OFF with the gate floating (that's the pulldown doing
     its job).
5. **Controls:**
   - *v2:* shutter button to the controller's SHUTTER connector. The
     encoder is on the board; just mount the knob through the
     enclosure wall.
   - *v1:* wire each button between its GPIO and GND. No external
     resistors needed, the Pi's internal pull-ups handle it.
6. **X1202:** mount under the Pi with its standoffs. Set up the 5 V
   feed per the [X1202 wiki](https://wiki.geekworm.com/X1202). On v2
   the feed runs through the controller's VBAT_IN/VBAT_OUT
   pass-through. **Check each 18650's orientation twice against the
   bay markings before inserting it.** There is reverse protection,
   but don't lean on it.
7. **First battery boot outside the enclosure**, with a multimeter on
   the 5 V rail. `vcgencmd get_throttled` must return `0x0`.
8. **Software:** `sudo apt install python3-picamera2 python3-pyqt5
   python3-opencv`, `pip install -r firmware/requirements.txt`, run
   `python3 -m wigglecam.app`. Enable the hotspot:
   `nmcli device wifi hotspot ssid WiggleCam password <pick-one>`.
9. **Enclosure last**, only after everything works on the bench.
   Heat-set inserts in, stack in, ribbons folded (folded, never
   creased), zip-tie strain relief on the flash and button wiring,
   close it up.
