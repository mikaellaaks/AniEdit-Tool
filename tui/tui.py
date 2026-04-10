"""
An App to show the current time.
"""
from textual.app import App
from textual.binding import Binding
from textual import events

from tui.screens.download import DownloadScreen
from tui.screens.settings import SettingScreen
from tui.screens.welcome import WelcomeScreen
from tui.utils import load_settings

# Main App
class AniEdit(App):
    CSS_PATH = "aniedit.tcss"
    ENABLE_COMMAND_PALETTE = False
    AUTO_FOCUS = None
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(key="s", action="settings", description="Open settings"),
        Binding(key="h", action="help", description="Help")
    ]

    def on_mount(self) -> None:
        # Load the base screen
        self.push_screen(DownloadScreen())

        settings = load_settings()
        if settings.get("show_welcome", True):
            self.push_screen(WelcomeScreen())

    def on_key(self, event: events.Key) -> None:
        if event.key == "s" and not isinstance(self.screen, SettingScreen):
            self.push_screen(SettingScreen())

        elif event.key == "h" and not isinstance(self.screen, WelcomeScreen):
            self.push_screen(WelcomeScreen())