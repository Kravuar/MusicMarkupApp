from typing import Any

from PyQt5 import QtCore, QtWidgets

from src.components.multipage import GotoPayload
from src.components.widgets.style.Styles import GeneralStyleMixin


class WindowPage(QtWidgets.QWidget):
    gotoSignal = QtCore.pyqtSignal(GotoPayload)

    def __init__(self):
        super().__init__()
        GeneralStyleMixin.applyStyle(self)

    def onEnter(self, data: Any):
        pass

    def onExit(self):
        pass

    def goto(self, name: str, data: Any = None):
        self.onExit()
        self.gotoSignal.emit(GotoPayload(name, data))
