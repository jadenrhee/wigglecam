"""Capture path: one stitched frame in, four synchronized views out.

The Camarray HAT clocks all four sensors from a single source, so the
four sub-images inside one stitched frame were exposed simultaneously.
No software sync is needed or possible to get wrong.
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
        # Picamera2 naming quirk: format names follow little-endian DRM
        # conventions, so "BGR888" is R,G,B byte order in memory (and
        # "RGB888" would hand us B,G,R). Everything downstream (filters,
        # PIL export) treats channel 0 as red, so ask for "BGR888".
        cfg = self.picam.create_still_configuration(
            main={"size": config.STITCHED_STILL_SIZE, "format": "BGR888"},
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
        """Grab one full-resolution stitched frame: a 2x2 grid of views,
        shape (H, W, 3) = (3496, 4656, 3).

        The camera free-runs for the preview, so the pipeline always
        holds frames that were exposed *before* this call. flush=True
        discards those and returns the first frame whose exposure
        started after now -- which is what lets flash.fire_around()
        guarantee the flash is already lit when the frame exposes."""
        req = self.picam.capture_request(flush=True)
        try:
            return req.make_array("main")
        finally:
            req.release()

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
