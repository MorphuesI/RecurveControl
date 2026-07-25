# RecurveControl

Desktop control app for the Mouse Archer Recurve 300.

RecurveControl is a Windows desktop utility built with Python + pywebview that talks directly to the Recurve 300 over HID.  
It currently supports switching DPI stages, changing per-stage RGB colors, and setting polling rate.

## Features

- Native desktop app window (no browser tab UI)
- Device connection status for Recurve 300 (VID:PID `1bcf:08b8`)
- Switch active DPI stage across 6 onboard presets
- Set RGB color for each DPI stage
- Set polling/report rate: 125 / 250 / 500 / 1000 Hz
- Listens for hardware DPI button press events and prompts stage re-sync in UI

## Current limitations

- Arbitrary custom DPI values are not confirmed by protocol and are not applied
- RGB effect modes (breathing/waltz/neon/etc.) are not implemented
- Button remapping and macros are not implemented
- DPI stage readback from hardware is not reliable on this chip, so stage sync is assisted by UI

## Tech stack

- Python
- `hidapi` (USB HID communication)
- `pywebview` (native desktop wrapper for HTML UI)
- `pyinstaller` (Windows executable packaging)

## Project files

- `main.py` — app entrypoint and JS bridge API
- `hid_backend.py` — HID protocol implementation
- `gui.html` — desktop UI
- `build.bat` — one-step Windows build script

## Run from source

1. Install Python 3.10+ on Windows.
2. Install dependencies:
   ```bash
   pip install pywebview hidapi
   ```
3. Start the app:
   ```bash
   python main.py
   ```

## Build `.exe` (Windows)

From the repository root run:

```bat
build.bat
```

Output binary:

- `dist\RecurveControl.exe`

## Suggested repository descriptions

Use one of these in GitHub repository settings:

- **Short description:** `Windows desktop control app for Mouse Archer Recurve 300 (DPI stages, polling rate, stage RGB).`
- **Long description:** `RecurveControl is a Python + pywebview desktop utility for the Mouse Archer Recurve 300 that uses reverse-engineered HID commands to control DPI presets, polling rate, and per-stage RGB colors.`

## Disclaimer

This project is unofficial and not affiliated with the device vendor.

## Repository description (long)

RecurveControl is a Python + pywebview desktop utility for the Mouse Archer Recurve 300 that uses reverse-engineered HID commands to control DPI presets, polling rate, and per-stage RGB colors.
