# WiggleCam

A handheld camera with four synchronized lenses. They fire at the same
instant, and the four views become a bouncing 3-D "wigglegram" GIF — a
digital version of the Nishika N8000. Touchscreen for preview and filters,
and a QR code after each shot that opens the GIF on any phone over the
camera's own hotspot.

<p align="center">
  <img src="docs/images/enclosure_front.png" width="49%" alt="Enclosure, front: four bezeled lenses, grip, top-plate shutter and filter buttons">
  <img src="docs/images/enclosure_back.png" width="49%" alt="Enclosure, back: 4.3 inch touchscreen">
</p>

## How it works

Four 16 MP modules sit 40 mm apart behind the faceplate. An Arducam Camarray
HAT clocks all four sensors off one clock and merges them into a single
2×2 frame over one CSI cable, so the exposures land together and moving
subjects don't ghost. Firmware splits the frame, aligns the views by phase
correlation, applies a filter, and writes a bounce-looped GIF.

![System wiring diagram](docs/images/system_diagram.svg)

## Controller board

[wigglecam-controller](https://github.com/jadenrhee/wigglecam-controller) is
the RP2040 co-processor board: flash driving, shutter debounce, encoder
decoding, battery telemetry, and camera sync, over I2C/UART to the Pi.
76 × 50 mm, 4-layer, DRC-clean.

<p align="center">
  <img src="docs/images/controller_board.png" width="49%" alt="Controller board, rendered top view">
  <img src="docs/images/pcb_layout.svg" width="49%" alt="PCB routing: front copper red, back copper blue">
</p>

## Repo layout

| Path | Contents |
|------|----------|
| [hardware/BOM.md](hardware/BOM.md) | bill of materials (~$550) |
| [hardware/wiring.md](hardware/wiring.md) | block diagram, GPIO map, assembly order |
| [hardware/power-budget.md](hardware/power-budget.md) | load table, flash transients, 4.4 h runtime |
| [hardware/safety-checklist.md](hardware/safety-checklist.md) | battery, electrical, thermal |
| [firmware/](firmware/) | Python app: capture, filters, alignment, GIF, share server, UI |
| [enclosure/](enclosure/) | parametric OpenSCAD body + printing guide |
| [docs/architecture.md](docs/architecture.md) | reasoning behind each design decision |

## Running it (on the Pi)

```bash
sudo apt install -y python3-picamera2 python3-pyqt5 python3-opencv
python3 -m venv --system-site-packages .venv && source .venv/bin/activate
pip install -r firmware/requirements.txt
echo 'dtoverlay=imx519,cam0' | sudo tee -a /boot/firmware/config.txt && sudo reboot
# after reboot:
nmcli device wifi hotspot ssid WiggleCam password <choose-one>
cd firmware && python3 -m wigglecam.app
```
