# Enclosure

Parametric OpenSCAD body in [wigglecam_body.scad](wigglecam_body.scad).
Open it in [OpenSCAD](https://openscad.org) (free), set `PART` to
`"front"` or `"back"`, press F6 to render, then **File → Export → STL**.

**Before printing anything:** measure your actual delivered screen,
camera modules, and Pi/UPS stack with calipers and update the
`scr_*`, `cam_*`, and `pi_*` variables. Vendor drawings drift between
hardware revisions; a 1 mm error in the screen cutout ruins a 10-hour print.

## Printing without owning a printer

- **Public library / school makerspace** — many offer free or at-cost
  prints; this body fits most 220×220 mm beds diagonally, or reduce
  `body_w` / print at a service with a larger bed.
- **[Craftcloud](https://craftcloud3d.com)** — comparison marketplace for
  print services; upload the STL, pick PETG.
- **[JLC3DP](https://jlc3dp.com)** / **PCBWay** — cheap, good quality,
  ~1 week shipping.

Recommended settings: **PETG** (more heat-tolerant than PLA — the Pi 5
runs warm), 0.2 mm layers, 4 perimeters, 25 % infill.

## Hardware for assembly

- 6× M3 heat-set brass inserts + M3×10 screws (join the shells)
- 16× M2×6 self-tapping screws (camera modules)
- 4× M2.5×16 standoff screws (Pi 5 + X1202 stack)
- 4× M3×8 screws (screen)
- 1× 1/4-20 hex nut, epoxied into the bottom pocket (tripod mount)
- White PETG or frosted acrylic scrap behind the flash window as a diffuser
