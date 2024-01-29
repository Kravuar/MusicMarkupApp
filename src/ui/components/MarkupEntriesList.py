from typing import Iterable

from PySide6.QtCore import Signal
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem

from src.app.markup_data import MarkupView


class MarkupEntriesWidget(QWidget):
    itemSelected = Signal(str)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        _layout = QVBoxLayout(self)
        self._list_widget = QListWidget(self)
        self._list_widget.itemDoubleClicked.connect(self._handle_item_click)
        _layout.addWidget(self._list_widget)

    def _handle_item_click(self, item: QListWidgetItem):
        md5 = item.data(Qt.ItemDataRole.UserRole)
        self.itemSelected.emit(md5)

    def set_entries(self, entries: Iterable[MarkupView]):
        self._list_widget.clear()
        for view in entries:
            label = f'{str(view.entry.entry_info.relative_path)} --- Labels: {len(view.entry.values)}'
            item = QListWidgetItem(label, self._list_widget)
            item.setData(Qt.ItemDataRole.UserRole, view.md5)
            if view.entry.entry_info.is_corrupted:
                item.setForeground(Qt.GlobalColor.red)