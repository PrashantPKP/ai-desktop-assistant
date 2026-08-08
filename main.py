import sys
from pathlib import Path

# Ensure project root is in Python path
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ui.main_window import MainWindow
from core.shortcut_manager import ShortcutManager
from core.tray_manager import TrayManager


def main():
    app = MainWindow()

    # Global hotkey: Ctrl+Shift+A
    shortcut = ShortcutManager()
    shortcut.set_callback(app.shortcut_pressed)
    shortcut.start()

    # System tray icon
    tray = TrayManager(
        on_show=lambda: app.root.after(0, app.show_window),
        on_quit=lambda: app.root.after(0, app.close)
    )
    tray.start()

    # Run the app
    app.run()

    # Cleanup
    shortcut.stop()
    tray.stop()


if __name__ == "__main__":
    main()