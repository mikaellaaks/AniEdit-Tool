from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Button, Checkbox
from textual.containers import Vertical

from tui.utils import load_settings, save_settings

class WelcomeScreen(ModalScreen):
    """Initial Welcome & Instructions Screen for new users."""
    
    def compose(self) -> ComposeResult:
        settings = load_settings()
        show_checkbox = settings.get("show_welcome", True)

        with Vertical(id="welcome-modal", classes="modal-container"):
            yield Label("Welcome to AniEdit!", classes="title")
            yield Label(
                "How to use this app:\n\n"
                "1. Paste an Animekai video URL.\n"
                "2. Set an output filename.\n"
                "3. Optionally provide Start and End times to extract a clip.\n"
                "4. Click 'Start Download' and wait!\n\n"
                "The app will fetch the highest quality stream natively to your system.", 
                id="welcome-instructions"
            )
            
            if show_checkbox:
                yield Checkbox("Do not show this again", id="do-not-show-checkbox", value=False)
            
            yield Button("Got it!", id="close-welcome-btn", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-welcome-btn":
            try:
                checkbox = self.query_one("#do-not-show-checkbox", Checkbox)
                # If the user ticked the box, save this preference in settings.json
                if checkbox.value:
                    settings = load_settings()
                    settings["show_welcome"] = False
                    save_settings(settings)
            except Exception:
                # Checkbox not rendered because it was already dismissed previously
                pass
            
            # Close the welcome screen and return to the Download screen
            self.app.pop_screen()