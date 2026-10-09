"""Control panel window: a drawn DualSense with every button labelled for the active mode."""

import tkinter as tk

from controls import ACTIONS, MODE_DESCRIPTIONS, MODE_NAMES
from overlay import rounded_rect

FONT = "Segoe UI"
BG = "#0f1115"
PANEL = "#16181d"
LINE = "#343a48"
TEXT = "#f2f4f8"
TEXT_DIM = "#8b93a3"
TEXT_OFF = "#4b5263"
ACCENT = "#2f6bff"
BODY = "#eef0f4"
BODY_EDGE = "#c3c9d4"
TOUCHPAD = "#dde1e8"
DARK = "#1b1e25"
PART = "#3a3f4b"
MODE_COLORS = {"standard": "#2f6bff", "tiktok": "#fe2c55", "browser": "#22c55e", "keyboard": "#f5a524"}
SYMBOL_COLORS = {"triangle": "#3ddc97", "circle": "#ff5b6e", "cross": "#6aa8ff", "square": "#e58ae8"}

# Drawing space is 1040 x 590 units, scaled by the screen DPI.
W, H, OX = 1040, 590, 20

LEFT = ["l2", "l1", "create", "up", "left", "right", "down", "lstick", "l3"]
RIGHT = ["r2", "r1", "options", "triangle", "circle", "square", "cross", "rstick", "r3"]
CHIPS = {
    "l2": "L2", "l1": "L1", "r2": "R2", "r1": "R1", "create": "Create", "options": "Options",
    "up": "↑", "down": "↓", "left": "←", "right": "→",
    "triangle": "△", "circle": "○", "cross": "✕", "square": "□",
    "lstick": "L stick", "rstick": "R stick", "l3": "L3 press", "r3": "R3 press",
    "touchpad": "Touchpad", "ps": "PS",
}
ANCHORS = {
    "l2": (350, 92), "l1": (350, 122), "r2": (650, 92), "r1": (650, 122),
    "create": (382, 167), "options": (618, 167),
    "up": (307, 206), "left": (277, 241), "right": (349, 253), "down": (307, 276),
    "triangle": (680, 200), "circle": (720, 241), "square": (640, 241), "cross": (680, 282),
    "lstick": (420, 322), "l3": (420, 322), "rstick": (580, 322), "r3": (580, 322),
    "touchpad": (500, 150), "ps": (500, 334),
}
STICK_TRAVEL = 11


class ControlPanel:
    def __init__(self, root, scale, on_mode, on_pause):
        self.root, self.s = root, scale
        self.on_mode, self.on_pause = on_mode, on_pause
        self.mode = "standard"
        self.keyboard_open = False
        self.preview_keyboard = False
        self.paused = False
        self.pressed = set()
        self.parts = {}       # button -> [(canvas item, normal fill)]
        self.callouts = {}    # button -> (chip item, chip text item, action text item)

        root.title("Use Your Controller on Desktop")
        root.configure(bg=BG)
        root.resizable(False, False)
        self._build_header()
        self.canvas = tk.Canvas(root, width=self.x(W), height=self.x(H), bg=BG, highlightthickness=0)
        self.canvas.pack(padx=self.x(12))
        self._build_footer()
        self._draw_controller()
        self._draw_callouts()
        self._refresh_view()

    # ---- scaling ------------------------------------------------------------
    def x(self, v):
        return int(v * self.s)

    def p(self, *coords):
        """Scale (x, y, x, y, ...) drawing coordinates to canvas pixels."""
        return [(v + (OX if i % 2 == 0 else 0)) * self.s for i, v in enumerate(coords)]

    # ---- header / footer ----------------------------------------------------
    def _button(self, parent, text, command):
        b = tk.Label(parent, text=text, bg=PANEL, fg=TEXT, font=(FONT, 10),
                     padx=self.x(16), pady=self.x(7), cursor="hand2")
        b.bind("<Button-1>", lambda e: command())
        return b

    def _build_header(self):
        pad = self.x(18)
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=pad, pady=(pad, 0))
        tk.Label(top, text="Use Your Controller on Desktop", bg=BG, fg=TEXT,
                 font=(FONT, 16, "bold")).pack(side="left")
        self.status = tk.Label(top, text="", bg=PANEL, fg=TEXT_DIM, font=(FONT, 10),
                               padx=self.x(12), pady=self.x(5))
        self.status.pack(side="right")

        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=pad, pady=(self.x(14), 0))
        tk.Label(bar, text="Mode", bg=BG, fg=TEXT_DIM, font=(FONT, 10)).pack(side="left", padx=(0, self.x(10)))
        self.mode_buttons = {}
        for mode in ("standard", "tiktok", "browser"):
            b = self._button(bar, MODE_NAMES[mode], lambda m=mode: self.on_mode(m))
            b.pack(side="left", padx=(0, self.x(4)))
            self.mode_buttons[mode] = b
        self.pause_button = self._button(bar, "Pause", self.on_pause)
        self.pause_button.pack(side="right")
        self.kb_button = self._button(bar, "Keyboard controls", self._toggle_preview)
        self.kb_button.pack(side="right", padx=(0, self.x(6)))

        self.description = tk.Label(self.root, text="", bg=BG, fg=TEXT_DIM, font=(FONT, 10), anchor="w")
        self.description.pack(fill="x", padx=pad, pady=(self.x(10), 0))

    def _build_footer(self):
        pad = self.x(18)
        foot = tk.Frame(self.root, bg=BG)
        foot.pack(fill="x", padx=pad, pady=(0, pad))
        tk.Label(foot, text="Press Create on the controller to switch modes  ·  Options pauses  ·  PS quits",
                 bg=BG, fg=TEXT_DIM, font=(FONT, 9)).pack(side="left")
        self.message = tk.Label(foot, text="", bg=BG, fg=TEXT_DIM, font=(FONT, 9))
        self.message.pack(side="right")

    # ---- controller drawing -------------------------------------------------
    def _part(self, button, item, fill):
        self.parts.setdefault(button, []).append((item, fill))
        return item

    def _rrect(self, x1, y1, x2, y2, r, **kw):
        return rounded_rect(self.canvas, *self.p(x1, y1, x2, y2), r * self.s, **kw)

    def _circle(self, cx, cy, r, **kw):
        return self.canvas.create_oval(*self.p(cx - r, cy - r, cx + r, cy + r), **kw)

    def _draw_controller(self):
        c, s = self.canvas, self.s
        # Triggers and bumpers peek out above the body.
        for side, x1, x2 in (("l", 310, 392), ("r", 608, 690)):
            self._part(f"{side}2", self._rrect(x1, 76, x2, 124, 12, fill=TOUCHPAD, outline=BODY_EDGE), TOUCHPAD)
            fill = c.create_rectangle(*self.p(x1 + 6, 112, x2 - 6, 112), fill=ACCENT, width=0)
            setattr(self, f"{side}2_fill", (fill, x1 + 6, x2 - 6))
        for side, x1, x2 in (("l", 298, 402), ("r", 598, 702)):
            self._part(f"{side}1", self._rrect(x1, 110, x2, 146, 12, fill=TOUCHPAD, outline=BODY_EDGE), TOUCHPAD)

        body = [330, 138, 420, 128, 580, 128, 670, 138, 720, 160, 752, 212, 772, 300, 792, 400,
                786, 458, 750, 484, 704, 472, 668, 432, 630, 392, 600, 385, 400, 385, 370, 392,
                332, 432, 296, 472, 250, 484, 214, 458, 208, 400, 228, 300, 248, 212, 280, 160]
        c.create_polygon(*self.p(*body), smooth=True, fill=BODY, outline=BODY_EDGE, width=max(1, int(2 * s)))
        panel = [400, 262, 600, 262, 616, 330, 596, 378, 404, 378, 384, 330]
        c.create_polygon(*self.p(*panel), smooth=True, fill=DARK, outline="")

        self._part("touchpad", self._rrect(405, 138, 595, 248, 18, fill=TOUCHPAD, outline=BODY_EDGE), TOUCHPAD)
        self.lightbars = [c.create_line(*self.p(x, 160, x, 232), width=max(2, int(4 * s)),
                                        capstyle="round", fill=ACCENT) for x in (398, 602)]

        for name, x in (("create", 382), ("options", 618)):
            self._part(name, self._rrect(x - 6, 152, x + 6, 182, 6, fill=PART, outline=""), PART)

        # D-pad
        for name, (x1, y1, x2, y2), (dx, dy) in (("up", (307, 198, 333, 228), (0, -1)),
                                                 ("down", (307, 254, 333, 284), (0, 1)),
                                                 ("left", (276, 228, 306, 254), (-1, 0)),
                                                 ("right", (334, 228, 364, 254), (1, 0))):
            self._part(name, self._rrect(x1, y1, x2, y2, 6, fill=PART, outline=""), PART)
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            tip = (mx + dx * 6, my + dy * 6)
            base = [(mx - dx * 4 + dy * 6, my - dy * 4 + dx * 6), (mx - dx * 4 - dy * 6, my - dy * 4 - dx * 6)]
            c.create_polygon(*self.p(*tip, *base[0], *base[1]), fill="#c8cdd8", outline="", tags="glyph")

        # Face buttons with their symbols
        for name, (cx, cy) in (("triangle", (680, 200)), ("circle", (720, 241)),
                               ("cross", (680, 282)), ("square", (640, 241))):
            self._part(name, self._circle(cx, cy, 18, fill=PART, outline=""), PART)
            col, w = SYMBOL_COLORS[name], max(1, int(2 * s))
            if name == "triangle":
                c.create_polygon(*self.p(cx, cy - 9, cx + 9, cy + 6, cx - 9, cy + 6), fill="", outline=col, width=w)
            elif name == "circle":
                self._circle(cx, cy, 8, outline=col, width=w)
            elif name == "cross":
                c.create_line(*self.p(cx - 7, cy - 7, cx + 7, cy + 7), fill=col, width=w)
                c.create_line(*self.p(cx - 7, cy + 7, cx + 7, cy - 7), fill=col, width=w)
            else:
                c.create_rectangle(*self.p(cx - 7, cy - 7, cx + 7, cy + 7), outline=col, width=w)

        # Sticks: the cap moves with the real stick
        self.caps = {}
        for name, cx in (("lstick", 420), ("rstick", 580)):
            self._circle(cx, 322, 37, fill="#0b0c10", outline="")
            cap = self._part(name, self._circle(cx, 322, 25, fill=PART, outline="#4a505e", width=max(1, int(2 * s))), PART)
            ring = self._circle(cx, 322, 16, outline="#4a505e")
            self.caps[name] = (cap, ring, cx, 322)

        self._part("ps", self._circle(500, 322, 12, fill=PART, outline=""), PART)
        c.create_text(*self.p(500, 322), text="PS", fill="#c8cdd8", font=(FONT, 7, "bold"), tags="glyph")
        self._rrect(489, 350, 511, 357, 3, fill=PART, outline="")  # mute button (unused)

    # ---- callouts -----------------------------------------------------------
    def _callout(self, name, chip_box, text_xy, text_anchor, line_from):
        c, s = self.canvas, self.s
        ax, ay = ANCHORS[name]
        c.create_line(*self.p(*line_from, ax, ay), fill=LINE, width=max(1, int(s)))
        self._circle(ax, ay, 3, fill=LINE, outline="")
        x1, y1, x2, y2 = chip_box
        chip = self._rrect(x1, y1, x2, y2, 8, fill=PANEL, outline=LINE)
        chip_text = c.create_text(*self.p((x1 + x2) / 2, (y1 + y2) / 2), text=CHIPS[name], fill=TEXT,
                                  font=(FONT, 11 if len(CHIPS[name]) == 1 else 8, "bold"))
        action = c.create_text(*self.p(*text_xy), text="", anchor=text_anchor, fill=TEXT, font=(FONT, 10))
        self.callouts[name] = (chip, chip_text, action)

    def _draw_callouts(self):
        for i, (left, right) in enumerate(zip(LEFT, RIGHT)):
            y = 80 + i * 52
            self._callout(left, (196, y - 14, 258, y + 14), (186, y), "e", (258, y))
            self._callout(right, (742, y - 14, 804, y + 14), (814, y), "w", (742, y))
        self._callout("touchpad", (456, 12, 544, 38), (554, 25), "w", (500, 38))
        self._callout("ps", (472, 548, 528, 574), (538, 561), "w", (500, 548))
        self.canvas.tag_raise("glyph")  # keep button symbols above the label lines

    # ---- state --------------------------------------------------------------
    def view(self):
        return "keyboard" if self.keyboard_open or self.preview_keyboard else self.mode

    def _toggle_preview(self):
        self.preview_keyboard = not self.preview_keyboard
        self._refresh_view()

    def _refresh_view(self):
        view = self.view()
        actions = ACTIONS[view]
        color = MODE_COLORS[view]
        for name, (chip, chip_text, action) in self.callouts.items():
            text = actions.get(name)
            self.canvas.itemconfigure(action, text=text or "Not used", fill=TEXT if text else TEXT_OFF)
            self.canvas.itemconfigure(chip_text, fill=TEXT if text else TEXT_OFF)
        for bar in self.lightbars:
            self.canvas.itemconfigure(bar, fill=color)
        for mode, b in self.mode_buttons.items():
            active = mode == self.mode
            b.configure(bg=MODE_COLORS[mode] if active else PANEL, fg="#ffffff" if active else TEXT_DIM,
                        font=(FONT, 10, "bold" if active else "normal"))
        self.kb_button.configure(bg=MODE_COLORS["keyboard"] if view == "keyboard" else PANEL,
                                 fg="#111111" if view == "keyboard" else TEXT_DIM)
        title = MODE_NAMES[view] + (" (preview)" if self.preview_keyboard and not self.keyboard_open else "")
        desc = MODE_DESCRIPTIONS[view]
        if self.paused:
            desc = "PAUSED: the controller does nothing until you press Options or click Resume."
        self.description.configure(text=f"{title}: {desc}", fg="#f5a524" if self.paused else TEXT_DIM)
        self.pause_button.configure(text="Resume" if self.paused else "Pause",
                                    bg="#f5a524" if self.paused else PANEL,
                                    fg="#111111" if self.paused else TEXT_DIM)
        self._paint_pressed(set(self.pressed), force=True)

    def set_mode(self, mode):
        self.mode = mode
        self._refresh_view()

    def set_keyboard_open(self, is_open):
        if is_open != self.keyboard_open:
            self.keyboard_open = is_open
            self._refresh_view()

    def set_paused(self, paused):
        self.paused = paused
        self._refresh_view()

    def set_connection(self, name, battery=None):
        if name:
            extra = f"  ·  Battery: {battery}" if battery and battery != "unknown" else ""
            self.status.configure(text=f"●  {name}{extra}", fg="#3ddc97")
        else:
            self.status.configure(text="●  Waiting for controller (USB or Bluetooth)", fg="#ff5b6e")

    def log(self, message):
        self.message.configure(text=message)

    # ---- live input ---------------------------------------------------------
    def update_input(self, buttons, axes):
        """buttons: name -> bool. axes: lx, ly, rx, ry (-1..1), l2, r2 (0..1)."""
        pressed = {n for n, down in buttons.items() if down}
        if abs(axes["lx"]) > 0.2 or abs(axes["ly"]) > 0.2:
            pressed.add("lstick")
        if abs(axes["rx"]) > 0.2 or abs(axes["ry"]) > 0.2:
            pressed.add("rstick")
        self._paint_pressed(pressed)

        for name, (sx, sy) in (("lstick", ("lx", "ly")), ("rstick", ("rx", "ry"))):
            cap, ring, cx, cy = self.caps[name]
            dx, dy = axes[sx] * STICK_TRAVEL, axes[sy] * STICK_TRAVEL
            self.canvas.coords(cap, *self.p(cx + dx - 25, cy + dy - 25, cx + dx + 25, cy + dy + 25))
            self.canvas.coords(ring, *self.p(cx + dx - 16, cy + dy - 16, cx + dx + 16, cy + dy + 16))
        for side in ("l2", "r2"):
            item, x1, x2 = getattr(self, f"{side}_fill")
            top = 112 - 30 * max(0.0, axes[side])
            self.canvas.coords(item, *self.p(x1, top, x2, 112))

    def _paint_pressed(self, pressed, force=False):
        if pressed == self.pressed and not force:
            return
        self.pressed = pressed
        lit = set(pressed)  # clicking a stick lights up the stick itself too
        if "l3" in lit:
            lit.add("lstick")
        if "r3" in lit:
            lit.add("rstick")
        for name, items in self.parts.items():
            for item, fill in items:
                self.canvas.itemconfigure(item, fill=ACCENT if name in lit else fill)
        for name, (chip, _, _) in self.callouts.items():
            on = name in pressed
            self.canvas.itemconfigure(chip, fill=ACCENT if on else PANEL, outline=ACCENT if on else LINE)
