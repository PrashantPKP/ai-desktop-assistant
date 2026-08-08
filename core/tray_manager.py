import threading
from PIL import Image, ImageDraw
import pystray


class TrayManager:
    """
    System tray icon manager.
    Provides Show/Quit menu when the window is minimized.
    """

    def __init__(self, on_show, on_quit):
        self.on_show = on_show
        self.on_quit = on_quit
        self.icon = None

    def _create_icon_image(self):
        """
        Generate a simple AI-themed tray icon programmatically.
        A circular gradient icon with an 'AI' text effect.
        """

        size = 64
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Outer circle — dark blue
        draw.ellipse(
            [2, 2, size - 2, size - 2],
            fill=(30, 90, 200),
            outline=(20, 70, 170),
            width=2
        )

        # Inner circle — lighter accent
        draw.ellipse(
            [14, 14, size - 14, size - 14],
            fill=(60, 140, 255)
        )

        # Center dot
        draw.ellipse(
            [26, 26, size - 26, size - 26],
            fill=(255, 255, 255)
        )

        return image

    def _build_menu(self):
        return pystray.Menu(
            pystray.MenuItem(
                "Show Assistant",
                self._on_show_click,
                default=True
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Quit",
                self._on_quit_click
            )
        )

    def _on_show_click(self, icon, item):
        if self.on_show:
            self.on_show()

    def _on_quit_click(self, icon, item):
        self.stop()
        if self.on_quit:
            self.on_quit()

    def start(self):
        """Start the system tray icon in a background thread."""

        self.icon = pystray.Icon(
            name="AI Assistant",
            icon=self._create_icon_image(),
            title="AI Desktop Assistant",
            menu=self._build_menu()
        )

        threading.Thread(
            target=self.icon.run,
            daemon=True
        ).start()

    def stop(self):
        """Remove the tray icon."""
        if self.icon:
            self.icon.stop()
