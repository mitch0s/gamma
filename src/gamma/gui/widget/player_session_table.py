import time
import logging
from datetime import datetime

from textual.widget import Widget
from textual.widgets import DataTable
from textual import events

import gamma.common

logger = logging.getLogger()


class PlayerSessionTable(Widget):
    def __init__(self, *children, name=None, id=None, classes=None, disabled=False, markup=True):
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled, markup=markup)

        self._columns = (
            "ID",
            "Connected (UTC)",
            "Username",
            "Type",
            "Hostname",
            "Duration (s)",
            "Bandwidth (MB)",
        )

        self._col_keys = []
        self.table = DataTable(cursor_type="row")


    def compose(self):
        yield self.table

    def on_mount(self):
        self._col_keys = self.table.add_columns(*self._columns)
        self.set_interval(0.1, self.refresh_table)

        # Ensure key events go to the table
        self.table.focus()

    def on_key(self, event: events.Key) -> None:
        if event.key != "k":
            return
        logger.info('K button pressed!')
        row_index = self.table.cursor_row
        if row_index is None:
            logger.info('Row index is None')
            return

        row_key = str(self.table.get_row_at(row_index)[0])

        for conn in gamma.common.connections:
            logger.info(conn.id)
            if str(conn.id) == str(row_key):
                self.run_worker(conn.downstream.close)
                logger.info(f'Kicked {conn.downstream.username} ({conn.downstream.host_addr}:{conn.downstream.host_port}) from {conn.downstream.hostname}')
                break

    def refresh_table(self):
        for conn in list(gamma.common.connections):
            row_key = str(conn.id)

            row_exists = True
            try:
                self.table.get_row(row_key)
            except Exception:
                row_exists = False

            # remove dead connections
            if not conn._connection_open:
                if row_exists:
                    self.table.remove_row(row_key)
                continue

            # add new connection row
            if not row_exists:
                self.table.add_row(
                    *([None] * len(self._columns)),
                    key=row_key,
                )

            # update active row
            bandwidth_mb = conn.total_bytes / 1_000_000

            self.table.update_cell(row_key, self._col_keys[0], conn.id)
            self.table.update_cell(row_key, self._col_keys[1], datetime.fromtimestamp(conn.created_ts))
            self.table.update_cell(row_key, self._col_keys[2], conn.downstream.username)
            if conn.downstream.type:
                self.table.update_cell(row_key, self._col_keys[3], conn.downstream.type.name)
            self.table.update_cell(row_key, self._col_keys[4], conn.downstream.hostname, update_width=True)
            self.table.update_cell(row_key, self._col_keys[5], int(time.time() - conn.created_ts))
            self.table.update_cell(row_key, self._col_keys[6], f"{bandwidth_mb:.3f}")