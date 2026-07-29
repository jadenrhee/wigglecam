# Power budget

Supply: Geekworm X1202, 5.1 V, 5 A max continuous (25.5 W).

## Load table

| Load | Typical | Worst case | Duration |
|------|---------|-----------|----------|
| Pi 5 (4 cores busy, Wi-Fi AP on) | 1.2 A | 2.4 A | continuous |
| Active cooler | 0.1 A | 0.15 A | continuous |
| Camarray HAT + 4x IMX519 | 0.3 A | 0.4 A | continuous |
| 4.3" DSI display | 0.25 A | 0.3 A | continuous |
| Flash (2x XP-G3 @ 1 A) | 0 | 2.0 A | 150 ms max pulse |
| **Total continuous** | **1.85 A (9.4 W)** | **3.25 A (16.6 W)** | |
| **Total during flash pulse** | | **5.25 A** | 150 ms max |

## The flash transient

Worst-case draw during the pulse exceeds the X1202's 5 A continuous
rating by ~0.25 A for ≤150 ms. The flash branch has **2× 2200 µF** of
local reservoir capacitance, but honest math says the caps cannot
bridge that excess: it amounts to 0.25 A × 0.15 s = 37.5 mC, while
4400 µF supplies only 4.4 mC per volt of allowed sag — about 12% of
what's needed, or ~18 ms of the 150 ms pulse. Bridging the full pulse
at 1 V of sag would take ~37,500 µF. So the reservoir's real job is
smaller: it feeds the LED turn-on edge and keeps the
pulse's fast di/dt off the wiring. For the body of a worst-case pulse
the X1202 itself runs ~5% over its "max continuous" rating for under
150 ms — a brief overload I'm leaning on supply headroom for, with a
momentary rail droop possible, not something the caps absorb. Two
things bound the risk:

1. Firmware hard-caps the pulse at 150 ms (`flash.py`, enforced with a
   watchdog even if the capture call hangs), and the worst case is
   synthetic: the Pi's measured draw during a capture is ~1.5 A, not
   2.4 A, which puts the realistic pulse total near 4.35 A — inside
   the rating with margin.
2. If `vcgencmd get_throttled` ever reads ≠ 0x0 after flash shots,
   dropping the branch resistors to 2.7 Ω (≈0.8 A/LED) resolves it, still
   plenty of light at wigglegram distances.

## Runtime estimate

4x Samsung 35E: 4 x 3500 mAh x 3.6 V = about **50 Wh**.
At the 9.4 W typical draw and ~85% boost-converter efficiency:

50 Wh x 0.85 / 9.4 W = about **4.5 hours** of continuous shooting per
charge.

## Charging

Charging is only through the X1202's USB-C input (5 V/5 A) or its DC jack
(6-18 V), which feed the onboard charger/BMS. The cells are never charged
outside the device except with a dedicated 18650 charger.
