from textual.widget import Widget
from textual.widgets import DataTable
from gamma.mixin.logger import CallbackHandler
from logging import LogRecord
import logging
from datetime import datetime

logger = logging.getLogger()

class EventLog(Widget):
    def __init__(self, *children, name=None, id=None, classes=None, disabled=False, markup=True):
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled, markup=markup)
        self._columns = ('Time (UTC)', 'Severity', 'Message')
        self.table = DataTable(cursor_type='row')
        CallbackHandler().bind(self.handle_log)

        self._log_queue:list[list[str]] = []

    def compose(self):
        yield self.table

    def on_mount(self):
        self.table.add_columns(*self._columns)
        self.set_interval(0.2, self.draw_queued_logs)

    def handle_log(self, record:LogRecord=None):
        row = [datetime.fromtimestamp(record.created), record.levelname, record.getMessage()]
        self._log_queue.append(row)

    def draw_queued_logs(self):
        for row in self._log_queue:
            self.table.add_row(*row)
        # self.table.scroll_end()
        self._log_queue = []
