"""
DualSense (PS5) controller -> mouse for Windows, with three modes.

Press CREATE (the small button left of the touchpad) to switch modes:
  Standard -> TikTok -> Browser

Everywhere
  Left stick        move the mouse cursor (hold L2 for slow, precise movement)
  Cross (X)         left click (hold to drag)
  Circle (O)        right click
  Touchpad click    open / close the on-screen keyboard
  Create            switch mode
  Options           pause / resume the controller mapping
  PS button         quit (Ctrl+C in the console also works)

Standard mode
  Right stick       scroll (up/down and left/right)
  D-pad             arrow keys
  L1 / R1           mouse back / forward buttons
  Square            middle click
  Triangle          open the on-screen keyboard

TikTok mode
  Right stick flick next (down) / previous (up) video
  D-pad down / R1   next video
  D-pad up   / L1   previous video
  Triangle          like
  Square            mute / unmute
  R3                play / pause

Browser mode
  Right stick       scroll the page
  L1 / R1           previous / next tab
  D-pad left/right  back / forward
  D-pad up          reload
  D-pad down (hold) close tab
  Triangle          address bar + keyboard (search or type a URL)
  Square            new tab + keyboard
  R3                middle click (open link in a new tab)
  The keyboard pops up by itself when you click into a search box.

On-screen keyboard
  D-pad / left stick  move    Cross  type key    Square  backspace
  Triangle  space     R2  Enter    L1 / R1  move the text caret
  L2  shift           L3  switch language (English / Arabic / symbols)
  Circle or touchpad  close
"""

import ctypes
import math
import os
import sys
import time

# Must be set before pygame is imported: keep reading the controller while the
# browser (not this console) has focus, and allow rumble over Bluetooth.
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
os.environ["SDL_JOYSTICK_HIDAPI_PS5_RUMBLE"] = "1"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import tkinter as tk  # noqa: E402

import pygame  # noqa: E402
from pygame._sdl2 import controller as sdl_controller  # noqa: E402

import winput as wi  # noqa: E402
from focus_watch import FocusWatcher  # noqa: E402
from overlay import ControllerKeyboard, Toast  # noqa: E402

# ---------------------------------------------------------------- settings ---
DEFAULT_MODE = "standard"    # "standard", "tiktok" or "browser"
POLL_HZ = 120
STICK_DEADZONE = 0.12        # ignore small stick drift (0..1)
CURSOR_MAX_SPEED = 1400      # pixels per second at full tilt
CURSOR_CURVE = 2.2           # >1 = finer control near the center
SLOW_MODE_FACTOR = 0.3       # cursor speed multiplier while L2 is held
SCROLL_SPEED = 2400          # wheel units per second at full tilt (120 = one notch)
FLICK_THRESHOLD = 0.6        # right-stick tilt that counts as a flick (TikTok mode)
REPEAT_DELAY = 0.45          # seconds before a held button repeats
REPEAT_INTERVAL = 0.30       # seconds between repeats while held
KEYBOARD_REPEAT_INTERVAL = 0.09  # faster repeat while moving around the keyboard
CLOSE_TAB_HOLD = 0.5         # seconds to hold D-pad down before a tab closes
INVERT_SCROLL = False        # True swaps TikTok next/previous directions
AUTO_KEYBOARD_MODES = {"browser"}  # modes where the keyboard pops up on text boxes

MODES = ["standard", "tiktok", "browser"]
MODE_INFO = {
    "standard": ("Standard mode", "Controller as a mouse"),
    "tiktok": ("TikTok mode", "Flick right stick or D-pad to change video"),
    "browser": ("Browser mode", "L1 / R1 switch tabs  ·  △ search"),
}

BUTTONS = {
    "cross": pygame.CONTROLLER_BUTTON_A,
    "circle": pygame.CONTROLLER_BUTTON_B,
    "square": pygame.CONTROLLER_BUTTON_X,
    "triangle": pygame.CONTROLLER_BUTTON_Y,
    "create": pygame.CONTROLLER_BUTTON_BACK,
    "options": pygame.CONTROLLER_BUTTON_START,
    "ps": pygame.CONTROLLER_BUTTON_GUIDE,
    "l3": pygame.CONTROLLER_BUTTON_LEFTSTICK,
    "r3": pygame.CONTROLLER_BUTTON_RIGHTSTICK,
    "l1": pygame.CONTROLLER_BUTTON_LEFTSHOULDER,
    "r1": pygame.CONTROLLER_BUTTON_RIGHTSHOULDER,
    "up": pygame.CONTROLLER_BUTTON_DPAD_UP,
    "down": pygame.CONTROLLER_BUTTON_DPAD_DOWN,
    "left": pygame.CONTROLLER_BUTTON_DPAD_LEFT,
    "right": pygame.CONTROLLER_BUTTON_DPAD_RIGHT,
    "touchpad": 20,  # SDL_CONTROLLER_BUTTON_TOUCHPAD (no pygame constant)
}
TRIGGERS = {"l2": pygame.CONTROLLER_AXIS_TRIGGERLEFT, "r2": pygame.CONTROLLER_AXIS_TRIGGERRIGHT}
TRIGGER_PRESS = 0.5


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

    def __init__(self, interval=REPEAT_INTERVAL):
        self.interval = interval
        self.held_since = None
        self.last_fire = 0.0

    def update(self, active, now):
        if not active:
            self.held_since = None
            return False
        if self.held_since is None:
            self.held_since = self.last_fire = now
            return True
        if now - self.held_since >= REPEAT_DELAY and now - self.last_fire >= self.interval:
            self.last_fire = now
            return True
        return False


class Repeaters(dict):
    """Lazily created Repeater per name."""

    def __init__(self, interval=REPEAT_INTERVAL):
        super().__init__()
        self.interval = interval

    def __missing__(self, key):
        self[key] = Repeater(self.interval)
        return self[key]


# -------------------------------------------------------------------- app ----
class App:
    def __init__(self):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # crisp overlay on high-DPI screens
        except Exception:
            pass
        pygame.init()
        pygame.display.init()  # needed for the event pump; no window is opened
        sdl_controller.init()
        ctypes.windll.winmm.timeBeginPeriod(1)

        user32 = ctypes.windll.user32
        previous_window = user32.GetForegroundWindow()
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.report_callback_exception = self._on_error
        scale = self.root.winfo_fpixels("1i") / 96.0
        self.keyboard = ControllerKeyboard(self.root, scale)
        self.toast = Toast(self.root, scale)
        self.root.update()
        user32.SetForegroundWindow(previous_window)  # creating Tk windows grabs focus
        self.watcher = FocusWatcher()

        self.pad = None
        self.next_pad_search = 0.0
        self.waiting_msg_shown = False
        self.mode = DEFAULT_MODE
        self.enabled = True
        self.prev = {}
        self.suppressed = set()   # buttons ignored until released (after the keyboard closes)
        self.held_mouse = set()
        self.rep = Repeaters()
        self.kb_rep = Repeaters(KEYBOARD_REPEAT_INTERVAL)
        self.frac = [0.0, 0.0]
        self.scroll_acc = [0.0, 0.0]
        self.close_tab_since = None
        self.close_tab_done = False
        self.dismissed_focus = None
        self.keyboard_opened_at = 0.0
        self.last = time.perf_counter()
        self.running = True

    # ---- lifecycle --------------------------------------------------------
    def run(self):
        print(__doc__)
        self.set_mode(self.mode, announce=False)
        self.root.after(1, self.tick)
        self.root.mainloop()

    def quit(self):
        if not self.running:
            return
        self.running = False
        self.release_mouse()
        self.watcher.stop()
        ctypes.windll.winmm.timeEndPeriod(1)
        self.root.quit()

    def _on_error(self, exc_type, exc, tb):
        if exc_type is KeyboardInterrupt:
            print("\nStopped.")
            self.quit()
        else:
            import traceback
            traceback.print_exception(exc_type, exc, tb)

    # ---- helpers ----------------------------------------------------------
    def rumble(self, strength=0.4, ms=120):
        try:
            self.pad.rumble(strength, strength, ms)
        except Exception:
            pass

    def mouse(self, name, down):
        if down and name not in self.held_mouse:
            self.held_mouse.add(name)
            wi.mouse_button(name, True)
        elif not down and name in self.held_mouse:
            self.held_mouse.discard(name)
            wi.mouse_button(name, False)

    def release_mouse(self):
        for name in list(self.held_mouse):
            self.mouse(name, False)

    def set_mode(self, mode, announce=True):
        self.mode = mode
        self.release_mouse()
        self.keyboard.close()
        self.watcher.active = mode in AUTO_KEYBOARD_MODES
        self.dismissed_focus = self.watcher.focus_id  # don't pop up for what is already focused
        title, subtitle = MODE_INFO[mode]
        print(f"Mode: {title}")
        self.toast.show(title, subtitle)
        if announce:
            self.rumble(0.5, 90)

    def open_keyboard(self, auto=False):
        self.release_mouse()
        self.keyboard.open(auto=auto)
        self.keyboard_opened_at = time.perf_counter()

    def close_keyboard(self, dismiss=True):
        self.keyboard.close()
        # Don't let the button that closed the keyboard click or act on the page.
        self.suppressed = {n for n, down in self.prev.items() if down}
        if dismiss:
            self.dismissed_focus = self.watcher.focus_id

    def find_controller(self, now):
        if now < self.next_pad_search:
            return
        self.next_pad_search = now + 0.5
        for i in range(sdl_controller.get_count()):
            if sdl_controller.is_controller(i):
                self.pad = sdl_controller.Controller(i)
                print(f"Connected: {self.pad.name or 'controller'}")
                self.waiting_msg_shown = False
                self.prev = {}
                self.rumble()
                return
        if not self.waiting_msg_shown:
            print("Waiting for a controller (USB or Bluetooth)...")
            self.waiting_msg_shown = True

    # ---- main loop --------------------------------------------------------
    def tick(self):
        if not self.running:
            return
        try:
            self.step()
        finally:
            if self.running:
                self.root.after(max(1, int(1000 / POLL_HZ)), self.tick)

    def step(self):
        pygame.event.pump()
        now = time.perf_counter()
        dt = min(now - self.last, 0.05)
        self.last = now

        if self.pad is not None and not self.pad.attached():
            print("Controller disconnected.")
            self.pad = None
            self.release_mouse()
            self.keyboard.close()
        if self.pad is None:
            self.find_controller(now)
            return

        pad = self.pad
        cur = {name: bool(pad.get_button(btn)) for name, btn in BUTTONS.items()}
        for name, axis in TRIGGERS.items():
            cur[name] = norm_axis(pad.get_axis(axis)) > TRIGGER_PRESS
        self.suppressed = {n for n in self.suppressed if cur[n]}
        for name in self.suppressed:
            cur[name] = False
        pressed = {n for n in cur if cur[n] and not self.prev.get(n, False)}
        self.prev = cur

        if "ps" in pressed:
            print("PS button pressed - quitting.")
            self.quit()
            return

        if "options" in pressed:
            self.enabled = not self.enabled
            self.release_mouse()
            self.keyboard.close()
            print("Mapping", "RESUMED" if self.enabled else "PAUSED (press Options to resume)")
            self.toast.show("Resumed" if self.enabled else "Paused",
                            "" if self.enabled else "Press Options to resume")
            self.rumble(0.6 if self.enabled else 0.25, 150)
        if not self.enabled:
            return

        if "create" in pressed:
            self.set_mode(MODES[(MODES.index(self.mode) + 1) % len(MODES)])
            return

        lx = norm_axis(pad.get_axis(pygame.CONTROLLER_AXIS_LEFTX))
        ly = norm_axis(pad.get_axis(pygame.CONTROLLER_AXIS_LEFTY))
        rx = norm_axis(pad.get_axis(pygame.CONTROLLER_AXIS_RIGHTX))
        ry = norm_axis(pad.get_axis(pygame.CONTROLLER_AXIS_RIGHTY))

        self.update_auto_keyboard(now)

        if self.keyboard.visible:
            self.keyboard_controls(cur, pressed, lx, ly, now)
            return

        if "touchpad" in pressed:
            self.open_keyboard()
            return

        self.move_cursor(lx, ly, cur["l2"], dt)
        self.mouse("left", cur["cross"])
        self.mouse("right", cur["circle"])

        if self.mode == "standard":
            self.standard_controls(cur, pressed, rx, ry, dt, now)
        elif self.mode == "tiktok":
            self.tiktok_controls(cur, pressed, ry, now)
        else:
            self.browser_controls(cur, pressed, rx, ry, dt, now)

    # ---- shared -----------------------------------------------------------
    def move_cursor(self, lx, ly, slow, dt):
        x, y = apply_deadzone(lx, ly)
        speed = CURSOR_MAX_SPEED * (SLOW_MODE_FACTOR if slow else 1.0)
        self.frac[0] += x * speed * dt
        self.frac[1] += y * speed * dt
        mx, my = int(self.frac[0]), int(self.frac[1])
        if mx or my:
            self.frac[0] -= mx
            self.frac[1] -= my
            wi.move_mouse(mx, my)

    def smooth_scroll(self, rx, ry, dt):
        x, y = apply_deadzone(rx, ry)
        self.scroll_acc[0] += x * SCROLL_SPEED * dt
        self.scroll_acc[1] += -y * SCROLL_SPEED * dt  # stick down = scroll down
        for i, send in ((0, wi.hwheel), (1, wi.wheel)):
            if abs(self.scroll_acc[i]) >= 10:
                delta = int(self.scroll_acc[i])
                self.scroll_acc[i] -= delta
                send(delta)
        if x == 0:
            self.scroll_acc[0] = 0.0
        if y == 0:
            self.scroll_acc[1] = 0.0

    def held(self, name, active, now):
        return self.rep[name].update(active, now)

    # ---- modes ------------------------------------------------------------
    def standard_controls(self, cur, pressed, rx, ry, dt, now):
        self.smooth_scroll(rx, ry, dt)
        self.mouse("middle", cur["square"])
        self.mouse("back", cur["l1"])
        self.mouse("forward", cur["r1"])
        for name, vk in (("up", wi.VK_UP), ("down", wi.VK_DOWN),
                         ("left", wi.VK_LEFT), ("right", wi.VK_RIGHT)):
            if self.held(name, cur[name], now):
                wi.tap(vk)
        if "triangle" in pressed:
            self.open_keyboard()

    def tiktok_controls(self, cur, pressed, ry, now):
        want_next = cur["down"] or cur["r1"] or ry > FLICK_THRESHOLD
        want_prev = cur["up"] or cur["l1"] or ry < -FLICK_THRESHOLD
        direction = 1 if INVERT_SCROLL else -1  # negative wheel = scroll down
        if self.held("next_video", want_next and not want_prev, now):
            wi.wheel(direction * wi.WHEEL_DELTA)
        if self.held("prev_video", want_prev and not want_next, now):
            wi.wheel(-direction * wi.WHEEL_DELTA)
        if "triangle" in pressed:
            wi.tap(wi.VK_L)
        if "square" in pressed:
            wi.tap(wi.VK_M)
        if "r3" in pressed:
            wi.tap(wi.VK_SPACE)

    def browser_controls(self, cur, pressed, rx, ry, dt, now):
        self.smooth_scroll(rx, ry, dt)
        self.mouse("middle", cur["r3"])
        if self.held("prev_tab", cur["l1"] and not cur["r1"], now):
            wi.combo(wi.VK_CONTROL, wi.VK_SHIFT, wi.VK_TAB)
        if self.held("next_tab", cur["r1"] and not cur["l1"], now):
            wi.combo(wi.VK_CONTROL, wi.VK_TAB)
        if "left" in pressed:
            wi.combo(wi.VK_MENU, wi.VK_LEFT)
        if "right" in pressed:
            wi.combo(wi.VK_MENU, wi.VK_RIGHT)
        if "up" in pressed:
            wi.tap(wi.VK_F5)

        # Close tab only after a deliberate hold, so a bump doesn't lose a page.
        if cur["down"]:
            if self.close_tab_since is None:
                self.close_tab_since, self.close_tab_done = now, False
            elif not self.close_tab_done and now - self.close_tab_since >= CLOSE_TAB_HOLD:
                wi.combo(wi.VK_CONTROL, wi.VK_W)
                self.close_tab_done = True
                self.rumble(0.5, 80)
        else:
            self.close_tab_since = None

        if "triangle" in pressed:
            wi.combo(wi.VK_CONTROL, wi.VK_L)
            self.open_keyboard(auto=True)
        if "square" in pressed:
            wi.combo(wi.VK_CONTROL, wi.VK_T)
            self.open_keyboard(auto=True)

    # ---- keyboard ---------------------------------------------------------
    def update_auto_keyboard(self, now):
        w = self.watcher
        if not w.active:
            return
        if w.text_focused and not self.keyboard.visible and w.focus_id != self.dismissed_focus:
            self.open_keyboard(auto=True)
            self.dismissed_focus = w.focus_id
        elif (self.keyboard.visible and self.keyboard.auto and not w.text_focused
              and w.last_text_time > self.keyboard_opened_at       # it did see the text box
              and now - self.keyboard_opened_at > 1.5 and now - w.last_text_time > 0.8):
            self.close_keyboard(dismiss=False)  # focus left the text box (e.g. search submitted)
        if not w.text_focused:
            self.dismissed_focus = None

    def keyboard_controls(self, cur, pressed, lx, ly, now):
        kb = self.keyboard
        stick = {
            "up": ly < -0.5 and abs(ly) > abs(lx),
            "down": ly > 0.5 and abs(ly) > abs(lx),
            "left": lx < -0.5 and abs(lx) >= abs(ly),
            "right": lx > 0.5 and abs(lx) >= abs(ly),
        }
        for d in ("up", "down", "left", "right"):
            if self.kb_rep[d].update(cur[d] or stick[d], now):
                kb.move(d)

        if "circle" in pressed or "touchpad" in pressed:
            self.close_keyboard()
            return
        if "cross" in pressed and kb.press_selected() == "enter":
            self.close_keyboard()
            return
        if self.rep["kb_bksp"].update(cur["square"], now):
            kb.do("#bksp")
        if "triangle" in pressed:
            kb.do("#space")
        if "r2" in pressed:
            kb.do("#enter")
            self.close_keyboard()
            return
        if self.kb_rep["caret_left"].update(cur["l1"], now):
            kb.do("#left")
        if self.kb_rep["caret_right"].update(cur["r1"], now):
            kb.do("#right")
        if "l2" in pressed:
            kb.cycle_shift()
        if "l3" in pressed:
            kb.next_layout()


if __name__ == "__main__":
    if sys.platform != "win32":
        sys.exit("This program uses the Windows SendInput API and only runs on Windows.")
    sys.stdout.reconfigure(errors="replace")
    App().run()
