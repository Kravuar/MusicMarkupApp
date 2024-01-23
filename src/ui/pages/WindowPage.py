from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget


@dataclass
class GotoPayload:
    name: str
    data: Any = None


class WindowPage(QWidget):
    goto_signal = Signal(GotoPayload)

    def __init__(self):
        super().__init__()

    def on_enter(self, data: Any):
        pass

    def _goto(self, name: str, data: Any = None):
        self.goto_signal.emit(GotoPayload(name, data))
