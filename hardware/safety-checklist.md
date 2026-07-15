# Safety checklist

This design deliberately avoids the two genuinely dangerous options for a
DIY camera: **no xenon flash** (needs a ~300 V charge circuit, a real
shock/burn hazard on perfboard) and **no raw/unmanaged LiPo packs** (the
X1202's BMS handles over-current, over-voltage, over-discharge, and
reverse-cell protection in hardware). What remains is low-voltage
(≤5.1 V) work, but lithium cells still demand respect.

## Batteries (the one serious hazard left in this build)

- 18650s are sourced only from a reputable specialist dealer; counterfeit
  cells are the #1 fire risk in DIY builds.
- The cells are **flat-top, unprotected, ≥8 A** types (Samsung 35E /
  Molicel M35A class). The X1202 bay is 65.3 mm, so protected cells don't
  fit, and the board's BMS provides the protection instead.
- Polarity is verified against the bay markings before every insertion.
- All four cells are matched: same brand, model, and age, and within
  0.05 V of each other before first use (measured with a multimeter).
- Charging is never left unattended and always runs on a non-flammable
  surface.
- Cells with dents, torn wrap, or heat discoloration are retired at a
  battery recycling point, never household trash.
- Cells come out before any soldering near the device.

## Electrical

- The flash board is bench-tested standalone (current per branch ≈ 1 A,
  LEDs off with the gate floating) before it connects to the Pi.
- Pi, X1202, and flash board share a common ground, confirmed with a
  continuity check before power-up.
- No conductors are left exposed after assembly; every splice is
  heat-shrunk.
- A polyfuse sits in the flash 5 V feed to protect the wiring on a short.
- Buttons switch to GND only; 5 V is never wired to a GPIO (Pi GPIOs are
  3.3 V-only and not 5 V tolerant).
- The first battery boot is outside the enclosure with a meter on the 5 V
  rail; `vcgencmd get_throttled` must read `0x0`.

## Thermal

- An active cooler is fitted to the Pi 5, and the case vent slots stay clear.
- After 15 min of live preview in the closed case, `vcgencmd measure_temp`
  stays under 75 °C; if not, the vents get enlarged.
- LED flash duty is firmware-capped at 150 ms per shot, so the LED stars
  need no heatsink at that duty cycle.

## Mechanical

- Camera and display ribbons are folded gently (folded, never creased),
  with no tension when the shells close.
- Flash and button wiring have strain relief (a zip-tie anchor).
- Nothing conductive can shift and bridge the X1202 terminals; the flash
  perfboard underside is insulated with polyimide tape.
