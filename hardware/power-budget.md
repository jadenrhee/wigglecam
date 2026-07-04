# Power budget

Supply: Geekworm X1202. 5.1 V, 5 A max continuous (25.5 W).

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

On paper, worst-case draw during the pulse goes about 0.25 A over the
X1202's 5 A rating for up to 150 ms. That's why there's local
reservoir capacitance on the flash rail (2x 2200 µF on the v1
perfboard; polymer caps on the v2 controller): the caps source the
front edge of the pulse and the small average excess, and the rail
only has to sag a little to hand them that job. In practice it's even
more comfortable, because the Pi's real draw during a capture is
around 1.5 A, not the 2.4 A stacked worst case.

Two backstops on top of that:

1. The pulse is hard-capped at 150 ms. On v1 that's `flash.py` with a
   watchdog in case the capture call hangs; on v2 the controller board
   enforces it in its own firmware and hardware.
2. If `vcgencmd get_throttled` ever reads anything but 0x0 after flash
   shots, lower the flash current: on v2 turn `FLASH_PCT` down, on v1
   swap the branch resistors to 2.7 Ω (about 0.8 A per LED). Still plenty
   of light at wigglegram distances.

## Runtime estimate

4x Samsung 35E: 4 x 3500 mAh x 3.6 V = about **50 Wh**.
At the ~9.7 W typical draw and ~85% boost-converter efficiency:

50 Wh x 0.85 / 9.7 W = about **4.4 hours** of continuous shooting per
charge.

## Charging

Only through the X1202's USB-C input (5 V / 5 A) or its DC jack
(6-18 V); both feed the onboard charger/BMS. Don't charge the cells
outside the device unless it's in a proper dedicated 18650 charger.
