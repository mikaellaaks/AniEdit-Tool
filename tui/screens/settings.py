import tkinter as tk
from tkinter import filedialog
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, Button, Switch
from textual.containers import Vertical, Horizontal
from textual.binding import Binding
from textual import events

from tui.utils import load_settings, save_settings

root = tk.Tk()
root.withdraw()

class SettingScreen(Screen):

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(key="b", action="back", description="Go back"),
        Binding(key="s", action="", show=False)
    ]

    def on_mount(self) -> None:
        self.settings = load_settings()
        folder = self.settings.get("default_folder", "Not set")
        always_use = self.settings.get("always_use_default_folder", False)
        
        self.query_one("#default-folder-label", Label).update(folder)
        self.query_one("#always-use-switch", Switch).value = always_use

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="settings-main"):
            yield Label("AniEdit Settings", id="settings-title")
            
            with Vertical(classes="setting-item"):
                yield Label("• Default Download Folder")
                with Horizontal(classes="setting-row"):
                    yield Label("Not set", id="default-folder-label", classes="dim-text")
                    yield Button("Browse", id="browse-folder-btn", variant="primary")
            
            with Horizontal(classes="setting-item switch-row"):
                yield Label("• Automatically save to default folder without prompting")
                yield Switch(id="always-use-switch")
                
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "browse-folder-btn":
            self.select_default_folder()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id == "always-use-switch":
            self.settings["always_use_default_folder"] = event.value
            save_settings(self.settings)

    def on_key(self, event: events.Key) -> None:
        if event.key == "b":
            self.app.pop_screen()

    def select_default_folder(self):
        folder_path = filedialog.askdirectory(title="Select Default Download Folder")
        if folder_path:
            self.settings["default_folder"] = folder_path
            save_settings(self.settings)
            self.query_one("#default-folder-label", Label).update(folder_path)

