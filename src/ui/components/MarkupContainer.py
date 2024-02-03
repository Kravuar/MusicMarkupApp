from typing import Iterable, Callable, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton)

from src.app.markup_data import MarkupValue
from src.ui.components.RangeSlider import LabeledRangeSlider


class MarkupHistoryWidget(QWidget):
    delete_signal = Signal(QWidget)

    def __init__(self, markup: MarkupValue, time_label_mapper: Callable[[int], str], entry_duration: Optional[int], parent: Optional[QWidget] = None):
        super().__init__(parent)

        vertical_layout = QVBoxLayout(self)

        # Header
        horizontal_layout = QHBoxLayout(self)
        vertical_layout.addLayout(horizontal_layout)

        # Slider
        self._slider = LabeledRangeSlider(time_label_mapper, parent=self)
        if entry_duration is not None:
            self._slider.set_range_limit(0, entry_duration)
        else:
            self._slider.set_range_limit(markup.start, markup.end)
        self._slider.set_range(markup.start, markup.end)
        self._slider.set_min_border_visible(False)
        self._slider.set_max_border_visible(False)
        self._slider.set_readonly(True)
        self._slider.setEnabled(False)
        horizontal_layout.addWidget(self._slider)

        # Delete Button
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.delete_signal.emit(self))
        horizontal_layout.addWidget(delete_button)

        # Text area
        text_area = QTextEdit(markup.description, self)
        text_area.setReadOnly(True)
        vertical_layout.addWidget(text_area)

    def update_with_duration(self, entry_duration: int):
        self._slider.set_range_limit(0, entry_duration)


class MarkupContainerWidget(QWidget):
    delete_signal = Signal(int)

    def __init__(self, time_label_mapper: Callable[[int], str], parent: QWidget = None):
        super().__init__(parent)

        # State
        self._time_label_mapper = time_label_mapper

        # Layout
        self._container_layout = QVBoxLayout(self)
        self.setLayout(self._container_layout)

    def set_markups(self, markups: Iterable[MarkupValue], entry_duration: Optional[int] = None):
        for i in reversed(range(self._container_layout.count())):
            self._container_layout.itemAt(i).widget().setParent(None)

        for i, markup in enumerate(markups):
            self.add_markup(markup, entry_duration)

    def add_markup(self, markup: MarkupValue, entry_duration: Optional[int], index: Optional[int] = None):
        if index is None:
            index = self._container_layout.count()

        markup_widget = MarkupHistoryWidget(markup, self._time_label_mapper, entry_duration, self)
        markup_widget.delete_signal.connect(self._delete_markup)

        self._container_layout.insertWidget(index, markup_widget)

    def update_markups_with_duration(self, entry_duration: int):
        for i in range(self._container_layout.count()):
            widget = self._container_layout.itemAt(i).widget()
            if isinstance(widget, MarkupHistoryWidget):
                widget.update_with_duration(entry_duration)

    def _delete_markup(self, markup: MarkupHistoryWidget):
        self.delete_signal.emit(self._container_layout.indexOf(markup))
        markup.setParent(None)
