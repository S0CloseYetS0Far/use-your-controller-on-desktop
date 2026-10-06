"""Send mouse and keyboard input on Windows through the SendInput API."""

import ctypes
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)

INPUT_MOUSE, INPUT_KEYBOARD = 0, 1

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0002, 0x0004
MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP = 0x0008, 0x0010
MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP = 0x0020, 0x0040
MOUSEEVENTF_XDOWN, MOUSEEVENTF_XUP = 0x0080, 0x0100
MOUSEEVENTF_WHEEL, MOUSEEVENTF_HWHEEL = 0x0800, 0x1000
KEYEVENTF_EXTENDEDKEY, KEYEVENTF_KEYUP, KEYEVENTF_UNICODE = 0x0001, 0x0002, 0x0004
WHEEL_DELTA = 120

VK_BACK, VK_TAB, VK_RETURN, VK_SHIFT, VK_CONTROL, VK_MENU = 0x08, 0x09, 0x0D, 0x10, 0x11, 0x12
VK_ESCAPE, VK_SPACE = 0x1B, 0x20
VK_LEFT, VK_UP, VK_RIGHT, VK_DOWN = 0x25, 0x26, 0x27, 0x28
VK_F5 = 0x74
VK_L, VK_M, VK_T, VK_W = 0x4C, 0x4D, 0x54, 0x57

# Keys that need the "extended" flag or Windows treats them as numpad keys.
_EXTENDED = {0x21, 0x22, 0x23, 0x24, VK_LEFT, VK_UP, VK_RIGHT, VK_DOWN, 0x2D, 0x2E}

# Mouse buttons: name -> (down flag, up flag, mouseData)
BUTTONS = {
    "left": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP, 0),
    "right": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP, 0),
    "middle": (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP, 0),
    "back": (MOUSEEVENTF_XDOWN, MOUSEEVENTF_XUP, 1),
    "forward": (MOUSEEVENTF_XDOWN, MOUSEEVENTF_XUP, 2),
}


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
    if vk in _EXTENDED:
        flags |= KEYEVENTF_EXTENDEDKEY
    return INPUT(type=INPUT_KEYBOARD, u=_INPUTUNION(ki=KEYBDINPUT(wVk=vk, dwFlags=flags)))


def _unicode(unit, up=False):
    flags = KEYEVENTF_UNICODE | (KEYEVENTF_KEYUP if up else 0)
    return INPUT(type=INPUT_KEYBOARD, u=_INPUTUNION(ki=KEYBDINPUT(wScan=unit, dwFlags=flags)))


# ------------------------------------------------------------------ mouse ---
def move_mouse(dx, dy):
    _send(_mouse(MOUSEEVENTF_MOVE, dx, dy))


def wheel(delta):
    """Vertical scroll. 120 = one notch up, -120 = one notch down."""
    _send(_mouse(MOUSEEVENTF_WHEEL, data=delta))


def hwheel(delta):
    """Horizontal scroll. Positive = right."""
    _send(_mouse(MOUSEEVENTF_HWHEEL, data=delta))


def mouse_button(name, down):
    down_flag, up_flag, data = BUTTONS[name]
    _send(_mouse(down_flag if down else up_flag, data=data))


# --------------------------------------------------------------- keyboard ---
def tap(vk):
    _send(_key(vk), _key(vk, up=True))


def combo(*vks):
    """Press keys in order and release them in reverse, e.g. combo(VK_CONTROL, VK_T)."""
    _send(*[_key(vk) for vk in vks], *[_key(vk, up=True) for vk in reversed(vks)])


def type_text(text):
    """Type any Unicode text (Arabic, symbols, emoji...) regardless of keyboard layout."""
    raw = text.encode("utf-16-le")
    units = [int.from_bytes(raw[i:i + 2], "little") for i in range(0, len(raw), 2)]
    events = []
    for unit in units:
        events += [_unicode(unit), _unicode(unit, up=True)]
    if events:
        _send(*events)
