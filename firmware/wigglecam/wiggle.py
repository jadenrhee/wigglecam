"""Turn four simultaneous views into a wigglegram.

The four lenses sit a few centimetres apart, so the views are shifted
relative to each other. For the 3-D "wiggle" to read well, the frames
must be aligned on the *subject*: the subject then stays put while the
background parallax-shifts around it. align_views() does this with
phase correlation on a centre crop (where the subject usually is).
"""

from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from . import config


def _center_crop(img: np.ndarray, frac: float = 0.5) -> np.ndarray:
    h, w = img.shape[:2]
    ch, cw = int(h * frac), int(w * frac)
    y0, x0 = (h - ch) // 2, (w - cw) // 2
    return img[y0:y0 + ch, x0:x0 + cw]


def align_views(views: list[np.ndarray]) -> list[np.ndarray]:
    """Shift every view so the centre subject overlaps the reference
    view (index 1, second from left — near the middle of the rig)."""
    ref_idx = 1
    ref = cv2.cvtColor(_center_crop(views[ref_idx]), cv2.COLOR_RGB2GRAY)
    ref = np.float32(ref)
    out = []
    for i, v in enumerate(views):
        if i == ref_idx:
            out.append(v)
            continue
        g = np.float32(cv2.cvtColor(_center_crop(v), cv2.COLOR_RGB2GRAY))
        (dx, dy), _ = cv2.phaseCorrelate(ref, g)
        m = np.float32([[1, 0, -dx], [0, 1, -dy]])
        shifted = cv2.warpAffine(v, m, (v.shape[1], v.shape[0]),
                                 borderMode=cv2.BORDER_REPLICATE)
        out.append(shifted)
    return _common_crop(out)


def _common_crop(views: list[np.ndarray], margin: int = 32) -> list[np.ndarray]:
    """Trim edges so replicated borders from the shifts never show."""
    h, w = views[0].shape[:2]
    return [v[margin:h - margin, margin:w - margin] for v in views]


def bounce_sequence(views: list[np.ndarray]) -> list[np.ndarray]:
    """1-2-3-4-3-2 so the loop swings instead of snapping back."""
    if config.BOUNCE and len(views) > 2:
        return views + views[-2:0:-1]
    return views


def save_wigglegram(views: list[np.ndarray],
                    out_dir: Path = config.CAPTURE_DIR) -> Path:
    """Write an animated GIF (plus the four stills) and return its path."""
    if config.ALIGN:
        views = align_views(views)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shot_dir = out_dir / stamp
    shot_dir.mkdir(parents=True, exist_ok=True)

    frames = []
    for i, v in enumerate(views):
        im = Image.fromarray(v)
        im.save(shot_dir / f"view{i}.jpg", quality=92)
        # GIFs get heavy fast; 720px wide is plenty for phone screens.
        im.thumbnail((720, 720))
        frames.append(im)

    seq = bounce_sequence(frames)
    gif_path = shot_dir / f"wiggle_{stamp}.gif"
    seq[0].save(gif_path, save_all=True, append_images=seq[1:],
                duration=int(1000 / config.GIF_FPS), loop=0)
    return gif_path
