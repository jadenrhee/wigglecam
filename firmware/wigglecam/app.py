"""WiggleCam main application.

Touch UI on the 4.3" DSI screen: live preview from the leftmost camera
(cropped out of the stitched lores stream), filter carousel, shutter,
and a QR overlay after each shot for instant phone download.

Run on the Pi:  python3 -m wigglecam.app
"""

import sys
import threading

from PyQt5 import QtCore, QtWidgets
from gpiozero import Button

from . import config
from .camera import QuadCamera
from .filters import FILTERS, FILTER_NAMES
from .flash import Flash
from .share import ShareServer
from .wiggle import save_wigglegram

try:
    from picamera2.previews.qt import QGlPicamera2
except ImportError:
    QGlPicamera2 = None


class WiggleCamWindow(QtWidgets.QMainWindow):
    shot_saved = QtCore.pyqtSignal(str)   # gif filename, emitted off-thread

    def __init__(self):
        super().__init__()
        self.setWindowTitle("WiggleCam")

        self.cam = QuadCamera()
        self.flash = Flash()
        self.share = ShareServer()
        self.share.start()

        self.filter_idx = 0
        self._busy = threading.Lock()

        self._build_ui()
        self.cam.start()

        # Physical controls mirror the on-screen ones.
        self.shutter_btn = Button(config.PIN_SHUTTER, pull_up=True,
                                  bounce_time=0.05)
        self.shutter_btn.when_pressed = self.trigger_capture
        self.mode_btn = Button(config.PIN_MODE, pull_up=True,
                               bounce_time=0.05)
        self.mode_btn.when_pressed = self.next_filter

        self.shot_saved.connect(self._show_qr)

    # ----------------------------------------------------------------- UI --
    def _build_ui(self):
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)

        if QGlPicamera2 is not None:
            self.preview = QGlPicamera2(self.cam.picam, keep_ar=True)
        else:
            self.preview = QtWidgets.QLabel("preview unavailable")
        layout.addWidget(self.preview, stretch=1)

        bar = QtWidgets.QHBoxLayout()
        self.filter_label = QtWidgets.QPushButton(FILTER_NAMES[0])
        self.filter_label.setMinimumHeight(56)
        self.filter_label.clicked.connect(self.next_filter)
        bar.addWidget(self.filter_label)

        shoot = QtWidgets.QPushButton("●")
        shoot.setMinimumHeight(56)
        shoot.setStyleSheet("font-size:28px;color:red")
        shoot.clicked.connect(self.trigger_capture)
        bar.addWidget(shoot, stretch=1)
        layout.addLayout(bar)

        self.setCentralWidget(central)

    def next_filter(self):
        self.filter_idx = (self.filter_idx + 1) % len(FILTER_NAMES)
        self.filter_label.setText(FILTER_NAMES[self.filter_idx])

    # ------------------------------------------------------------ capture --
    def trigger_capture(self):
        if not self._busy.acquire(blocking=False):
            return  # capture already in flight
        threading.Thread(target=self._capture_worker, daemon=True).start()

    def _capture_worker(self):
        try:
            stitched = self.flash.fire_around(self.cam.capture_stitched)
            views = self.cam.split(stitched)
            f = FILTERS[FILTER_NAMES[self.filter_idx]]
            views = [f(v) for v in views]
            gif_path = save_wigglegram(views)
            self.shot_saved.emit(gif_path.name)
        finally:
            self._busy.release()

    def _show_qr(self, gif_name: str):
        qr = self.share.qr_image(gif_name)
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Scan to download")
        lay = QtWidgets.QVBoxLayout(dlg)
        label = QtWidgets.QLabel()
        qr.save("/dev/shm/wiggle_qr.png")   # tmpfs, no SD-card wear
        label.setPixmap(_load("/dev/shm/wiggle_qr.png"))
        label.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(label)
        lay.addWidget(QtWidgets.QLabel(self.share.url(gif_name)))
        QtCore.QTimer.singleShot(15000, dlg.accept)  # auto-dismiss
        dlg.exec_()

    def closeEvent(self, event):
        self.cam.stop()
        self.flash.close()
        event.accept()


def _load(path):
    from PyQt5.QtGui import QPixmap
    return QPixmap(path)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = WiggleCamWindow()
    win.showFullScreen()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
