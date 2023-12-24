from PyQt5 import QtCore, QtWidgets
from src.components.Styles import GeneralStyleMixin


class PageWindow(QtWidgets.QWidget):
    gotoSignal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        GeneralStyleMixin.applyStyle(self)

    def goto(self, name):
        self.gotoSignal.emit(name)
