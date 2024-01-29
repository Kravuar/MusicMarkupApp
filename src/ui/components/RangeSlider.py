from typing import Callable

from PySide6.QtCore import QRect, QSize, Signal
from PySide6.QtGui import Qt, QPaintEvent, QPainter, QBrush, QPalette, QMouseEvent, QFontMetrics
from PySide6.QtWidgets import QWidget, QStyleOptionSlider, QSizePolicy, QStyle, QVBoxLayout, QLabel, \
    QHBoxLayout, QToolTip


class RangeSlider(QWidget):
    first_value_changed = Signal(int)
    second_value_changed = Signal(int)
    min_changed = Signal(int)
    max_changed = Signal(int)

    def __init__(self, readonly: bool = False, parent: QWidget = None):
        super().__init__(parent)

        self._readonly = readonly
        self._first_tooltip = None
        self._second_tooltip = None
        self._first_sc = None
        self._second_sc = None
        self._first_position = 0
        self._second_position = 0
        self._min_range = 0

        self.opt = QStyleOptionSlider()
        self.opt.minimum = 0
        self.opt.maximum = 0

        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed, QSizePolicy.Slider))

    def set_range_limit(self, minimum: int, maximum: int):
        if maximum >= minimum:
            self.opt.minimum = minimum
            self.min_changed.emit(minimum)
            self.opt.maximum = maximum
            self.max_changed.emit(maximum)
            self._min_range = min(self._min_range, self.opt.maximum - self.opt.minimum)

    def set_range(self, start: int, end: int):
        if end <= self.opt.maximum and start >= self.opt.minimum and end - start >= self._min_range:
            self._first_position = start
            self.first_value_changed.emit(start)
            self._second_position = end
            self.second_value_changed.emit(end)

    def get_range(self):
        return self._first_position, self._second_position

    def set_min_range(self, min_range_in_ms: int):
        if min_range_in_ms <= (self.opt.maximum - self.opt.minimum):
            self._min_range = min_range_in_ms

            expansion_needed = min_range_in_ms - (self._second_position - self._first_position)

            first_new_position = max(self._first_position - expansion_needed, self.opt.minimum)
            expansion_needed -= self._first_position - first_new_position
            second_new_position = min(self._second_position + expansion_needed, self.opt.maximum)

            self.set_range(first_new_position, second_new_position)

    def set_first_tooltip(self, tooltip: str):
        self._first_tooltip = tooltip

    def set_second_tooltip(self, tooltip: str):
        self._second_tooltip = tooltip

    def set_readonly(self, readonly: bool):
        self._readonly = readonly

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        # Draw rule
        self.opt.initFrom(self)
        self.opt.rect = self.rect()
        self.opt.sliderPosition = 0
        self.opt.subControls = QStyle.SubControl.SC_SliderGroove | QStyle.SubControl.SC_SliderTickmarks

        # Draw GROOVE
        self.style().drawComplexControl(QStyle.ComplexControl.CC_Slider, self.opt, painter)

        # Draw INTERVAL
        color = self.palette().color(QPalette.Highlight)
        color.setAlpha(160)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)

        selection = self._get_selection()

        painter.drawRect(selection)

        # Handles
        self.opt.subControls = QStyle.SubControl.SC_SliderHandle

        # Draw first handle
        self.opt.sliderPosition = self._first_position
        self.style().drawComplexControl(QStyle.ComplexControl.CC_Slider, self.opt, painter)

        # Draw second handle
        self.opt.sliderPosition = self._second_position
        self.style().drawComplexControl(QStyle.ComplexControl.CC_Slider, self.opt, painter)

    def mousePressEvent(self, event: QMouseEvent):
        self.opt.sliderPosition = self._first_position
        self._first_sc = self.style().hitTestComplexControl(QStyle.ComplexControl.CC_Slider, self.opt, event.pos(), self)

        self.opt.sliderPosition = self._second_position
        self._second_sc = self.style().hitTestComplexControl(QStyle.ComplexControl.CC_Slider, self.opt, event.pos(), self)

    def mouseMoveEvent(self, event: QMouseEvent):
        distance = self.opt.maximum - self.opt.minimum

        pos = self.style().sliderValueFromPosition(0, distance, event.pos().x(), self.rect().width())

        if not self._readonly:
            if self._second_sc == QStyle.SubControl.SC_SliderHandle:
                if pos - self._min_range >= self._first_position:
                    self.set_range(self._first_position, pos)
                    self.update()
            elif self._first_sc == QStyle.SubControl.SC_SliderHandle:
                if pos + self._min_range <= self._second_position:
                    self.set_range(pos, self._second_position)
                    self.update()

    def enterEvent(self, event):
        self._show_tooltip()

    def sizeHint(self):
        slider_length = 84

        w = slider_length
        h = self.style().pixelMetric(QStyle.PixelMetric.PM_SliderThickness, self.opt, self)

        return self.style().sizeFromContents(QStyle.ContentsType.CT_Slider, self.opt, QSize(w, h), self)

    def _get_selection(self):
        self.opt.sliderPosition = self._first_position
        x_left_handle = (
            self.style()
            .subControlRect(QStyle.ComplexControl.CC_Slider, self.opt, QStyle.SubControl.SC_SliderHandle)
            .right()
        )

        self.opt.sliderPosition = self._second_position
        x_right_handle = (
            self.style()
            .subControlRect(QStyle.ComplexControl.CC_Slider, self.opt, QStyle.SubControl.SC_SliderHandle)
            .left()
        )

        groove_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider, self.opt, QStyle.SubControl.SC_SliderGroove
        )

        return QRect(
            x_left_handle,
            groove_rect.y(),
            x_right_handle - x_left_handle,
            groove_rect.height(),
        ).adjusted(-1, 1, 1, -1)

    def _show_tooltip(self):
        pos = self._get_selection().center()

        tooltip_text = f'{self._first_tooltip} - {self._second_tooltip}'
        font_metrics = QFontMetrics(QToolTip.font())

        tooltip_width = font_metrics.horizontalAdvance(tooltip_text)
        pos.setX(pos.x() - tooltip_width // 2)

        QToolTip.showText(self.mapToGlobal(pos), tooltip_text)


class LabeledRangeSlider(QWidget):
    def __init__(self, label_map_func: Callable[[int], str], parent: QWidget = None):
        super().__init__(parent)

        # State
        self._label_map_func = label_map_func

        # Layout
        layout = QVBoxLayout(self)

        # Slider
        slider_layout = QHBoxLayout(self)

        self._min_label = QLabel(self._label_map_func(0), self)
        slider_layout.addWidget(self._min_label)

        self._slider = RangeSlider(parent=self)
        slider_layout.addWidget(self._slider)

        self._max_label = QLabel(self._label_map_func(0), self)
        slider_layout.addWidget(self._max_label)

        self._slider.first_value_changed.connect(self._show_first_tooltip)
        self._slider.second_value_changed.connect(self._show_second_tooltip)
        self._slider.min_changed.connect(lambda value: self._min_label.setText(self._label_map_func(value)))
        self._slider.max_changed.connect(lambda value: self._max_label.setText(self._label_map_func(value)))

        layout.addLayout(slider_layout)

        self.setLayout(layout)

    def set_range_limit(self, minimum: int, maximum: int):
        self._slider.set_range_limit(minimum, maximum)

    def set_range(self, start: int, end: int):
        self._slider.set_range(start, end)

    def set_min_range(self, min_range_in_ms: int):
        self._slider.set_min_range(min_range_in_ms)

    def get_range(self):
        return self._slider.get_range()

    def set_readonly(self, readonly: bool):
        self._slider.set_readonly(readonly)

    def set_min_border_visible(self, visible: bool):
        self._min_label.setVisible(visible)

    def set_max_border_visible(self, visible: bool):
        self._max_label.setVisible(visible)

    def _show_first_tooltip(self, value):
        self._slider.set_first_tooltip(self._label_map_func(value))

    def _show_second_tooltip(self, value):
        self._slider.set_second_tooltip(self._label_map_func(value))
