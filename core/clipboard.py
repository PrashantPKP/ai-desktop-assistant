import time

import keyboard
import pyperclip


class ClipboardManager:
    def __init__(self):
        self.previous_clipboard = ""

    def get_selected_text(self):
        """
        Copies selected text without permanently changing
        the user's clipboard.
        """

        try:
            # Save current clipboard
            self.previous_clipboard = pyperclip.paste()

            # Clear clipboard
            pyperclip.copy("")

            # Copy selected text
            keyboard.send("ctrl+c")

            # Wait for clipboard to update
            time.sleep(0.15)

            selected_text = pyperclip.paste()

            # Restore previous clipboard
            pyperclip.copy(self.previous_clipboard)

            return selected_text.strip()

        except Exception:
            return ""

    def copy_to_clipboard(self, text):
        """
        Copy AI response to clipboard.
        """
        pyperclip.copy(text)