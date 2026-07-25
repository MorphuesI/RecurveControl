"""
hid_backend.py — the ONLY file that talks to the mouse.

Everything here is original code written against the HID protocol we
reverse-engineered from Wireshark captures of the mouse's own USB traffic.
No vendor code, binaries, or firmware is used or embedded.

Confirmed via isolated captures + live hardware tests:
  - Polling rate (Report ID 0x40, subcmd 0x05, field 0x04 / 0x08)
  - DPI preset selection (Report ID 0x40, subcmd 0x05, field 0xa6 / 0x2b)

NOT yet confirmed / not implemented:
  - Arbitrary custom DPI values (the mouse appears to only support switching
    between 6 onboard presets, not writing a free-form number)
  - RGB / lighting modes, brightness, breathing speed
  - Button remapping / macros
"""

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


class RecurveDevice:
    """Thin wrapper around the vendor HID interface (usage_page 0xff00)."""

    def __init__(self):
        self._path = None

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
