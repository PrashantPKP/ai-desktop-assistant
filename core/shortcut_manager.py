import threading
import keyboard
from core.settings_manager import SettingsManager


class ShortcutManager:
    def __init__(self):
        settings = SettingsManager()
        self.shortcut = settings.get("shortcut", "ctrl+shift+a")
        self.callback = None

    def set_callback(self, callback):
        self.callback = callback

    def start(self):
        keyboard.add_hotkey(
            self.shortcut,
            self._on_shortcut,
            suppress=True
        )

        threading.Thread(
            target=keyboard.wait,
            daemon=True
        ).start()

    def _on_shortcut(self):
        if self.callback:
            self.callback()

    def stop(self):
        keyboard.unhook_all_hotkeys()