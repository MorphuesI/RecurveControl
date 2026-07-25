"""
hid_backend.py — the ONLY file that talks to the mouse.

Everything here is original code written against the HID protocol we
reverse-engineered from Wireshark captures of the mouse's own USB traffic.
No vendor code, binaries, or firmware is used or embedded.

Confirmed via isolated captures + live hardware tests:
  - Polling rate (Report ID 0x40, subcmd 0x05, field 0x04 / 0x08)
  - DPI preset selection (Report ID 0x40, subcmd 0x05, field 0xa6 / 0x2b)
  - Per-stage RGB color (Report ID 0x40, subcmd 0x05, field 0x57 + stage*3)
  - DPI hardware-button press event (Report ID 0x42, input report) — this
    only tells us a press happened, not the resulting stage (readback via
    Report ID 0x41 doesn't work reliably on this chip), so the app tracks
    current stage in software and advances it on each press. See NOTE below.

NOT yet confirmed / not implemented:
  - RGB effect modes (Neon/Waltz/Colorful/etc.), brightness, breathing speed
  - Button remapping / macros
"""

import threading
import hid

VID = 0x1bcf
PID = 0x08b8

POLLING_RATES = {
    125:  (0xcf, 0xa7),
    250:  (0xdf, 0xaf),
    500:  (0xef, 0xaf),
    1000: (0xff, 0xaf),
}

DPI_STAGE_COUNT = 6
STAGE_COLOR_BASE = 0x57
STAGE_COLOR_STEP = 3


class RecurveDevice:
    """Thin wrapper around the vendor HID interface (usage_page 0xff00)."""

    def __init__(self):
        self._listener_thread = None
        self._listener_stop = threading.Event()

    def _find_vendor_interface(self):
        for d in hid.enumerate(VID, PID):
            if d["usage_page"] >= 0xff00:
                return d["path"]
        return None

    def is_connected(self):
        return self._find_vendor_interface() is not None

    def _send(self, payload):
        path = self._find_vendor_interface()
        if path is None:
            raise RuntimeError("Recurve 300 not found (vendor interface missing)")
        h = hid.device()
        h.open_path(path)
        try:
            n = h.send_feature_report(bytes(payload))
            if n is not None and n < 0:
                raise RuntimeError(h.error())
        finally:
            h.close()

    def set_polling_rate(self, hz):
        if hz not in POLLING_RATES:
            raise ValueError(f"Unsupported rate {hz}. Options: {list(POLLING_RATES)}")
        val4, val8 = POLLING_RATES[hz]
        self._send([0x40, 0x05, 0x00, 0x04, val4, 0x00, 0x00, 0x01])
        self._send([0x40, 0x05, 0x00, 0x08, val8, 0x00, 0x00, 0x01])
        self._send([0x40, 0x0e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    def set_dpi_stage(self, index):
        """index is 0-based: 0 = stage 1, 1 = stage 2, ... 5 = stage 6."""
        if not (0 <= index < DPI_STAGE_COUNT):
            raise ValueError(f"Stage index must be 0-{DPI_STAGE_COUNT - 1}")
        self._send([0x40, 0x05, 0x00, 0xa6, index, 0x00, 0x00, 0x01])
        self._send([0x40, 0x05, 0x00, 0x2b, 0x05, 0x00, 0x00, 0x01])

    def set_stage_color(self, index, r, g, b):
        """Assign an RGB color (0-255 each) to one of the 6 DPI stages."""
        if not (0 <= index < DPI_STAGE_COUNT):
            raise ValueError(f"Stage index must be 0-{DPI_STAGE_COUNT - 1}")
        field = STAGE_COLOR_BASE + index * STAGE_COLOR_STEP
        self._send([0x40, 0x05, 0x00, field, r & 0xff, g & 0xff, b & 0xff, 0x03])

    # ---- DPI hardware-button tracking (see NOTE in module docstring) ----

    def start_dpi_button_listener(self, on_press):
        """
        Calls on_press() every time the physical DPI-shift button is pressed
        on the mouse. Does NOT tell you which stage it landed on -- readback
        isn't reliable on this chip -- so the caller is expected to track
        "current stage" itself and just advance it by one (wrapping) each
        time this fires.
        """
        path = self._find_vendor_interface()
        if path is None:
            raise RuntimeError("Recurve 300 not found (vendor interface missing)")

        h = hid.device()
        h.open_path(path)
        h.set_nonblocking(True)
        self._listener_stop.clear()

        def _loop():
            while not self._listener_stop.is_set():
                try:
                    data = h.read(64, timeout_ms=200)
                except Exception:
                    data = None
                if data and data[0] == 0x42 and len(data) >= 4 and data[3] == 0x01:
                    on_press()
            h.close()

        self._listener_thread = threading.Thread(target=_loop, daemon=True)
        self._listener_thread.start()

    def stop_dpi_button_listener(self):
        self._listener_stop.set()
