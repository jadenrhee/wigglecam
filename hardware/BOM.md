# Bill of Materials

Prices are approximate (mid-2026, USD) and drift over time.
Every part below was chosen so the whole chain is plug-compatible:
one CSI port for all four synchronized cameras, one DSI port for the
screen, one 5.1 V/5 A battery HAT rated for exactly what the Pi 5 needs.

## Core electronics

| # | Part | Qty | ~Price | Why this part |
|---|------|-----|--------|---------------|
| 1 | Raspberry Pi 5 (8 GB) | 1 | $80 | Two 22-pin MIPI ports (cameras + display), enough CPU for live preview and GIF assembly |
| 2 | [Arducam 16MP IMX519 Autofocus Synchronized Quad-Camera Kit](https://www.arducam.com/arducam-16mp-imx519-autofocus-synchronized-quad-camera-kit-for-raspberry-pi-nvidia-jetson-nano-xavier-nx.html) | 1 | $260 | Camarray HAT hardware-syncs all 4 sensors for truly simultaneous exposure, the one thing a wigglegram cannot fake in software. Quad mode outputs one 4656×3496 frame |
| 3 | [Waveshare 4.3" DSI LCD, 800×480 capacitive touch](https://www.waveshare.com/4.3inch-dsi-lcd.htm), **Rev 2.2 or newer** | 1 | $40 | DSI leaves the CSI port free; Rev ≤2.1 will NOT boot on a Pi 5 (power-detect false short) |
| 4 | Pi 5 DSI display cable (official, or Waveshare Pi5-Display-Cable-200mm) | 1 | $4 | Pi 5 uses 22-pin mini connectors, so the generic 15-pin cable does not fit |
| 5 | [Geekworm X1202 UPS HAT](https://geekworm.com/products/x1202) | 1 | $37 | 5.1 V/5 A output (the Pi 5's full requirement), onboard BMS with over-current/over-voltage/reverse-cell protection, mounts underneath so camera/display ports stay free |
| 6 | 18650 cells, flat-top unprotected, ≥8 A rated (Samsung 35E / Molicel M35A) | 4 | $28 | X1202 bay fits max 65.3 mm, so protected cells are too long; the X1202's own BMS provides protection. Sourced from a reputable dealer (18650BatteryStore, IMR), never marketplace no-names |
| 7 | microSD 64 GB, A2 class | 1 | $12 | OS + captures |
| 8 | Raspberry Pi Active Cooler | 1 | $6 | Pi 5 throttles without it inside an enclosure |

## Flash circuit (hand-soldered on perfboard; see wiring.md)

| # | Part | Qty | ~Price | Notes |
|---|------|-----|--------|-------|
| 9 | Cree XP-G3 (or XP-G2) LED on 20 mm star MCPCB | 2 | $8 | ~500 lm each at 1 A pulse |
| 10 | IRLZ44N logic-level N-MOSFET, TO-220 | 1 | $2 | Fully on at 3.3 V gate drive; 2 A load is far below its 47 A rating |
| 11 | 2.2 Ω 5 W wirewound resistor | 2 | $2 | Sets ~1 A per LED branch; 2.2 W dissipation each during the pulse |
| 12 | 100 Ω 1/4 W (gate series), 100 kΩ 1/4 W (gate pulldown) | 1+1 | $1 | Pulldown keeps flash OFF during boot |
| 13 | 2200 µF 10 V low-ESR electrolytic | 2 | $4 | Reservoir that supplies the 2 A pulse so the 5 V rail doesn't sag |
| 14 | Polyfuse (PTC), 3 A hold | 1 | $1 | Protects the flash branch wiring on a fault |
| 15 | Perfboard 50×70 mm, JST-XH connectors, 20 AWG silicone wire, heat-shrink | 1 set | $12 | |

## Controls, assembly, enclosure

| # | Part | Qty | ~Price | Notes |
|---|------|-----|--------|-------|
| 16 | 12 mm momentary pushbutton (shutter + filter) | 2 | $4 | |
| 17 | M3 heat-set inserts + M3×10, M2×6 self-tap, M2.5×16 standoffs, M3×8 | kit | $12 | See enclosure/README.md |
| 18 | 1/4-20 hex nut (tripod mount) + epoxy | 1 | $2 | |
| 19 | Panel-mount USB-C extension (charging port) | 1 | $8 | Routes X1202's USB-C input to the case wall |
| 20 | Enclosure print, PETG (print service) | 2 shells | $30 | See enclosure/README.md for services |

**Total: roughly $550.**

## Compatibility cross-check (why these work together)

- Camera kit → Pi 5 **CAM0** port (needs the 22-pin cable included/adapter);
  enabled with `dtoverlay=imx519,cam0`. Uses ONE CSI port for all 4 cams.
- Display → Pi 5 **DISP1** port via Pi-5-specific cable. No conflict with cameras.
- X1202 powers the Pi through the GPIO 5 V pins at 5.1 V/5 A, the same
  budget as the official 27 W adapter, so no undervoltage warnings.
- X1202 mounts on the **bottom**; Camarray HAT sits on top of the 40-pin
  header via stacking header, and it only uses I2C + 3V3/5V/GND pins, leaving
  GPIO 17/18/27 free for our button, flash, and mode pins.
- Flash draws from the X1202 5 V rail: worst-case system peak
  (Pi ~2.4 A + display 0.3 A + cameras ~0.4 A + flash 2 A ≈ 5.1 A) is
  covered for the 120 ms pulse by the 4400 µF reservoir. Math in
  power-budget.md.
