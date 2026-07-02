# Safety checklist

This design deliberately avoids the two genuinely dangerous options for a
DIY camera: **no xenon flash** (needs a ~300 V charge circuit — a real
shock/burn hazard on perfboard) and **no raw/unmanaged LiPo packs** (the
X1202's BMS handles over-current, over-voltage, over-discharge, and
reverse-cell protection in hardware). What remains is low-voltage
(≤5.1 V) work, but lithium cells still demand respect.

## Batteries (the only serious hazard in this build)

- [ ] Buy 18650s only from a reputable specialist dealer. Counterfeit
      cells are the #1 fire risk in DIY builds.
- [ ] Use **flat-top, unprotected, ≥8 A** cells (Samsung 35E / Molicel
      M35A class). The X1202 bay is 65.3 mm — protected cells don't fit,
      and the board's BMS provides the protection instead.
- [ ] Check polarity against the bay markings **before every insertion**.
- [ ] All four cells: same brand, model, age, and within 0.05 V of each
      other before first use (measure with a multimeter).
- [ ] Never leave charging unattended; charge on a non-flammable surface.
- [ ] No dents, torn wrap, or heat discoloration — retire damaged cells
      at a battery recycling point (never household trash).
- [ ] Remove cells before soldering anywhere near the device.

## Electrical

- [ ] Flash board: bench-test standalone (current per branch ≈ 1 A,
      LEDs off with gate floating) **before** connecting to the Pi.
- [ ] Common ground between Pi, X1202, and flash board — verified with a
      continuity check before power-up.
- [ ] No exposed conductors after assembly; heat-shrink every splice.
- [ ] Polyfuse in the flash 5 V feed (protects wiring on a short).
- [ ] Buttons switch to GND only — never wire 5 V to a GPIO (Pi GPIOs are
      3.3 V-only and not 5 V tolerant).
- [ ] First battery boot outside the enclosure with a meter on the 5 V
      rail; `vcgencmd get_throttled` must read `0x0`.

## Thermal

- [ ] Active cooler installed on the Pi 5; vent slots in the case clear.
- [ ] After 15 min of live preview in the closed case:
      `vcgencmd measure_temp` < 75 °C. If not, enlarge vents.
- [ ] LED flash duty is firmware-capped at 150 ms per shot — the LED
      stars need no heatsink at that duty cycle.

## Mechanical

- [ ] Camera/display ribbons folded gently (fold, never crease), no
      tension when the shells close.
- [ ] Strain relief (zip-tie anchor) on flash and button wiring.
- [ ] Nothing conductive can shift and bridge the X1202 terminals —
      insulate the flash perfboard underside with polyimide tape.
