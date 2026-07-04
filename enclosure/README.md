# Enclosure

The body is parametric OpenSCAD, all in
[wigglecam_body.scad](wigglecam_body.scad). It's styled like a wide
compact camera: raised top and bottom plates, bezeled lens rings, a
hand grip on the photographer's right, a shutter button on the top
plate, a flash window, and a raised screen bezel on the back.

Open it in [OpenSCAD](https://openscad.org) (free) and press F5. The
default `PART = "assembly"` shows the closed camera standing upright
with dummy lenses, screen, and buttons so you can sanity-check the
layout. To print, set `PART` to `"front"` or `"back"`, press F6 to
render, then File → Export → STL.

**Before printing anything:** measure your actual delivered screen,
camera modules, and Pi/UPS stack with calipers and update the
`scr_*`, `cam_*`, and `pi_*` variables. Vendor drawings drift between
hardware revisions, and a 1 mm error in the screen cutout ruins a
10-hour print.

## Printing without owning a printer

- **Public library / school makerspace.** Many do free or at-cost
  prints. The body fits most 220x220 mm beds diagonally; if yours is
  smaller, reduce `body_w` or use a service with a bigger bed.
- **[Craftcloud](https://craftcloud3d.com)**: a comparison marketplace
  for print services. Upload the STL, pick PETG.
- **[JLC3DP](https://jlc3dp.com)** / **PCBWay**: cheap, good quality,
  about a week of shipping.

Settings that work: **PETG** (handles heat better than PLA, and the
Pi 5 runs warm), 0.2 mm layers, 4 perimeters, 25% infill.

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
