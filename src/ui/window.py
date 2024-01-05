from PyQt5 import QtCore, QtWidgets

from src.ui.pages import MainPage, ProjectPage, GotoPayload, WindowPage
from src.ui.styles import GeneralStyleMixin


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        GeneralStyleMixin.apply_style(self)

        # Window size
        self.setMinimumSize(400, 400)
        self.resize(1000, 700)

        # Page container
        self.stacked_widget = QtWidgets.QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        self.pages = {}

        # Pages
        self.register_page(MainPage(), "main")
        self.register_page(ProjectPage(), "project")

        self.goto(GotoPayload("main"))

    def register_page(self, page: WindowPage, name: str):
        self.pages[name] = page
        self.stacked_widget.addWidget(page)
        page.goto_signal.connect(self.goto)

    @QtCore.pyqtSlot(GotoPayload)
    def goto(self, payload: GotoPayload):
        if payload.name in self.pages:
            page = self.pages[payload.name]
            self.stacked_widget.setCurrentWidget(page)
            self.setWindowTitle(page.windowTitle())
            page.on_enter(payload.data)
