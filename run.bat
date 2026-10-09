@echo off
cd /d "%~dp0"
echo Checking dependencies...
python -m pip install -q --disable-pip-version-check -r requirements.txt
start "" pythonw dualsense_mouse.py
