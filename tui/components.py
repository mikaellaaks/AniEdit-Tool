from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Label, Input, Button, ProgressBar
from textual.screen import ModalScreen
from textual.containers import Vertical

class AppInput(Input):
    """A custom Input that uses Windows-like bindings for Select All."""
    BINDINGS = [
        Binding("ctrl+a", "select_all", "Select All", show=False),
    ]

class NotificationModal(ModalScreen):
    def __init__(self, message: str = "", show_progress: bool = False, on_cancel=None):
        super().__init__()
        self.message = message
        self.show_progress = show_progress
        self.on_cancel = on_cancel

    def compose(self) -> ComposeResult:
        with Vertical(id="notification-modal", classes="modal-container"):
            yield Label(self.message, id="notification-message")
            if self.show_progress:
                # Provide a total so that it functions as a 0-100% bar
                yield ProgressBar(total=100, show_percentage=True, show_eta=False, id="modal-progress-bar")
            button_label = "Cancel" if self.show_progress else "Close"
            yield Button(button_label, id="close-modal-btn", variant="primary")

    def update_message(self, message: str):
        self.query_one("#notification-message", Label).update(message)

    def update_button_text(self, text: str):
        self.query_one("#close-modal-btn", Button).label = text
        
    def update_progress(self, current: int, total: int = 100):
        if self.progress_bar:
            # Only update total if it changes, otherwise it resets the ETA timer!
            if self.progress_bar.total != total:
                self.progress_bar.total = total
            self.progress_bar.progress = current

    @property
    def progress_bar(self):
        try:
            return self.query_one("#modal-progress-bar", ProgressBar)
        except Exception:
            return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-modal-btn":
            if self.on_cancel:
                self.on_cancel()
            self.app.pop_screen()