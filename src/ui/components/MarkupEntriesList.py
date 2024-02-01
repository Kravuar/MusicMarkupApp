from typing import Iterable

from PySide6.QtCore import Signal
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QStyle

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
            item = QListWidgetItem(self._entry_to_label(view), self._list_widget)
            item.setData(Qt.ItemDataRole.UserRole, view.md5)
            if view.entry.entry_info.is_corrupted:
                item.setIcon(self.style().standardPixmap(QStyle.StandardPixmap.SP_MessageBoxCritical))

    def scroll_to(self, entry: MarkupView):
        items = self._list_widget.findItems(self._entry_to_label(entry), Qt.MatchFlag.MatchExactly)
        if len(items) == 1:
            item = items[0]
            self._list_widget.setCurrentItem(item)
            self._list_widget.scrollToItem(item)

    @staticmethod
    def _entry_to_label(view: MarkupView):
        return f'{str(view.entry.entry_info.relative_path)} --- Labels: {len(view.entry.values)}'
