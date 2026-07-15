# Enclosure

The body is parametric OpenSCAD, all in
[wigglecam_body.scad](wigglecam_body.scad). It's styled like a wide
compact camera: raised top and bottom plates, bezeled lens rings, a
hand grip on the photographer's right, a shutter button on the top
plate, a flash window, and a raised screen bezel on the back.

Opened in [OpenSCAD](https://openscad.org) (free), pressing F5 renders the
default `PART = "assembly"`: the closed camera standing upright, with dummy
lenses/screen/button for a quick layout sanity-check. Setting `PART` to
`"front"` or `"back"` and pressing F6 renders a shell for export via
**File → Export → STL**.

The `scr_*`, `cam_*`, and `pi_*` variables hold the dimensions of the
actual delivered screen, camera modules, and Pi/UPS stack, measured with
calipers before any print. Vendor drawings drift between hardware
revisions, and a 1 mm error in the screen cutout ruins a 10-hour print.

## Printing without owning a printer

- **Public library or school makerspace.** Many offer free or at-cost
  prints. This body fits most 220×220 mm beds diagonally, or `body_w` can
  be reduced to print at a service with a larger bed.
- **[Craftcloud](https://craftcloud3d.com)** is a comparison marketplace
  for print services; upload the STL and pick PETG.
- **[JLC3DP](https://jlc3dp.com)** and **PCBWay** are cheap, good quality,
  and ship in about a week.

Recommended settings: **PETG** (more heat-tolerant than PLA, and the Pi 5
runs warm), 0.2 mm layers, 4 perimeters, 25 % infill.

**Orientation:** print both shells open-side down (cosmetic face up)
with supports on. The raised lens bezels, grip, and plates mean the
shells don't sit flat face-down anymore, and this way the support
marks end up inside the shell where nobody sees them.

## Assembly hardware

- 6x M3 heat-set brass inserts + M3x10 screws (join the shells)
- 16x M2x6 self-tapping screws (camera modules)
- 4x M2.5x16 standoff screws (Pi 5 + X1202 stack)
- 4x M3x8 screws (screen)
- 1x 1/4-20 hex nut, epoxied into the bottom pocket (tripod mount)
- a scrap of white PETG or frosted acrylic behind the flash window as
  a diffuser
