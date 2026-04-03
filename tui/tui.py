"""
An App to show the current time.
"""
import re
import os
import shutil
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Label, Footer, Header, Input, Button, ProgressBar
from textual.screen import Screen, ModalScreen
from textual.containers import Vertical, Horizontal
from textual import events
from textual import work
import tkinter as tk
from tkinter import filedialog
from src.downloader import download_pipeline

root = tk.Tk()
root.withdraw()

class AppInput(Input):
    """A custom Input that uses Windows-like bindings for Select All."""
    BINDINGS = [
        Binding("ctrl+a", "select_all", "Select All", show=False),
    ]

# Notification Modal
class NotificationModal(ModalScreen):
    def __init__(self, message: str = "", show_progress: bool = False):
        super().__init__()
        self.message = message
        self.show_progress = show_progress

    def compose(self) -> ComposeResult:
        with Vertical(id="notification-modal", classes="modal-container"):
            yield Label(self.message, id="notification-message")
            if self.show_progress:
                # total=None makes it an indeterminate progress bar
                yield ProgressBar(total=None, show_percentage=False, id="modal-progress-bar")
            yield Button("Close", id="close-modal-btn", variant="primary")

    def update_message(self, message: str):
        self.query_one("#notification-message", Label).update(message)

    @property
    def progress_bar(self):
        try:
            return self.query_one("#modal-progress-bar", ProgressBar)
        except Exception:
            return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-modal-btn":
            self.app.pop_screen()

# Download Screen
class DownloadScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Vertical(
            Label("Download Anime Clip", id="download-title"),
            AppInput(placeholder="Enter Aniwatch URL", id="url-input"),
            AppInput(placeholder="Enter output filename", id="filename"),
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

    def show_notification(self, message: str, show_progress: bool = False):
        modal = NotificationModal(message, show_progress)
        self.app.push_screen(modal)
        return modal

    def _get_input_values(self):
        """Retrieve values from UI input fields."""
        url = self.query_one("#url-input", Input).value
        output_file = self.query_one("#filename", Input).value
        start_time = self.query_one("#start-time-input", Input).value
        end_time = self.query_one("#end-time-input", Input).value
        return url, output_file, start_time, end_time

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start-download-btn":
            self._handle_start_download()

    def _handle_start_download(self) -> None:
        """Process the download initiation step."""
        url, output_file, start_time, end_time = self._get_input_values()

        if not output_file:
            self.show_notification("Output filename required!", show_progress=False)
            return
            
        temp_path = os.path.join(os.getcwd(), f"{output_file}.mp4")

        if self.is_valid_input(url, temp_path, start_time, end_time):
            modal = self.show_notification("Download started...", show_progress=True)
            self.perform_download(url, temp_path, start_time, end_time, output_file, modal)
        else:
            self.show_notification("Invalid Input!", show_progress=False)

    @work(thread=True)
    def perform_download(self, url, temp_path, start_time, end_time, output_file, modal):
        """Run the actual blocking download pipeline in a background thread."""
        has_downloaded = download_pipeline(url, temp_path, start_time, end_time)
        
        # When done, safely call a UI-updating function back on the main thread
        self.app.call_from_thread(self._finish_download, has_downloaded, temp_path, output_file, modal)

    def _prompt_save_location(self, default_filename: str) -> str:
        """Prompt user for the final save location."""
        return filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
            initialfile=default_filename
        )

    def _finish_download(self, has_downloaded: bool, temp_path: str, output_file: str, modal: NotificationModal):
        """Handle the end of the download, update UI and move file."""
        if modal.progress_bar:
            modal.progress_bar.display = False
            
        if has_downloaded:
            modal.update_message("Download complete! Select save location...")
            save_path = self._prompt_save_location(f"{output_file}.mp4")
            
            if save_path:
                shutil.move(temp_path, save_path)
                modal.update_message(f"File saved successfully to:\n{save_path}")
            else:
                modal.update_message("Save cancelled. File is in the temp folder.")
        else:
            modal.update_message("Error: Download failed!")

    def on_key(self, event) -> None:
        match event.key:
            case "enter":
                self.query_one("#progress-label", Label).update("Download started...")

        
    def is_valid_input(self, url, output_path, start_time=None, end_time=None):
        
        # Basic URL validation: must start with http:// or https://
        if not url or not output_path:
            return False
        if not (url.startswith("http://") or url.startswith("https://")):
            return False

        # Time validation: allow empty or mm:ss (e.g., 01:30)
        time_pattern = re.compile(r"^(?:[0-5]?\d:[0-5]\d)?$")
        for t in (start_time, end_time):
            if t and not time_pattern.match(t):
                return False

        return True
        

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