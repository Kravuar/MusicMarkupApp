import math
from pathlib import Path

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColor


def sigmoid(x, slope=1, midpoint=0.5):
    return 1 / (1 + math.exp(-slope * (x - midpoint)))


def blend_colors(color1: QColor, color2: QColor, ratio: float):
    r = int(color1.red() * (1 - ratio) + color2.red() * ratio)
    g = int(color1.green() * (1 - ratio) + color2.green() * ratio)
    b = int(color1.blue() * (1 - ratio) + color2.blue() * ratio)

    return QColor(r, g, b, 255)


class GeneralStyleMixin:
    icon_path = str(Path("assets/icon.png").resolve())

    main_color = QColor("#505")
    accent_color = QColor("#DFA")

    text_color = QtCore.Qt.white
    button_text_color = QtCore.Qt.black

    @staticmethod
    def apply_style(widget: QtWidgets.QWidget):
        widget.setWindowIcon(QtGui.QIcon(GeneralStyleMixin.icon_path))

        gradient = QtGui.QLinearGradient(0, 0, widget.width(), widget.height())
        num_steps = 100

        for i in range(num_steps + 1):
            position = i / num_steps
            blend_factor = sigmoid(position, 2, midpoint=1.7)
            color = blend_colors(GeneralStyleMixin.main_color, GeneralStyleMixin.accent_color, blend_factor)
            gradient.setColorAt(position, color)

        widget.setAutoFillBackground(True)
        palette = widget.palette()
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(gradient))
        palette.setColor(QtGui.QPalette.WindowText, GeneralStyleMixin.text_color)
        palette.setColor(QtGui.QPalette.Button, GeneralStyleMixin.accent_color)
        palette.setColor(QtGui.QPalette.ButtonText, GeneralStyleMixin.button_text_color)
        widget.setPalette(palette)

        font = widget.font()
        font.setStyleHint(font.SansSerif)
        font.setPointSize(16)
        widget.setFont(font)
