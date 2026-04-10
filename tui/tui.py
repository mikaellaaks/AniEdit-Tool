"""
An App to show the current time.
"""
from textual.app import App
from textual.binding import Binding
from textual import events

from tui.screens.download import DownloadScreen
from tui.screens.settings import SettingScreen

# Main App
class AniEdit(App):
    CSS_PATH = "aniedit.tcss"
    ENABLE_COMMAND_PALETTE = False
    AUTO_FOCUS = None
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(key="s", action="settings", description="Open settings")
    ]

    def on_mount(self) -> None:
        self.push_screen(DownloadScreen())

    def on_key(self, event: events.Key) -> None:
        if event.key == "s":
            self.push_screen(SettingScreen())