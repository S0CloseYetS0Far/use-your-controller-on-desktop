"""What every controller button does in each mode, as shown in the control panel."""

COMMON = {
    "lstick": "Move cursor",
    "l2": "Slow cursor (hold)",
    "cross": "Left click",
    "circle": "Right click",
    "touchpad": "Open on-screen keyboard",
    "create": "Switch mode",
    "options": "Pause / resume",
    "ps": "Quit",
}

ACTIONS = {
    "standard": {
        **COMMON,
        "rstick": "Scroll",
        "l1": "Mouse back",
        "r1": "Mouse forward",
        "up": "Arrow up",
        "down": "Arrow down",
        "left": "Arrow left",
        "right": "Arrow right",
        "square": "Middle click",
        "triangle": "On-screen keyboard",
    },
    "tiktok": {
        **COMMON,
        "rstick": "Flick: next / previous video",
        "r3": "Play / pause",
        "l1": "Previous video",
        "r1": "Next video",
        "up": "Previous video",
        "down": "Next video",
        "triangle": "Like",
        "square": "Mute / unmute",
    },
    "browser": {
        **COMMON,
        "rstick": "Scroll page",
        "r3": "Middle click (new tab)",
        "l1": "Previous tab",
        "r1": "Next tab",
        "left": "Back",
        "right": "Forward",
        "up": "Reload",
        "down": "Close tab (hold)",
        "triangle": "Search / address bar",
        "square": "New tab",
    },
    "keyboard": {
        "lstick": "Move between keys",
        "up": "Move up",
        "down": "Move down",
        "left": "Move left",
        "right": "Move right",
        "cross": "Type key",
        "square": "Backspace",
        "triangle": "Space",
        "r2": "Enter",
        "l1": "Text cursor left",
        "r1": "Text cursor right",
        "l2": "Shift / caps lock",
        "l3": "Switch language",
        "circle": "Close keyboard",
        "touchpad": "Close keyboard",
        "create": "Switch mode",
        "options": "Pause / resume",
        "ps": "Quit",
    },
}

MODE_NAMES = {
    "standard": "Standard",
    "tiktok": "TikTok",
    "browser": "Browser",
    "keyboard": "On-screen keyboard",
}

MODE_DESCRIPTIONS = {
    "standard": "Use the controller as a normal mouse.",
    "tiktok": "Scroll TikTok videos. Keep the cursor over the video.",
    "browser": "Switch tabs and search. The keyboard pops up in text boxes.",
    "keyboard": "The on-screen keyboard is open. Text goes into the focused box.",
}
