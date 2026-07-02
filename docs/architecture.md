# Architecture

## What a wigglegram needs, and how each need drove a decision

**1. Four views of the same instant.** If the four exposures are even a
few ms apart, anything moving (people, hair, leaves) ghosts between
frames and the 3-D illusion collapses. Software-triggering four
independent cameras (e.g. four ESP32-CAMs or four Pi cams on a mux that
*switches* between them) cannot achieve this. The Arducam Camarray HAT
clocks all four IMX519 sensors from one source and merges them into a
single 2×2-stitched frame — the exposures are simultaneous by
construction, and the Pi sees just one ordinary camera on one CSI port.

**2. Parallax baseline.** The 3-D effect comes from the lenses being
horizontally offset. The enclosure spaces the four modules 40 mm apart
(120 mm outer baseline) — similar to the Nishika N8000 film camera this
is inspired by. Frames are auto-aligned on the subject in software
(`wiggle.py`, phase correlation on a center crop) so the subject holds
still and the background does the wiggling.

**3. Flash synchronized to the exposure.** Because the flash is LED,
not xenon, there is no microsecond trigger problem: firmware simply
holds the LEDs on for a ~120 ms window that brackets the capture
(`flash.py`), with a hardware-independent watchdog cap so no bug can
leave 2 A flowing.

**4. Handheld power.** Pi 5 demands 5 V/5 A — beyond generic power
banks and boost boards. The Geekworm X1202 (4×18650, BMS, 5.1 V/5 A) is
purpose-built for it and mounts under the Pi, keeping the top-side
camera/display connectors free.

**5. Instant sharing.** AirDrop is Apple-proprietary (AWDL) and not
implementable on a Pi. Instead the camera runs its own Wi-Fi hotspot
and a small Flask gallery (`share.py`); after each shot the touchscreen
shows a QR code that opens the GIF directly on any phone — iPhone or
Android, no app install.

## Data flow

```
4x IMX519 ─(hw sync)─▶ Camarray HAT ─CSI─▶ Picamera2
                                            ├── lores stream ─▶ Qt live preview (touch UI)
                                            └── still capture (4656×3496, flash bracketed)
                                                  └▶ split 2×2 ─▶ filter ─▶ align ─▶
                                                      ├▶ 4x JPEG stills
                                                      └▶ bounce GIF ─▶ Flask gallery ─▶ QR ─▶ phone
```

## Firmware layout

| Module | Responsibility |
|--------|----------------|
| `config.py` | every tunable in one place |
| `camera.py` | Picamera2 setup, stitched capture, 2×2 split |
| `flash.py` | MOSFET gate control, watchdog-capped pulse |
| `filters.py` | pure-function looks (B&W, sepia, vivid, film) |
| `wiggle.py` | subject alignment, bounce sequencing, GIF/JPEG export |
| `share.py` | hotspot gallery server + QR generation |
| `app.py` | Qt touch UI, buttons, capture orchestration |

## Known limitations / future work

- Quad synchronized mode caps each view at 2328×1748 (~4 MP) — the
  price of single-cable hardware sync; plenty for GIFs.
- GIF export ~2-4 s on the Pi 5; an MP4 export path would be smaller
  files and faster.
- Autofocus is per-kit (one focus setting for all four in sync mode);
  fixed-focus at ~1.5 m works well for the classic wigglegram portrait.
