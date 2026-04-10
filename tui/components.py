from textual.app import ComposeResult
from textual.binding import Binding
from textual.events import Key, MouseDown
from textual.widgets import Label, Input, Button, ProgressBar
from textual.screen import ModalScreen
from textual.containers import Vertical

class AppInput(Input):
    """A custom Input that uses Windows-like bindings for Select All."""
    BINDINGS = [
        Binding("ctrl+a", "select_all", "Select All", show=False),
    ]

class NotificationModal(ModalScreen):
    def __init__(self, message: str = "", show_progress: bool = False):
        super().__init__()
        self.message = message
        self.show_progress = show_progress

    def compose(self) -> ComposeResult:
        with Vertical(id="notification-modal", classes="modal-container"):
            yield Label(self.message, id="notification-message")
            if self.show_progress:
                # Provide a total so that it functions as a 0-100% bar
                yield ProgressBar(total=100, show_percentage=True, id="modal-progress-bar")
            yield Button("Close", id="close-modal-btn", variant="primary")

    def update_message(self, message: str):
        self.query_one("#notification-message", Label).update(message)
        
    def update_progress(self, current: int, total: int = 100):
        if self.progress_bar:
            self.progress_bar.total = total
            self.progress_bar.progress = current

    @property
    def progress_bar(self):
        try:
            return self.query_one("#modal-progress-bar", ProgressBar)
        except Exception:
            return None

    def on_key(self, event: Key) -> None:
        if event.key:
            self.app.pop_screen()

    def on_mouse_down(self, event: MouseDown) -> None:
         if event.button:
            self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-modal-btn":
            self.app.pop_screen()