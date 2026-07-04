# Safety checklist

Two genuinely dangerous options got designed out of this project on
purpose: there's **no xenon flash** (that would mean a ~300 V charge
circuit, a real shock and burn hazard in a DIY build) and **no raw
LiPo packs** (the X1202's BMS handles over-current, over-voltage,
over-discharge, and reversed cells in hardware). What's left is all
low-voltage (5.1 V and below) work. Lithium cells still deserve real care,
though, so:

## Batteries (the one serious hazard left in this build)

- [ ] Buy 18650s only from a reputable specialist dealer. Counterfeit
      cells are the biggest fire risk in DIY builds.
- [ ] Use **flat-top, unprotected cells rated 8 A or more** (Samsung
      35E / Molicel M35A class). The X1202 bay is 65.3 mm, so protected
      cells don't fit; the board's BMS does that job instead.
- [ ] Check polarity against the bay markings **before every insertion**.
- [ ] All four cells: same brand, model, and age, and within 0.05 V of
      each other before first use (check with a multimeter).
- [ ] Never leave charging unattended; charge on a non-flammable
      surface.
- [ ] No dents, torn wrap, or heat discoloration. Retire damaged cells
      at a battery recycling point, never the trash.
- [ ] Pull the cells before soldering anywhere near the device.

## Electrical

- [ ] Whichever flash electronics you build (v1 perfboard or the v2
      controller board), bench-test it standalone first: about 1 A per
      LED branch, and the LEDs must stay off when nothing is driving
      the control input. Only then does it get connected to the Pi.
- [ ] Common ground between the Pi, X1202, and flash electronics,
      verified with a continuity check before power-up.
- [ ] No exposed conductors after assembly; heat-shrink every splice.
- [ ] Polyfuse in the flash 5 V feed (protects the wiring on a short).
      The v2 controller has this on the board.
- [ ] Buttons switch to GND only. Never wire 5 V to a GPIO; Pi GPIOs
      are 3.3 V-only and not 5 V tolerant.
- [ ] First battery boot happens outside the enclosure with a meter on
      the 5 V rail; `vcgencmd get_throttled` must read `0x0`.

## Thermal

- [ ] Active cooler installed on the Pi 5; vent slots in the case
      clear.
- [ ] After 15 min of live preview in the closed case:
      `vcgencmd measure_temp` under 75 °C. If not, enlarge the vents.
- [ ] Flash duty is capped at 150 ms per shot, so the LED stars don't
      need heatsinks.

## Mechanical

- [ ] Camera/display ribbons folded gently (fold, never crease), no
      tension when the shells close.
- [ ] Strain relief (zip-tie anchor) on the flash and button wiring.
- [ ] Nothing conductive can shift around and bridge the X1202
      terminals. Insulate the underside of any perfboard with
      polyimide tape.
