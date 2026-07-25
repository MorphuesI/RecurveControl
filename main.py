"""
main.py — entry point for Recurve Control.

Opens a native desktop window (via pywebview / WebView2 on Windows — this is
NOT a browser tab, no address bar, just an app window) showing gui.html, and
exposes hardware calls to it through the Api class below.
"""

import os
import sys
import webview

from hid_backend import RecurveDevice

device = RecurveDevice()


class Api:
    def get_status(self):
        try:
            connected = device.is_connected()
        except Exception:
            connected = False
        return {"connected": connected}

    def set_polling_rate(self, hz):
        try:
            device.set_polling_rate(hz)
            return {"ok": True, "message": f"Polling rate set to {hz} Hz"}
        except Exception as e:
            return {"ok": False, "message": f"Failed: {e}"}

    def set_dpi_stage(self, index):
        try:
            device.set_dpi_stage(index)
            return {"ok": True, "message": f"DPI stage {index + 1} active"}
        except Exception as e:
            return {"ok": False, "message": f"Failed: {e}"}

    def set_custom_dpi(self, value):
        # Not confirmed to be supported by the hardware protocol yet.
        return {
            "ok": False,
            "message": "Custom DPI values aren't confirmed supported by this "
                       "mouse's protocol yet — only switching between the 6 "
                       "onboard presets is wired up so far.",
        }


def resource_path(relative_path):
    """Works both when run as a script and when bundled by PyInstaller."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    api = Api()
    window = webview.create_window(
        "Recurve Control",
        resource_path("gui.html"),
        js_api=api,
        width=1000,
        height=680,
        min_size=(860, 600),
        background_color="#0b0c10",
    )
    webview.start()
