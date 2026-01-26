# utils/hotkey.py

try:
    from pynput import keyboard
except Exception:
    keyboard = None


class GlobalHotkey:
    def __init__(self, callback):
        self.callback = callback
        self.listener = None

        if keyboard:
            self.listener = keyboard.GlobalHotKeys({
                "<ctrl>+<alt>+v": self.callback
            })

    def start(self):
        if self.listener:
            self.listener.start()
