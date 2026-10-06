"""On-screen controller keyboard and mode toast.

Both windows are "no-activate" overlays: they float on top but never take
focus, so whatever you type goes straight into the browser's text box.
"""

import ctypes
import tkinter as tk
from ctypes import wintypes

import winput

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]

GWL_EXSTYLE = -20
WS_EX_TOPMOST, WS_EX_TOOLWINDOW, WS_EX_NOACTIVATE = 0x8, 0x80, 0x08000000
SW_HIDE, SW_SHOWNOACTIVATE = 0, 4
HWND_TOPMOST = -1
SWP_NOSIZE, SWP_NOMOVE, SWP_NOACTIVATE = 0x1, 0x2, 0x10
MONITOR_DEFAULTTONEAREST = 2

TRANSPARENT = "#010203"
BG = "#16181d"
KEY = "#2a2e37"
KEY_SPECIAL = "#353a45"
KEY_ACTIVE = "#2f6bff"
TEXT = "#f2f4f8"
TEXT_DIM = "#9aa3b2"
FONT = "Segoe UI"


class MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT),
                ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]


def work_area_at_cursor():
    """(left, top, right, bottom) of the work area on the monitor under the cursor."""
    pt = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    user32.MonitorFromPoint.restype = wintypes.HMONITOR
    mon = user32.MonitorFromPoint(pt, MONITOR_DEFAULTTONEAREST)
    info = MONITORINFO(cbSize=ctypes.sizeof(MONITORINFO))
    user32.GetMonitorInfoW(mon, ctypes.byref(info))
    r = info.rcWork
    return r.left, r.top, r.right, r.bottom


class NoActivateWindow:
    """A borderless, always-on-top window that never steals focus."""

    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.withdraw()
        self.top.overrideredirect(True)
        self.top.configure(bg=TRANSPARENT)
        self.top.attributes("-topmost", True)
        self.top.attributes("-transparentcolor", TRANSPARENT)
        self.top.update_idletasks()
        self.hwnd = user32.GetParent(self.top.winfo_id())
        style = user32.GetWindowLongPtrW(self.hwnd, GWL_EXSTYLE)
        user32.SetWindowLongPtrW(self.hwnd, GWL_EXSTYLE,
                                 style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TOPMOST)
        self.visible = False

    def show_at(self, x, y):
        self.top.geometry(f"+{int(x)}+{int(y)}")
        if not self.visible:
            self.top.deiconify()
            user32.ShowWindow(self.hwnd, SW_SHOWNOACTIVATE)
            self.visible = True
        user32.SetWindowPos(self.hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                            SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE)

    def hide(self):
        if self.visible:
            self.top.withdraw()
            self.visible = False


def rounded_rect(canvas, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


# ---------------------------------------------------------------- toast -----
class Toast(NoActivateWindow):
    def __init__(self, root, scale):
        super().__init__(root)
        self.scale = scale
        self.canvas = tk.Canvas(self.top, bg=TRANSPARENT, highlightthickness=0)
        self.canvas.pack()
        self._hide_job = None

    def show(self, title, subtitle="", ms=1600):
        s = self.scale
        w, h = int(360 * s), int((86 if subtitle else 58) * s)
        c = self.canvas
        c.delete("all")
        c.configure(width=w, height=h)
        rounded_rect(c, 0, 0, w, h, 18 * s, fill=BG, outline=KEY_ACTIVE, width=max(1, int(2 * s)))
        c.create_text(w / 2, 30 * s, text=title, fill=TEXT, font=(FONT, 15, "bold"))
        if subtitle:
            c.create_text(w / 2, 62 * s, text=subtitle, fill=TEXT_DIM, font=(FONT, 10))
        left, top, right, _ = work_area_at_cursor()
        self.show_at(left + (right - left - w) / 2, top + 40 * s)
        if self._hide_job:
            self.top.after_cancel(self._hide_job)
        self._hide_job = self.top.after(ms, self.hide)


# -------------------------------------------------------------- keyboard ----
# Each key: (label, action, width in key units). Action is text to type or a
# command starting with "#". Every row adds up to 11 units.
def _chars(s):
    return [(c, c, 1) for c in s]


BKSP = ("⌫", "#bksp", 1)
ENTER2 = ("Enter ↵", "#enter", 2)

LAYOUTS = {
    "en": [
        _chars("1234567890") + [BKSP],
        _chars("qwertyuiop/"),
        _chars("asdfghjkl") + [ENTER2],
        [("⇧ Shift", "#shift", 2)] + _chars("zxcvbnm,.") ,
        [("&123", "#layout:sym", 1.5), ("عربي", "#layout:ar", 1.5), ("@", "@", 1),
         ("Space", "#space", 4.5), (".com", ".com", 1.5), ("-", "-", 1)],
    ],
    "sym": [
        _chars("1234567890") + [BKSP],
        _chars("!@#$%^&*()?"),
        _chars("-_=+/\\:;'") + [ENTER2],
        _chars("`~|<>[]{}\","),
        [("ABC", "#layout:en", 1.5), ("عربي", "#layout:ar", 1.5), (".", ".", 1),
         ("Space", "#space", 4.5), (".com", ".com", 1.5), ("€", "€", 1)],
    ],
    "ar": [
        _chars("1234567890") + [BKSP],
        _chars("ضصثقفغعهخحج"),
        _chars("شسيبلاتنمكط"),
        _chars("ذئءؤرىةوزظد"),
        [("ABC", "#layout:en", 1.25), ("&123", "#layout:sym", 1.25), ("أ", "أ", 1), ("إ", "إ", 1),
         ("آ", "آ", 1), ("مسافة", "#space", 2.5), ("،", "،", 1), ("؟", "؟", 1), ("↵", "#enter", 1)],
    ],
}
LAYOUT_ORDER = ["en", "ar", "sym"]

HINT = "✕ Type    □ Delete    △ Space    R2 Enter    L1/R1 Move caret    L2 Shift    L3 Language    ○ Close"


class ControllerKeyboard(NoActivateWindow):
    def __init__(self, root, scale):
        super().__init__(root)
        self.scale = scale
        self.unit = 62 * scale
        self.row_h = 56 * scale
        self.gap = 6 * scale
        self.pad = 16 * scale
        self.hint_h = 34 * scale
        self.layout = "en"
        self.shift = 0          # 0 off, 1 next letter, 2 caps lock
        self.row, self.col = 1, 0
        self.target_x = None    # remembered column when moving up/down
        self.auto = False       # opened automatically by a focused text box
        self.width = int(11 * self.unit + 2 * self.pad)
        self.height = int(5 * self.row_h + 2 * self.pad + self.hint_h)
        self.canvas = tk.Canvas(self.top, width=self.width, height=self.height,
                                bg=TRANSPARENT, highlightthickness=0)
        self.canvas.pack()

    # ---- showing ----------------------------------------------------------
    def open(self, auto=False):
        self.auto = auto
        if not self.visible:
            left, top, right, bottom = work_area_at_cursor()
            self.draw()
            self.show_at(left + (right - left - self.width) / 2,
                         bottom - self.height - 24 * self.scale)

    def close(self):
        self.hide()

    # ---- geometry ---------------------------------------------------------
    def _rows(self):
        return LAYOUTS[self.layout]

    def _key_box(self, r, i):
        x = self.pad
        for label, action, w in self._rows()[r][:i]:
            x += w * self.unit
        w = self._rows()[r][i][2] * self.unit
        y = self.pad + r * self.row_h
        return x, y, x + w, y + self.row_h

    def _center_x(self, r, i):
        x1, _, x2, _ = self._key_box(r, i)
        return (x1 + x2) / 2

    # ---- drawing ----------------------------------------------------------
    def _label(self, label, action):
        if self.shift and len(action) == 1 and action.isalpha():
            return label.upper()
        if action == "#shift":
            return {0: "⇧ Shift", 1: "⬆ Shift", 2: "⇪ CAPS"}[self.shift]
        return label

    def draw(self):
        c, s, g = self.canvas, self.scale, self.gap
        c.delete("all")
        rounded_rect(c, 0, 0, self.width, self.height, 22 * s, fill=BG, outline="#2b3040")
        for r, row in enumerate(self._rows()):
            for i, (label, action, _) in enumerate(row):
                x1, y1, x2, y2 = self._key_box(r, i)
                selected = (r, i) == (self.row, self.col)
                fill = KEY_ACTIVE if selected else (KEY_SPECIAL if action.startswith("#") else KEY)
                if action == "#shift" and self.shift and not selected:
                    fill = "#3d4a6b"
                rounded_rect(c, x1 + g / 2, y1 + g / 2, x2 - g / 2, y2 - g / 2, 10 * s, fill=fill)
                size = 16 if len(label) == 1 else 11
                c.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=self._label(label, action),
                              fill=TEXT, font=(FONT, size, "bold" if selected else "normal"))
        c.create_text(self.width / 2, self.height - self.pad - self.hint_h / 2 + 6 * s,
                      text=HINT, fill=TEXT_DIM, font=(FONT, 9))

    # ---- navigation -------------------------------------------------------
    def move(self, direction):
        rows = self._rows()
        if direction in ("left", "right"):
            step = 1 if direction == "right" else -1
            self.col = (self.col + step) % len(rows[self.row])
            self.target_x = None
        else:
            if self.target_x is None:
                self.target_x = self._center_x(self.row, self.col)
            step = 1 if direction == "down" else -1
            self.row = (self.row + step) % len(rows)
            self.col = min(range(len(rows[self.row])),
                           key=lambda i: abs(self._center_x(self.row, i) - self.target_x))
        self.draw()

    def set_layout(self, name):
        self.layout = name
        self.row = min(self.row, len(self._rows()) - 1)
        self.col = min(self.col, len(self._rows()[self.row]) - 1)
        self.target_x = None
        self.draw()

    def next_layout(self):
        i = LAYOUT_ORDER.index(self.layout)
        self.set_layout(LAYOUT_ORDER[(i + 1) % len(LAYOUT_ORDER)])

    def cycle_shift(self):
        self.shift = (self.shift + 1) % 3
        self.draw()

    # ---- typing -----------------------------------------------------------
    def press_selected(self):
        """Activate the highlighted key. Returns "enter" if Enter was pressed."""
        _, action, _ = self._rows()[self.row][self.col]
        return self.do(action)

    def do(self, action):
        if action == "#bksp":
            winput.tap(winput.VK_BACK)
        elif action == "#space":
            winput.tap(winput.VK_SPACE)
        elif action == "#enter":
            winput.tap(winput.VK_RETURN)
            return "enter"
        elif action == "#shift":
            self.cycle_shift()
        elif action.startswith("#layout:"):
            self.set_layout(action.split(":", 1)[1])
        elif action == "#left":
            winput.tap(winput.VK_LEFT)
        elif action == "#right":
            winput.tap(winput.VK_RIGHT)
        else:
            text = action
            if self.shift and len(text) == 1:
                text = text.upper()
                if self.shift == 1:
                    self.shift = 0
                    self.draw()
            winput.type_text(text)
        return None
