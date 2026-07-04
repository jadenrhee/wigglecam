"""Capture path: one stitched frame in, four synchronized views out.

The Camarray HAT clocks all four sensors from a single source, so the
four sub-images inside one stitched frame were exposed simultaneously;
no software sync is needed or possible to get wrong.
"""

import time

import numpy as np

from . import config

try:
    from picamera2 import Picamera2
except ImportError:  # allows the test suite to run off-Pi
    Picamera2 = None


class QuadCamera:
    def __init__(self):
        if Picamera2 is None:
            raise RuntimeError("picamera2 not available (not on a Pi?)")
        self.picam = Picamera2()
        self._configure()

    def _configure(self):
        cfg = self.picam.create_still_configuration(
            main={"size": config.STITCHED_STILL_SIZE, "format": "RGB888"},
            lores={"size": config.STITCHED_PREVIEW_SIZE, "format": "YUV420"},
            display="lores",
            buffer_count=3,
        )
        self.picam.configure(cfg)

    def start(self):
        self.picam.start()
        time.sleep(0.5)  # let AE/AWB settle

    def stop(self):
        self.picam.stop()

    def capture_stitched(self) -> np.ndarray:
        """Grab one full-resolution stitched frame (H, W*4, 3)."""
        return self.picam.capture_array("main")

    @staticmethod
    def split(stitched: np.ndarray) -> list[np.ndarray]:
        """Cut the 2x2 stitched frame into the four views [TL, TR, BL,
        BR], then reorder left-to-right per config.CAM_ORDER."""
        rows, cols = config.GRID
        h, w = stitched.shape[:2]
        vh, vw = h // rows, w // cols
        views = [stitched[r * vh:(r + 1) * vh, c * vw:(c + 1) * vw].copy()
                 for r in range(rows) for c in range(cols)]
        return [views[i] for i in config.CAM_ORDER]

    def capture_views(self) -> list[np.ndarray]:
        return self.split(self.capture_stitched())
