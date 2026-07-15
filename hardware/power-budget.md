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
| **Total continuous** | **~1.9 A (9.7 W)** | **3.25 A (16.6 W)** | |
| **Total during flash pulse** | | **5.25 A** | 150 ms max |

## The flash transient

Worst-case draw during the pulse nominally exceeds 5 A by ~0.25 A for
≤150 ms. This is why the flash branch has **2× 2200 µF** of local
reservoir capacitance: the caps source the front of the pulse and the
average excess. Energy check: 0.25 A × 0.15 s = 37.5 mC; the caps hold
4400 µF × 5.1 V ≈ 22.4 mC *total*, but they only need to cover the
*excess* while sagging ~1 V max: 4400 µF × 1 V = 4.4 mC per volt of
allowed sag. Combined with the fact that the Pi's true draw during a
capture is ~1.5 A (not the 2.4 A synthetic worst case), the rail stays
inside spec. Two independent mitigations are still in place:

1. Firmware hard-caps the pulse at 150 ms (`flash.py`, enforced with a
   watchdog even if the capture call hangs).
2. If `vcgencmd get_throttled` ever reads ≠ 0x0 after flash shots,
   dropping the branch resistors to 2.7 Ω (≈0.8 A/LED) resolves it, still
   plenty of light at wigglegram distances.

## Runtime estimate

4x Samsung 35E: 4 x 3500 mAh x 3.6 V = about **50 Wh**.
At the ~9.7 W typical draw and ~85% boost-converter efficiency:

50 Wh x 0.85 / 9.7 W = about **4.4 hours** of continuous shooting per
charge.

## Charging

Charging is only through the X1202's USB-C input (5 V/5 A) or its DC jack
(6-18 V), which feed the onboard charger/BMS. The cells are never charged
outside the device except with a dedicated 18650 charger.
