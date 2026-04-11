from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Digits
from textual.containers import Horizontal

from .widget.event_log import EventLog
from .widget.player_session_table import PlayerSessionTable


class GammaTerminal(App):
    CSS = """
    Screen { align: center middle; }
    Digits { width: auto; }
    """

    def compose(self) -> ComposeResult:
        # yield Horizontal(
        #     EventLog(),
        #     PlayerSessionTable()
        # )
        yield PlayerSessionTable()

    def on_ready(self) -> None:
        pass