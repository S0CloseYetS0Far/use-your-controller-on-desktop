"""Detect when a text box (search bar, address bar, comment box...) has keyboard focus.

Uses Windows UI Automation on a background thread so a slow browser never
stalls the controller loop. Needs the `comtypes` package; without it the
watcher simply reports "no text box" and the keyboard only opens manually.
"""

import os
import threading
import time

UIA_EDIT = 50004
UIA_COMBOBOX = 50003   # Google's search box is an editable combobox
UIA_VALUE_PATTERN = 10002
UIA_IS_TEXT_PATTERN_AVAILABLE = 30040
POLL_SECONDS = 0.2


class FocusWatcher:
    def __init__(self):
        self.active = False          # only poll while someone cares
        self.text_focused = False
        self.focus_id = None         # changes whenever focus moves to another element
        self.last_text_time = 0.0
        self.available = True
        self._stop = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop = True

    def _run(self):
        try:
            import sys
            # comtypes initializes COM for the importing thread (this one) on import;
            # UI Automation clients should run multithreaded.
            sys.coinit_flags = 0  # COINIT_MULTITHREADED
            import comtypes.client
            comtypes.client.GetModule("UIAutomationCore.dll")
            from comtypes.gen import UIAutomationClient as uia_mod
            uia = comtypes.client.CreateObject(uia_mod.CUIAutomation,
                                               interface=uia_mod.IUIAutomation)
        except Exception as exc:  # comtypes missing or UIA unavailable
            self.available = False
            print(f"[keyboard] Automatic pop-up disabled ({exc}). "
                  "Use the touchpad button to open the keyboard.")
            return

        own_pid = os.getpid()
        while not self._stop:
            if not self.active:
                self.text_focused = False
                time.sleep(POLL_SECONDS)
                continue
            try:
                el = uia.GetFocusedElement()
                is_text = el.CurrentProcessId != own_pid and _is_text_input(el, uia_mod)
                self.focus_id = tuple(el.GetRuntimeId() or ())
                self.text_focused = is_text
                if is_text:
                    self.last_text_time = time.perf_counter()
            except Exception:
                self.text_focused = False
            time.sleep(POLL_SECONDS)


def _is_text_input(el, uia_mod):
    control_type = el.CurrentControlType
    if control_type not in (UIA_EDIT, UIA_COMBOBOX):
        return False
    # A dropdown (<select>) is also a combobox; only editable ones expose text.
    if control_type == UIA_COMBOBOX and not el.GetCurrentPropertyValue(UIA_IS_TEXT_PATTERN_AVAILABLE):
        return False
    try:
        pattern = el.GetCurrentPattern(UIA_VALUE_PATTERN)
        if pattern:
            value = pattern.QueryInterface(uia_mod.IUIAutomationValuePattern)
            return not value.CurrentIsReadOnly
    except Exception:
        pass
    # An Edit without a Value pattern is still something you can type into.
    return control_type == UIA_EDIT
