# Architecture

I started from what a wigglegram actually needs and let each
requirement pick the hardware. This doc walks through that reasoning,
then covers the electronics, the data flow, and what I'd still like to
fix.

## What a wigglegram needs

**1. Four views of the same instant.** If the four exposures are even
a few milliseconds apart, anything moving (people, hair, leaves)
ghosts between frames and the 3-D illusion collapses. Triggering four
separate cameras from software can't get you there: four ESP32-CAMs,
or four Pi cameras behind a multiplexer that switches between them,
all take their pictures at slightly different times. The Arducam
Camarray HAT solves this in hardware. It clocks all four IMX519
sensors from one source and merges them into a single 2x2-stitched
frame, so the exposures are simultaneous because they literally share
a clock, and the Pi sees just one ordinary camera on one CSI (camera
ribbon) port.

**2. A wide enough baseline.** The 3-D effect comes from the lenses
being horizontally offset from each other. The enclosure spaces the
four modules 40 mm apart, 120 mm from the first lens to the last,
similar to the Nishika N8000 film camera this is based on. In
software I align the four frames on the subject (`wiggle.py`, phase
correlation on a center crop), so the subject stays put and the
background does the wiggling.

**3. Flash that's synced to the exposure.** Since the flash is LED and
not xenon, there's no microsecond-level trigger problem. The LEDs just
stay on for a window that brackets the whole capture. In the current
(v2) electronics, the controller board brings the flash up to its set
current and then pulses a sync line, so the exposure lands inside the
lit window by design. In the older v1 electronics, `flash.py` brackets
the capture in software with a roughly 120 ms pulse. Both versions
have a hard cap so no bug can leave 2 A flowing: on v2 the cap lives
on the controller itself and holds even if the Pi hangs.

**4. Handheld power.** The Pi 5 wants 5 V at up to 5 A, which is past
what generic power banks and boost boards will do. The Geekworm X1202
(four 18650 cells, battery management, 5.1 V / 5 A out) is built for
the Pi 5 specifically and mounts underneath it, which keeps the
top-side camera and display connectors free.

**5. Instant sharing.** AirDrop is Apple-proprietary (it runs on their
AWDL protocol) and can't be implemented on a Pi. Instead the camera
runs its own Wi-Fi hotspot and a small Flask gallery (`share.py`).
After each shot the touchscreen shows a QR code that opens the GIF
right on any phone, iPhone or Android, nothing to install.

## The electronics: v1 perfboard vs v2 controller board

The flash and controls electronics exist in two versions. Both are
wired up in [hardware/wiring.md](../hardware/wiring.md).

**v1 (perfboard)** hangs everything straight off the Pi's header.
GPIO 18 gates an IRLZ44N MOSFET, 2.2 Ω power resistors set roughly
1 A through each LED, and GPIO 17/27 read the shutter and mode buttons
with debouncing done in software. It needs no PCB order, and it's what
the Python firmware drives today.

**v2 (current)** moves the timing-critical and analog work onto a
dedicated RP2040 co-processor, the
[wigglecam-controller](https://github.com/jadenrhee/wigglecam-controller)
board. Four reasons I went this way:

- **Flash current you can trust.** With a plain resistor, the LED
  current drifts with the LED's forward voltage and with battery sag.
  The controller uses op-amp constant-current sinks instead, so each
  LED gets exactly the commanded current, settable from 0 to 100% of
  1 A per shot.
- **Safety that doesn't depend on Linux.** Linux plus Python is not
  real-time. In v1, a hung process means 2 A keeps flowing until a
  software watchdog notices. The controller enforces a 150 ms pulse
  cap, an 800 ms cooldown, and a 500 ms watchdog on its own, and a
  pulldown resistor holds the flash off through reset and boot.
- **Deterministic capture timing.** The controller fires the flash,
  waits for it to reach current, then pulses a sync line into Pi
  GPIO 17. The capture loop waits on that edge instead of guessing at
  delays.
- **Better inputs and telemetry.** Debounced shutter in hardware, a
  rotary encoder for picking filters (one click per filter), and an
  in-line INA219 sensor that reports actual pack voltage and current,
  on top of the X1202's own fuel gauge.

The Pi keeps everything it's good at (capture, image processing, UI,
sharing) and sees the controller as an ordinary I2C peripheral at
address 0x17. The register map is in the controller repo's
[protocol doc](https://github.com/jadenrhee/wigglecam-controller/blob/main/docs/protocol.md).
Board status: fully routed, passes design rule checks, ready to order.
The Pi-side I2C client code is still on my list (see limitations
below).

## Data flow

```
4x IMX519 ─(hw sync)─▶ Camarray HAT ─CSI─▶ Picamera2
                                            ├── lores stream ─▶ Qt live preview (touch UI)
                                            └── still capture (4656x3496, flash bracketed)
                                                  └▶ split 2x2 ─▶ filter ─▶ align ─▶
                                                      ├▶ 4x JPEG stills
                                                      └▶ bounce GIF ─▶ Flask gallery ─▶ QR ─▶ phone
```

## Firmware layout

| Module | What it does |
|--------|--------------|
| `config.py` | every tunable in one place |
| `camera.py` | Picamera2 setup, stitched capture, 2x2 split |
| `flash.py` | flash pulse control (v1 GPIO gate today; v2 I2C client planned) |
| `filters.py` | the filter looks (B&W, sepia, vivid, film), all pure functions |
| `wiggle.py` | subject alignment, bounce sequencing, GIF/JPEG export |
| `share.py` | hotspot gallery server + QR generation |
| `app.py` | Qt touch UI, buttons, capture orchestration |

## Known limitations / future work

- Quad synchronized mode caps each view at 2328x1748 (~4 MP). That's
  the price of getting hardware sync over a single cable, and it's
  plenty for GIFs.
- GIF export takes 2-4 s on the Pi 5. An MP4 export path would be
  smaller files and faster.
- Autofocus is one setting for all four lenses in sync mode. Fixed
  focus at ~1.5 m works well for the classic wigglegram portrait.
- The Pi-side I2C client for the v2 controller board isn't written
  yet. `flash.py` and the button handling in `app.py` drive the v1
  electronics today. The register protocol is documented and stable,
  so it's a contained change.
