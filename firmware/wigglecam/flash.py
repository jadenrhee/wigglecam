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
        """Turn the flash on, run the capture callable, turn it off.
        A watchdog timer forces the flash off at FLASH_MAX_PULSE_S even
        if capture_fn hangs."""
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
