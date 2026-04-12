from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Digits
from textual.containers import Vertical

from .widget.event_log import EventLog
from .widget.player_session_table import PlayerSessionTable


class GammaTerminal(App):
    CSS = """
    Vertical {
        height: 100%;
    }

    EventLog {
        height: 1fr;
    }

    PlayerSessionTable {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            PlayerSessionTable(),
            EventLog()
        )
        # yield PlayerSessionTable()

    def on_ready(self) -> None:
        pass