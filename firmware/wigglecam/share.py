"""Phone sharing without AirDrop.

AirDrop is Apple-proprietary (AWDL) and cannot be spoken by a Pi, so we
do the next-best thing that works on every phone: the camera runs a
Wi-Fi hotspot and a tiny web gallery; the touchscreen shows a QR code
that opens the latest wigglegram directly on the phone.

Enable the hotspot once with NetworkManager (see docs/wiring.md):
  nmcli device wifi hotspot ssid WiggleCam password <yourpass>
"""

import io
import threading

import qrcode
from flask import Flask, abort, send_file, render_template_string

from . import config

_PAGE = """<!doctype html><meta name=viewport content="width=device-width">
<title>WiggleCam</title>
<body style="font-family:sans-serif;background:#111;color:#eee;text-align:center">
<h2>WiggleCam shots</h2>
{% for name in shots %}
  <p><a style="color:#8cf" href="/shot/{{name}}" download>{{name}}</a></p>
  <img src="/shot/{{name}}" style="max-width:95vw;border-radius:8px">
{% endfor %}
</body>"""


class ShareServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.add_url_rule("/", view_func=self._index)
        self.app.add_url_rule("/shot/<name>", view_func=self._shot)
        self._thread = None

    # ------------------------------------------------------------ routes --
    def _gifs(self):
        return sorted(config.CAPTURE_DIR.glob("*/wiggle_*.gif"),
                      key=lambda p: p.stat().st_mtime, reverse=True)

    def _index(self):
        return render_template_string(_PAGE,
                                      shots=[p.name for p in self._gifs()[:10]])

    def _shot(self, name):
        for p in self._gifs():
            if p.name == name:                # whitelist lookup, no path
                return send_file(p)           # traversal possible
        abort(404)

    # ------------------------------------------------------------ control --
    def start(self):
        self._thread = threading.Thread(
            target=lambda: self.app.run(host="0.0.0.0",
                                        port=config.SHARE_PORT,
                                        debug=False, use_reloader=False),
            daemon=True)
        self._thread.start()

    def url(self, latest: str | None = None) -> str:
        base = f"http://{config.HOTSPOT_IP}:{config.SHARE_PORT}/"
        return base + (f"shot/{latest}" if latest else "")

    def qr_image(self, latest: str | None = None):
        """PIL image of the QR code, ready to blit onto the UI."""
        qr = qrcode.QRCode(box_size=6, border=2)
        qr.add_data(self.url(latest))
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white")
