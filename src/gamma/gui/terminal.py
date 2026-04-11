from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Digits

from .widget.event_log import EventLog


class GammaTerminal(App):
    CSS = """
    Screen { align: center middle; }
    Digits { width: auto; }
    """

    def compose(self) -> ComposeResult:
        yield EventLog()

    def on_ready(self) -> None:
        pass