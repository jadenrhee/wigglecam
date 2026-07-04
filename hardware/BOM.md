# Bill of Materials

Prices are ballpark (mid-2026, USD), so re-check before ordering. The
parts were picked so the whole chain plugs together: one CSI port for
all four synchronized cameras, one DSI port for the screen, and one
battery HAT that outputs the 5.1 V / 5 A a Pi 5 actually needs.

The flash + controls electronics come in two versions. **Build one,
not both** (they claim the same Pi pins, see [wiring.md](wiring.md)):
the **v2 controller board** (current design) or the **v1 perfboard
circuit** (no PCB order needed; it's what the firmware drives today).

## Core electronics (both versions)

| # | Part | Qty | ~Price | Why this part |
|---|------|-----|--------|---------------|
| 1 | Raspberry Pi 5 (8 GB) | 1 | $80 | two 22-pin MIPI ports (cameras + display) and enough CPU for live preview and GIF assembly |
| 2 | [Arducam 16MP IMX519 Autofocus Synchronized Quad-Camera Kit](https://www.arducam.com/arducam-16mp-imx519-autofocus-synchronized-quad-camera-kit-for-raspberry-pi-nvidia-jetson-nano-xavier-nx.html) | 1 | $260 | the Camarray HAT syncs all 4 sensors in hardware. Truly simultaneous exposure is the one thing you can't fake in software, so this part carries the project. Quad mode outputs one 4656x3496 frame |
| 3 | [Waveshare 4.3" DSI LCD, 800x480 capacitive touch](https://www.waveshare.com/4.3inch-dsi-lcd.htm), **Rev 2.2 or newer** | 1 | $40 | DSI leaves the camera port free. Careful: Rev 2.1 and older will NOT boot on a Pi 5 (power-detect false short) |
| 4 | Pi 5 DSI display cable (official, or Waveshare Pi5-Display-Cable-200mm) | 1 | $4 | the Pi 5 uses 22-pin mini connectors; the common 15-pin cable doesn't fit |
| 5 | [Geekworm X1202 UPS HAT](https://geekworm.com/products/x1202) | 1 | $37 | 5.1 V / 5 A output (the Pi 5's full requirement), hardware BMS with over-current/over-voltage/reverse-cell protection, and it mounts underneath so the camera/display ports stay free |
| 6 | 18650 cells, flat-top unprotected, rated 8 A or better (Samsung 35E / Molicel M35A) | 4 | $28 | the X1202 bay fits 65.3 mm max, so protected cells are too long. The X1202's own BMS is the protection. Buy from a real battery dealer (18650BatteryStore, IMR), never marketplace no-names |
| 7 | microSD 64 GB, A2 class | 1 | $12 | OS + captures |
| 8 | Raspberry Pi Active Cooler | 1 | $6 | the Pi 5 throttles without it inside a closed case |
| 9 | Cree XP-G3 (or XP-G2) LED on 20 mm star board | 2 | $8 | flash LEDs, about 500 lm each at a 1 A pulse. Needed in both versions |

## Flash + controls: v2 controller board (current)

| # | Part | Qty | ~Price | Notes |
|---|------|-----|--------|-------|
| 10 | [wigglecam-controller](https://github.com/jadenrhee/wigglecam-controller) PCB, JLCPCB 4-layer, assembled | 1 | ~$90 for the minimum run of 5 boards (get a live quote at order time) | Gerbers/BOM/CPL are in that repo's `fab/`. The 2x6 socket, SWD header, and JST connectors are hand-soldered through-hole parts |
| 11 | 12 mm momentary pushbutton (shutter) | 1 | $2 | filter selection moves to the board's rotary encoder, so no second button |
| 12 | JST-XH 2-pin cable assemblies + 20 AWG silicone wire, heat-shrink | 5 | $8 | LED1, LED2, SHUTTER, VBAT_IN, VBAT_OUT |

## Flash + controls: v1 perfboard version

Build this only if you're skipping the controller board. Hand-soldered
on perfboard; the schematic is in [wiring.md](wiring.md).

| # | Part | Qty | ~Price | Notes |
|---|------|-----|--------|-------|
| 13 | IRLZ44N logic-level N-MOSFET, TO-220 | 1 | $2 | fully on at a 3.3 V gate; our 2 A is nothing next to its 47 A rating |
| 14 | 2.2 Ω 5 W wirewound resistor | 2 | $2 | sets ~1 A per LED; each one dissipates 2.2 W during the pulse |
| 15 | 100 Ω 1/4 W (gate series), 100 kΩ 1/4 W (gate pulldown) | 1+1 | $1 | the pulldown keeps the flash OFF while the Pi boots |
| 16 | 2200 µF 10 V low-ESR electrolytic | 2 | $4 | local reservoir, supplies the 2 A pulse so the 5 V rail doesn't sag |
| 17 | Polyfuse (PTC), 3 A hold | 1 | $1 | protects the flash wiring if something shorts |
| 18 | Perfboard 50x70 mm, JST-XH connectors, 20 AWG silicone wire, heat-shrink | - | $12 | |
| 19 | 12 mm momentary pushbutton (shutter + filter) | 2 | $4 | |

## Controls, assembly, enclosure (both versions)

| # | Part | Qty | ~Price | Notes |
|---|------|-----|--------|-------|
| 20 | M3 heat-set inserts + M3x10, M2x6 self-tap, M2.5x16 standoffs, M3x8 | kit | $12 | see enclosure/README.md |
| 21 | 1/4-20 hex nut (tripod mount) + epoxy | 1 | $2 | |
| 22 | Panel-mount USB-C extension (charging port) | 1 | $8 | brings the X1202's USB-C input out to the case wall |
| 23 | Enclosure print, PETG (print service) | 2 shells | $30 | see enclosure/README.md for services |

**Total: about $620 for a v2 build, about $550 for v1.** The
difference is the assembled controller-board run replacing ~$30 of
perfboard parts.

## Compatibility cross-check (why these work together)

- Camera kit goes to the Pi 5 **CAM0** port (needs the included 22-pin
  cable/adapter), enabled with `dtoverlay=imx519,cam0`. One CSI port
  covers all 4 cameras.
- Display goes to the **DISP1** port with the Pi-5-specific cable. No
  conflict with the cameras.
- The X1202 powers the Pi through the GPIO 5 V pins at 5.1 V / 5 A,
  the same budget as the official 27 W adapter, so no undervoltage
  warnings. On a v2 build the feed runs through the controller's
  VBAT_IN/VBAT_OUT pass-through (a 10 mΩ shunt) so the INA219 can
  measure it.
- The X1202 mounts on the **bottom**; the Camarray HAT sits on top of
  the 40-pin header on a tall stacking header, so header pins 1-12
  stay reachable. On v2 the controller's 2x6 socket seats there (5 V,
  I2C, UART, sync to GPIO 17, ATTN to GPIO 18). On v1 those pins stay
  free for the shutter (17), flash gate (18), and mode (27) lines.
- One shared Pi I2C bus, three different addresses, no conflicts:
  Camarray HAT control, X1202 fuel gauge (0x36), controller (0x17, v2
  only).
- The flash draws from the X1202's 5 V rail in both versions.
  Worst-case system peak (Pi ~2.4 A + display 0.3 A + cameras ~0.4 A +
  flash 2 A, about 5.1 A total) is covered for the short pulse: by the 4400 µF
  perfboard reservoir on v1, and by the controller's onboard reservoir
  plus its commanded current limit on v2. Math in power-budget.md.
