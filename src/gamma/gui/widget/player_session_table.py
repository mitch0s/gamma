import time
import logging
from textual.widget import Widget
from textual.widgets import DataTable
from textual.errors import *
import gamma.common
from datetime import datetime

logger = logging.getLogger()

class PlayerSessionTable(Widget):
    def __init__(self, *children, name=None, id=None, classes=None, disabled=False, markup=True):
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled, markup=markup)
        self._columns = ('ID', 'Connected (UTC)', 'Username', 'Hostname', 'Duration (s)', 'Bandwidth (MB)')
        self._col_keys = []
        self.table = DataTable(cursor_type='row')

    def compose(self):
        yield self.table

    def on_mount(self):
        self._col_keys = self.table.add_columns(*self._columns)
        self.set_interval(0.1, self.refresh_table)

    def refresh_table(self):
        for conn in gamma.common.connections:
            row_key = str(conn.id)
            # try: self.table.remove_row(row_key)
            # except: continue
            
            try: self.table.get_row(row_key)
            except: self.table.add_row(*[None for i in range(len(self._columns))], key=row_key)
            
            bandwidth_mb = conn.total_bytes / 1_000_000
            self.table.update_cell(row_key, self._col_keys[0], conn.id)
            self.table.update_cell(row_key, self._col_keys[1], datetime.fromtimestamp(conn.created_ts))
            self.table.update_cell(row_key, self._col_keys[2], conn.downstream.username)
            self.table.update_cell(row_key, self._col_keys[3], conn.downstream.hostname)
            self.table.update_cell(row_key, self._col_keys[4], int(time.time()-conn.created_ts))
            self.table.update_cell(row_key, self._col_keys[5], f"{bandwidth_mb:.3f}")
