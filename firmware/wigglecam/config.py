"""Central configuration for the WiggleCam firmware."""

from pathlib import Path

# ---------------------------------------------------------------- capture ---
# The Arducam IMX519 quad Camarray HAT presents all four sensors as ONE
# camera. In quad-channel (synchronized) mode the frame is a 2x2 grid:
#   [cam TL | cam TR]
#   [cam BL | cam BR]
# Max stitched still output is 4656x3496 (each view 2328x1748).
NUM_CAMS = 4
GRID = (2, 2)                      # rows, cols of the stitched frame
STITCHED_STILL_SIZE = (4656, 3496)
# Lower-res stitched stream used for the live preview (keeps UI fluid).
STITCHED_PREVIEW_SIZE = (1280, 960)

# Reorder table applied after the 2x2 split: entry p is the stitched-frame
# quadrant index (0 TL, 1 TR, 2 BL, 3 BR) of the camera at physical
# left-to-right position p. camera.split() emits
# [views[CAM_ORDER[0]], ..., views[CAM_ORDER[3]]]. A ribbon-routing swap
# between two cameras is remapped here instead of re-cabling.
CAM_ORDER = [0, 1, 2, 3]

# ------------------------------------------------------------------- GPIO ---
PIN_SHUTTER = 17          # momentary button to GND, internal pull-up
PIN_FLASH = 18            # gate of the flash MOSFET (active high)
PIN_MODE = 27             # optional second button: cycle filters

FLASH_PULSE_S = 0.120     # nominal manual pulse length (Flash.pulse);
                          # captures use Flash.fire_around instead
FLASH_MAX_PULSE_S = 0.150 # hard safety cap enforced in flash.py

# ---------------------------------------------------------------- wiggle ----
GIF_FPS = 12.5            # playback speed of the bounce loop. GIF frame
                          # delays quantize to 10 ms steps, so use a rate
                          # whose period is a whole centisecond (80 ms
                          # here); asking for 12 fps would store 80 ms too
BOUNCE = True             # 1-2-3-4-3-2 loop instead of 1-2-3-4
ALIGN = True              # auto-align frames on the subject before export

# ---------------------------------------------------------------- storage ---
CAPTURE_DIR = Path.home() / "wigglecam_captures"
CAPTURE_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------- sharing ---
SHARE_PORT = 8080
# NetworkManager AP-mode default address. share.py derives the actual
# local IP at runtime and only falls back to this.
HOTSPOT_IP = "10.42.0.1"
