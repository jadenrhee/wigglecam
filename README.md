# WiggleCam — a 4-lens digital wigglegram camera

A handheld camera with **four hardware-synchronized lenses** that fire
at the same instant (with LED flash), then splices the four views into
a bouncing 3-D "wigglegram" GIF — a digital take on the Nishika N8000.
A touchscreen shows a live preview, filter carousel, and after every
shot a QR code that opens the GIF straight on anyone's phone over the
camera's own Wi-Fi hotspot.

> Status: design + firmware complete, hardware build in progress.

## How it works

Four 16 MP camera modules sit 40 mm apart behind the faceplate. An
Arducam Camarray HAT clocks all four sensors together and merges them
into a single 2×2-stitched frame over one CSI cable — so all four
exposures are simultaneous *by construction*, which is what keeps
moving subjects from ghosting. Firmware splits the frame, auto-aligns
the views on the subject (phase correlation), applies the selected
filter, and writes a bounce-looped GIF. Full reasoning for every
design decision: [docs/architecture.md](docs/architecture.md).

## Repo layout

| Path | Contents |
|------|----------|
| [hardware/BOM.md](hardware/BOM.md) | full bill of materials (~$550) with compatibility cross-check |
| [hardware/wiring.md](hardware/wiring.md) | block diagram, GPIO map, flash driver schematic, assembly order |
| [hardware/power-budget.md](hardware/power-budget.md) | load table, flash-transient math, 4.4 h runtime estimate |
| [hardware/safety-checklist.md](hardware/safety-checklist.md) | battery, electrical, thermal checks — read first |
| [firmware/](firmware/) | Python app: capture, filters, alignment, GIF export, share server, touch UI |
| [enclosure/](enclosure/) | parametric OpenSCAD body + printing guide (no printer needed) |

## Key design choices

- **LED flash, not xenon** — no 300 V charge circuit in a handheld
  perfboard build; an LED pulse also makes flash/exposure sync trivial.
- **One battery system rated for the job** — Pi 5 needs 5 V/5 A;
  a purpose-built 4×18650 UPS HAT with hardware BMS delivers it.
- **QR-code sharing instead of AirDrop** — AirDrop is Apple-proprietary;
  a hotspot + QR works identically on every phone with zero setup.

## Running the firmware (on the Pi)

```bash
sudo apt install -y python3-picamera2 python3-pyqt5 python3-opencv
python3 -m venv --system-site-packages .venv && source .venv/bin/activate
pip install -r firmware/requirements.txt
echo 'dtoverlay=imx519,cam0' | sudo tee -a /boot/firmware/config.txt && sudo reboot
# after reboot:
nmcli device wifi hotspot ssid WiggleCam password <choose-one>
cd firmware && python3 -m wigglecam.app
```

## Build notes

Built with the help of AI tooling (Claude) for design verification,
firmware scaffolding, and documentation; hardware assembly, testing,
and debugging done by hand.
