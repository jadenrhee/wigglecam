# WiggleCam

A four-lens camera where all four lenses fire at the same moment. The
four views are combined into a looping GIF that reads as 3-D, the same
effect as the Nishika N8000 film camera. A touchscreen handles the
preview and filter selection, and every shot ends with a QR code that
opens the GIF on any phone over the camera's own hotspot.

Design and firmware are done. Parts aren't ordered yet, so the images
here are renders.

<p align="center">
  <img src="docs/images/enclosure_front.png" width="49%" alt="Enclosure, front: four bezeled lenses, grip, top-plate shutter and filter buttons">
  <img src="docs/images/enclosure_back.png" width="49%" alt="Enclosure, back: 4.3 inch touchscreen">
</p>

## How it works

Four 16 MP camera modules sit 40 mm apart behind the front plate. An
Arducam Camarray HAT drives all four from one clock and merges them into
a single 2x2 frame over one CSI cable. Sharing a frame puts each view at
roughly 4 MP, which is the tradeoff for hardware sync.

That shared clock is the reason for the HAT. Cameras triggered in
software drift by milliseconds, so a moving subject lands in a different
position in each frame and jumps between them instead of shifting
smoothly.

The firmware splits the frame and aligns the four views on the subject
using phase correlation on a center crop. It then applies the selected
filter and writes a bounce-looped GIF.

![System wiring diagram](docs/images/system_diagram.svg)

## Controller board

Linux is not a real-time OS, so the Pi can't be relied on to hit an
exact moment, and the jitter shows up as a flash firing outside the
exposure.
[wigglecam-controller](https://github.com/jadenrhee/wigglecam-controller)
handles the timing-critical work.

An RP2040 drives the flash at constant current and pulses the Pi the
instant the LEDs reach full current. It also debounces the shutter,
decodes the EC11 encoder, and monitors battery voltage and current
through an INA219. The Pi drives it over I2C at 0x17. The capture pulse
and an event flag come back on separate GPIO lines.

76 x 50 mm, 4 layers, DRC clean against JLCPCB's published 4-layer
rules, plus 24 checks measured off the finished layout. Not fabricated
yet either.

<p align="center">
  <img src="docs/images/controller_board.png" width="49%" alt="Controller board, rendered top view">
  <img src="docs/images/pcb_layout.svg" width="49%" alt="PCB routing: front copper red, back copper blue">
</p>

## Repo layout

| Path | Contents |
|------|----------|
| [hardware/BOM.md](hardware/BOM.md) | full parts list, about $550 |
| [hardware/wiring.md](hardware/wiring.md) | connections, GPIO map, assembly order |
| [hardware/power-budget.md](hardware/power-budget.md) | load table and the math behind the 4.5 hour runtime |
| [hardware/safety-checklist.md](hardware/safety-checklist.md) | lithium and thermal rules. The cells are unprotected by design, so the BMS and these checks carry the safety case |
| [firmware/](firmware/) | Python app: capture, filters, alignment, GIF export, share server, UI |
| [enclosure/](enclosure/) | parametric OpenSCAD body and printing guide |
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
