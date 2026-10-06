"""
DualSense (PS5) controller -> mouse, for scrolling TikTok on Windows.

Controls
  Left stick        move the mouse cursor
  L2 (hold)         slow / precise cursor
  Right stick flick next (down) / previous (up) video
  D-pad down / R1   next video
  D-pad up   / L1   previous video
  Cross   (X)       left click (hold to drag)
  Circle  (O)       right click
  Triangle          like (TikTok web "L" shortcut)
  Square            mute / unmute (TikTok web "M" shortcut)
  R3                play / pause (Space)
  Options           pause / resume the controller mapping
  PS button         quit (Ctrl+C in the console also works)

"Next/previous video" sends one mouse-wheel notch, which is how TikTok's feed
advances, so keep the cursor over the video. The keyboard shortcuts only work
after the TikTok page has focus (click it once).
"""

import ctypes
import math
import os
import sys
import time
from ctypes import wintypes

# Must be set before pygame is imported: keep reading the controller while the
# browser (not this console) has focus, and allow rumble over Bluetooth.
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
os.environ["SDL_JOYSTICK_HIDAPI_PS5_RUMBLE"] = "1"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame  # noqa: E402
from pygame._sdl2 import controller as sdl_controller  # noqa: E402

# ---------------------------------------------------------------- settings ---
POLL_HZ = 120
STICK_DEADZONE = 0.12        # ignore small stick drift (0..1)
CURSOR_MAX_SPEED = 1400      # pixels per second at full tilt
CURSOR_CURVE = 2.2           # >1 = finer control near the center
SLOW_MODE_FACTOR = 0.3       # cursor speed multiplier while L2 is held
FLICK_THRESHOLD = 0.6        # right-stick tilt that counts as a flick
REPEAT_DELAY = 0.45          # seconds before a held direction repeats
REPEAT_INTERVAL = 0.30       # seconds between repeats while held
INVERT_SCROLL = False        # True swaps next/previous directions

# ------------------------------------------------------- Windows SendInput ---
user32 = ctypes.WinDLL("user32", use_last_error=True)
winmm = ctypes.WinDLL("winmm")

INPUT_MOUSE, INPUT_KEYBOARD = 0, 1
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0002, 0x0004
MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP = 0x0008, 0x0010
MOUSEEVENTF_WHEEL = 0x0800
KEYEVENTF_EXTENDEDKEY, KEYEVENTF_KEYUP = 0x0001, 0x0002
WHEEL_DELTA = 120

VK_SPACE, VK_L, VK_M = 0x20, 0x4C, 0x4D


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_size_t)]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD)]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTUNION)]


def _send(*inputs):
    arr = (INPUT * len(inputs))(*inputs)
    user32.SendInput(len(inputs), arr, ctypes.sizeof(INPUT))


def _mouse(flags, dx=0, dy=0, data=0):
    return INPUT(type=INPUT_MOUSE, u=_INPUTUNION(mi=MOUSEINPUT(
        dx=dx, dy=dy, mouseData=data & 0xFFFFFFFF, dwFlags=flags)))


def _key(vk, up=False):
    flags = KEYEVENTF_KEYUP if up else 0
    return INPUT(type=INPUT_KEYBOARD, u=_INPUTUNION(ki=KEYBDINPUT(wVk=vk, dwFlags=flags)))


def move_mouse(dx, dy):
    _send(_mouse(MOUSEEVENTF_MOVE, dx, dy))


def wheel(notches):
    _send(_mouse(MOUSEEVENTF_WHEEL, data=notches * WHEEL_DELTA))


def tap_key(vk):
    _send(_key(vk), _key(vk, up=True))


# -------------------------------------------------------------- input help ---
def norm_axis(raw):
    """SDL axis (-32768..32767) -> -1..1"""
    return max(-1.0, min(1.0, raw / 32767.0))


def apply_deadzone(x, y):
    """Radial deadzone + response curve. Returns scaled (x, y)."""
    mag = math.hypot(x, y)
    if mag < STICK_DEADZONE:
        return 0.0, 0.0
    scaled = min(1.0, (mag - STICK_DEADZONE) / (1.0 - STICK_DEADZONE))
    scaled = scaled ** CURSOR_CURVE
    return x / mag * scaled, y / mag * scaled


class Repeater:
    """Fires once on press, then repeats while held (like keyboard auto-repeat)."""

    def __init__(self):
        self.held_since = None
        self.last_fire = 0.0

    def update(self, active, now):
        if not active:
            self.held_since = None
            return False
        if self.held_since is None:
            self.held_since = self.last_fire = now
            return True
        if now - self.held_since >= REPEAT_DELAY and now - self.last_fire >= REPEAT_INTERVAL:
            self.last_fire = now
            return True
        return False


# -------------------------------------------------------------------- main ---
def find_controller():
    for i in range(sdl_controller.get_count()):
        if sdl_controller.is_controller(i):
            pad = sdl_controller.Controller(i)
            name = pad.name or "controller"
            print(f"Connected: {name}")
            return pad
    return None


def rumble(pad, strength=0.4, ms=120):
    try:
        pad.rumble(strength, strength, ms)
    except Exception:
        pass


def main():
    pygame.init()
    pygame.display.init()  # needed for the event pump; no window is opened
    sdl_controller.init()
    winmm.timeBeginPeriod(1)  # accurate sleep for smooth cursor motion

    B = {
        "cross": pygame.CONTROLLER_BUTTON_A,
        "circle": pygame.CONTROLLER_BUTTON_B,
        "square": pygame.CONTROLLER_BUTTON_X,
        "triangle": pygame.CONTROLLER_BUTTON_Y,
        "options": pygame.CONTROLLER_BUTTON_START,
        "ps": pygame.CONTROLLER_BUTTON_GUIDE,
        "r3": pygame.CONTROLLER_BUTTON_RIGHTSTICK,
        "l1": pygame.CONTROLLER_BUTTON_LEFTSHOULDER,
        "r1": pygame.CONTROLLER_BUTTON_RIGHTSHOULDER,
        "up": pygame.CONTROLLER_BUTTON_DPAD_UP,
        "down": pygame.CONTROLLER_BUTTON_DPAD_DOWN,
    }

    pad = None
    enabled = True
    prev = {name: False for name in B}
    next_rep, prev_rep = Repeater(), Repeater()
    frac_x = frac_y = 0.0
    last = time.perf_counter()
    waiting_msg_shown = False

    print(__doc__)
    try:
        while True:
            pygame.event.pump()
            now = time.perf_counter()
            dt = min(now - last, 0.05)
            last = now

            if pad is None or not pad.attached():
                if pad is not None:
                    print("Controller disconnected.")
                    pad = None
                    if prev["cross"] and enabled:  # don't leave the button stuck down
                        _send(_mouse(MOUSEEVENTF_LEFTUP))
                    prev = {name: False for name in B}
                pad = find_controller()
                if pad is None:
                    if not waiting_msg_shown:
                        print("Waiting for a controller (USB or Bluetooth)...")
                        waiting_msg_shown = True
                    time.sleep(0.5)
                    continue
                waiting_msg_shown = False
                rumble(pad)

            cur = {name: bool(pad.get_button(btn)) for name, btn in B.items()}
            pressed = {n for n in B if cur[n] and not prev[n]}
            released = {n for n in B if not cur[n] and prev[n]}
            prev = cur

            if "ps" in pressed:
                print("PS button pressed - quitting.")
                break

            if "options" in pressed:
                enabled = not enabled
                if not enabled and cur["cross"]:
                    _send(_mouse(MOUSEEVENTF_LEFTUP))
                print("Mapping", "RESUMED" if enabled else "PAUSED (press Options to resume)")
                rumble(pad, 0.6 if enabled else 0.25, 150)

            if not enabled:
                time.sleep(1 / POLL_HZ)
                continue

            # Cursor movement (left stick)
            lx, ly = apply_deadzone(norm_axis(pad.get_axis(pygame.CONTROLLER_AXIS_LEFTX)),
                                    norm_axis(pad.get_axis(pygame.CONTROLLER_AXIS_LEFTY)))
            speed = CURSOR_MAX_SPEED
            if norm_axis(pad.get_axis(pygame.CONTROLLER_AXIS_TRIGGERLEFT)) > 0.3:
                speed *= SLOW_MODE_FACTOR
            frac_x += lx * speed * dt
            frac_y += ly * speed * dt
            mx, my = int(frac_x), int(frac_y)
            if mx or my:
                frac_x -= mx
                frac_y -= my
                move_mouse(mx, my)

            # Next / previous video
            ry = norm_axis(pad.get_axis(pygame.CONTROLLER_AXIS_RIGHTY))
            want_next = cur["down"] or cur["r1"] or ry > FLICK_THRESHOLD
            want_prev = cur["up"] or cur["l1"] or ry < -FLICK_THRESHOLD
            direction = 1 if INVERT_SCROLL else -1  # negative wheel = scroll down
            if next_rep.update(want_next and not want_prev, now):
                wheel(direction)
            if prev_rep.update(want_prev and not want_next, now):
                wheel(-direction)

            # Clicks
            if "cross" in pressed:
                _send(_mouse(MOUSEEVENTF_LEFTDOWN))
            if "cross" in released:
                _send(_mouse(MOUSEEVENTF_LEFTUP))
            if "circle" in pressed:
                _send(_mouse(MOUSEEVENTF_RIGHTDOWN))
            if "circle" in released:
                _send(_mouse(MOUSEEVENTF_RIGHTUP))

            # TikTok shortcuts
            if "triangle" in pressed:
                tap_key(VK_L)
            if "square" in pressed:
                tap_key(VK_M)
            if "r3" in pressed:
                tap_key(VK_SPACE)

            time.sleep(1 / POLL_HZ)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        if pad is not None and prev.get("cross") and enabled:
            _send(_mouse(MOUSEEVENTF_LEFTUP))
        winmm.timeEndPeriod(1)
        pygame.quit()


if __name__ == "__main__":
    if sys.platform != "win32":
        sys.exit("This script uses the Windows SendInput API and only runs on Windows.")
    main()
