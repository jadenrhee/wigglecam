"""Image filters applied uniformly to all four views before export.

Each filter is a function (np.ndarray RGB) -> (np.ndarray RGB). Keeping
them pure functions makes them trivial to preview on the lores stream
and to unit-test off the camera.
"""

import numpy as np
import cv2

def none(img):
    return img

def bw(img):
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return cv2.cvtColor(g, cv2.COLOR_GRAY2RGB)

def sepia(img):
    m = np.array([[0.393, 0.769, 0.189],
                  [0.349, 0.686, 0.168],
                  [0.272, 0.534, 0.131]], dtype=np.float32)
    out = img.astype(np.float32) @ m.T
    return np.clip(out, 0, 255).astype(np.uint8)

def vivid(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.35, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

def film(img):
    """Faded-film look: lifted blacks, warm cast, slight vignette."""
    out = img.astype(np.float32)
    out = out * 0.9 + 20.0                      # lift blacks
    out[..., 0] = np.clip(out[..., 0] * 1.06, 0, 255)   # warm reds
    out[..., 2] = np.clip(out[..., 2] * 0.94, 0, 255)   # cool blues
    h, w = img.shape[:2]
    y, x = np.ogrid[:h, :w]
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    vignette = np.clip(1.0 - 0.25 * d ** 2, 0, 1)[..., None]
    return np.clip(out * vignette, 0, 255).astype(np.uint8)

FILTERS = {
    "None": none,
    "B&W": bw,
    "Sepia": sepia,
    "Vivid": vivid,
    "Film": film,
}
FILTER_NAMES = list(FILTERS)
