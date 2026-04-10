from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer
from textual.binding import Binding
from textual import events

class SettingScreen(Screen):

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(key="b", action="back", description="Go back"),
        Binding(key="s", action="", show=False)
    ]

    def compose(self) -> ComposeResult:
        yield Footer()

    def on_key(self, event: events.Key) -> None:

        if event.key == "b":
            self.app.pop_screen()