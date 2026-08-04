"""LED flash control.

The flash is a bank of high-power LEDs switched by a logic-level MOSFET
on PIN_FLASH. Because it is an LED (not xenon) we simply hold it on for
a window that brackets the exposure instead of timing a microsecond
trigger. A hard cap on pulse length is enforced here so a software bug
can never leave 2 A flowing through the LED bank continuously.
"""

import threading
import time

from gpiozero import DigitalOutputDevice

from . import config


class Flash:
    def __init__(self, pin: int = config.PIN_FLASH):
        self._out = DigitalOutputDevice(pin, active_high=True,
                                        initial_value=False)
        self._lock = threading.Lock()

    def pulse(self, seconds: float = config.FLASH_PULSE_S):
        seconds = min(seconds, config.FLASH_MAX_PULSE_S)
        with self._lock:
            self._out.on()
            try:
                time.sleep(seconds)
            finally:
                self._out.off()          # always turns off, even on error

    def fire_around(self, capture_fn):
        """Bracket a capture with the flash: LED on, run the capture
        callable, LED off when it returns.

        capture_fn must return a frame exposed *after* it was called
        (QuadCamera.capture_stitched does this with flush=True), so the
        frame starts exposing with the flash already lit. A watchdog
        forces the flash off at FLASH_MAX_PULSE_S even if capture_fn
        hangs; that hard cap always wins over frame coverage, so a
        pipeline slower than the cap can lose the flash toward the end
        of readout. Runs on the capture worker thread, never the Qt UI
        thread, so blocking in capture_fn is fine."""
        watchdog = threading.Timer(config.FLASH_MAX_PULSE_S, self._out.off)
        with self._lock:
            self._out.on()
            watchdog.start()
            try:
                return capture_fn()
            finally:
                self._out.off()
                watchdog.cancel()

    def close(self):
        self._out.off()
        self._out.close()
