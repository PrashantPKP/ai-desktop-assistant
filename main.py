from ui.main_window import MainWindow
from core.shortcut_manager import ShortcutManager


def main():
    app = MainWindow()

    shortcut = ShortcutManager()
    shortcut.set_callback(app.shortcut_pressed)
    shortcut.start()

    app.run()


if __name__ == "__main__":
    main()