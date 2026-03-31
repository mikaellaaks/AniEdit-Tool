"""
An App to show the current time.
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Label, Footer, Header, Input, Button
from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual import events
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

class AppInput(Input):
    """A custom Input that uses Windows-like bindings for Select All."""
    BINDINGS = [
        Binding("ctrl+a", "select_all", "Select All", show=False),
    ]

# Download Screen
class DownloadScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Vertical(
            Label("Download Anime Clip", id="download-title"),
            AppInput(placeholder="Enter Aniwatch URL", id="url-input"),
            Horizontal(
                AppInput(placeholder="Output Path (e.g. ./downloads)", id="output-path-input"),
                Button("Browse", id="browse-btn"),
                id="output-row"
            ),
            AppInput(placeholder="Start Time (optional, e.g. 01:20)", id="start-time-input"),
            AppInput(placeholder="End Time (optional, e.g. 02:30)", id="end-time-input"),
            Button("Start Download", id="start-download-btn", variant="primary"),
            Label("[Download progress will appear here]", id="progress-label"),
            id="download-section"
        )
        yield Footer()

    def on_mount(self) -> None:
        # Prevent auto-focusing on the text inputs
        self.set_focus(None)

    def on_click(self, event: events.Click) -> None:
        # Clear focus if clicking outside of input boxes or buttons
        if not isinstance(event.widget, (Input, Button)):
            self.set_focus(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start-download-btn":
            self.query_one("#progress-label", Label).update("Download started...")
        elif event.button.id == "browse-btn":
            file_path = filedialog.askdirectory()
            if file_path:
                self.query_one("#output-path-input", Input).value = file_path

    def on_key(self, event) -> None:
        match event.key:
            case "enter":
                self.query_one("#progress-label", Label).update("Download started...")

# Main App
class AniEdit(App):
    CSS_PATH = "aniedit.tcss"
    ENABLE_COMMAND_PALETTE = False
    AUTO_FOCUS = None
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
    ]

    def on_mount(self) -> None:
        self.push_screen(DownloadScreen())

if __name__ == "__main__":
    app = AniEdit()
    app.run()