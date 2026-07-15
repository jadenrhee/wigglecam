# WiggleCam: a 4-lens digital wigglegram camera

A handheld camera with **four hardware-synchronized lenses** that fire
at the same instant (with LED flash), then splices the four views into
a bouncing 3-D "wigglegram" GIF. It's a digital take on the Nishika N8000.
A touchscreen shows a live preview, filter carousel, and after every
shot a QR code that opens the GIF straight on anyone's phone over the
camera's own Wi-Fi hotspot.

> Status: design and firmware are done. Next step is ordering parts
> and building it.

<p align="center">
  <img src="docs/images/enclosure_front.png" width="49%" alt="Enclosure, front: four bezeled lenses, grip, top-plate shutter and filter buttons">
  <img src="docs/images/enclosure_back.png" width="49%" alt="Enclosure, back: 4.3 inch touchscreen">
</p>

## How it works

Four 16 MP camera modules sit 40 mm apart behind the faceplate. An
Arducam Camarray HAT clocks all four sensors together and merges them
into a single 2×2-stitched frame over one CSI cable. Because the four
sensors share one clock, the exposures all land at the same instant,
which is what keeps moving subjects from ghosting. Firmware splits the frame, auto-aligns
the views on the subject (phase correlation), applies the selected
filter, and writes a bounce-looped GIF. Full reasoning for every
design decision: [docs/architecture.md](docs/architecture.md).

![System wiring diagram](docs/images/system_diagram.svg)

## Controller board

[wigglecam-controller](https://github.com/jadenrhee/wigglecam-controller)
is the camera's RP2040 co-processor board: it sits between the Pi 5 and
the physical hardware and handles the real-time and analog work:
constant-current LED flash driving with hardware-enforced safety
limits, shutter debounce, rotary-encoder decoding, battery telemetry,
and the camera-sync trigger, all exposed to the Pi over I2C/UART.
76 × 50 mm, 4-layer, fully routed, DRC-clean at JLCPCB limits.

<p align="center">
  <img src="docs/images/controller_board.png" width="49%" alt="Controller board, rendered top view">
  <img src="docs/images/pcb_layout.svg" width="49%" alt="PCB routing: front copper red, back copper blue">
</p>

The routing view above shows front copper in red and back copper in
blue, with the ground/power planes hidden so you can actually see the
traces.

## Repo layout

| Path | Contents |
|------|----------|
| [hardware/BOM.md](hardware/BOM.md) | full bill of materials (~$550) with compatibility cross-check |
| [hardware/wiring.md](hardware/wiring.md) | block diagram, GPIO map, flash driver schematic, assembly order |
| [hardware/power-budget.md](hardware/power-budget.md) | load table, flash-transient math, 4.4 h runtime estimate |
| [hardware/safety-checklist.md](hardware/safety-checklist.md) | battery, electrical, and thermal safety design |
| [firmware/](firmware/) | Python app: capture, filters, alignment, GIF export, share server, touch UI |
| [enclosure/](enclosure/) | parametric OpenSCAD body + printing guide (you don't need to own a printer) |

## Design choices, short version

- **LED flash, not xenon.** No 300 V charge circuit in a handheld
  perfboard build, and an LED pulse also makes flash/exposure sync trivial.
- **One battery system rated for the job.** The Pi 5 needs 5 V/5 A, and
  a 4×18650 UPS HAT with a hardware BMS delivers exactly that.
- **QR-code sharing instead of AirDrop.** AirDrop is Apple-only, but a
  hotspot plus QR code works the same way on every phone with zero setup.

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

I worked out the electronics and firmware on the bench and wrote up the
verification, wiring, and safety notes as I went, so the docs track the
decisions I actually made. Assembly, bring-up, and debugging are all
hands-on; see [hardware/](hardware/) for the wiring guide and safety
checklist.
