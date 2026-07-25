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
window = None  # set in __main__


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

    def set_stage_color(self, index, r, g, b):
        try:
            device.set_stage_color(index, r, g, b)
            return {"ok": True, "message": f"Stage {index + 1} color set"}
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


def _on_dpi_button_press():
    # Runs on the listener thread -- push an event into the page's JS.
    # We can't know the real new stage (readback isn't reliable on this
    # chip), so the frontend just advances its own counter by one on this
    # event; see the note in hid_backend.py.
    if window is not None:
        try:
            window.evaluate_js("window.onHardwareDpiButtonPress && window.onHardwareDpiButtonPress()")
        except Exception:
            pass


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
    try:
        device.start_dpi_button_listener(_on_dpi_button_press)
    except Exception:
        pass  # device not connected yet -- get_status() in the UI will reflect that
    webview.start()
