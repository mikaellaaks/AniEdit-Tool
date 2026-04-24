import re
import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Footer, Header, Input, Button
from textual.containers import Vertical
from textual import events, work

from src.downloader import download_pipeline
from tui.components import AppInput, NotificationModal
from tui.utils import remove_file, validate_input, load_settings

root = tk.Tk()
root.withdraw()

class DownloadScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Vertical(
            Label("Download Anime Clip", id="download-title"),
            AppInput(placeholder="Enter Anikai URL", id="url-input"),
            AppInput(placeholder="Enter output filename", id="filename"),
            AppInput(placeholder="Start Time (optional, e.g. 01:20)", id="start-time-input"),
            AppInput(placeholder="End Time (optional, e.g. 02:30)", id="end-time-input"),
            Button("Start Download", id="start-download-btn", variant="primary"),
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

    def show_notification(self, message: str, show_progress: bool = False, on_cancel=None):
        modal = NotificationModal(message, show_progress, on_cancel)
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

        is_valid, error_msg = validate_input(url, output_file, start_time, end_time)
        if not is_valid:
            self.show_notification(error_msg, show_progress=False)
            return
            
        cancel_event = threading.Event()
        def handle_cancel():
            cancel_event.set()
            
        temp_path = os.path.join(os.getcwd(), f"{output_file}.mp4")
        modal = self.show_notification("Fetching video...", show_progress=True, on_cancel=handle_cancel)
        self.perform_download(url, temp_path, start_time, end_time, output_file, modal, cancel_event)

    @work(thread=True)
    def perform_download(self, url, temp_path, start_time, end_time, output_file, modal, cancel_event):
        """Run the download pipeline in a background thread."""
        
        is_downloading = [False]
        
        # A simple callback function you can pass into download_pipeline.
        # This will be securely routed back to the main UI thread to update the ProgressBar.
        def _on_progress(current: int, total: int = 100):
            if not cancel_event.is_set():
                if not is_downloading[0]:
                    is_downloading[0] = True
                    self.app.call_from_thread(modal.update_message, "Downloading video...")
                self.app.call_from_thread(modal.update_progress, current, total)
        
        has_downloaded = download_pipeline(url, temp_path, start_time, end_time, progress_callback=_on_progress, cancel_event=cancel_event)
        
        # When done, call a UI-updating function back on the main thread
        self.app.call_from_thread(self._finish_download, has_downloaded, temp_path, output_file, modal, cancel_event.is_set())

    def _prompt_save_location(self, default_filename: str) -> str:
        """Prompt user for the final save location."""
        return filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
            initialfile=default_filename
        )

    def _finish_download(self, has_downloaded: bool, temp_path: str, output_file: str, modal: NotificationModal, is_cancelled: bool = False):
        """Handle the end of the download, update UI and move file."""
        if is_cancelled:
            # Clean up the partial/temporary file if it was aborted
            remove_file(temp_path)
            return
            
        if modal.progress_bar:
            modal.progress_bar.display = False
            
        if has_downloaded:
            settings = load_settings()
            always_use_folder = settings.get("always_use_default_folder", False)
            default_dir = settings.get("default_folder", "")
            
            save_path = None
            if always_use_folder and default_dir and os.path.exists(default_dir):
                save_path = os.path.join(default_dir, f"{output_file}.mp4")
            else:
                modal.update_message("Download complete! Select save location...")
                save_path = self._prompt_save_location(f"{output_file}.mp4")
            
            if save_path:
                shutil.move(temp_path, save_path)
                modal.update_message(f"File saved successfully to:\n{save_path}")
                modal.update_button_text("Close")

            else:
                remove_file(temp_path)
                modal.update_message("Save cancelled.")
                modal.update_button_text("Close")

        else:
            modal.update_message("Error: Download failed! Invalid URL or failed to fetch.")
            modal.update_button_text("Close")

    def on_key(self, event) -> None:
        if event.key == "enter":
            self._handle_start_download()