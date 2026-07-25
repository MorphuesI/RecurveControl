@echo off
REM Build script for Recurve Control.
REM Run this ONCE on your Windows machine, in this folder, with Python installed.

echo Installing dependencies...
pip install pywebview hidapi pyinstaller

echo.
echo Building RecurveControl.exe ...
pyinstaller --noconfirm --onefile ^
    --name RecurveControl ^
    --add-data "gui.html;." ^
    main.py

echo.
echo Done. Find it at: dist\RecurveControl.exe
pause
