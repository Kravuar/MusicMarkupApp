from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from src.ui.pages.MainPage import MainPage
from src.ui.pages.ProjectPage import ProjectPage
from src.ui.pages.WindowPage import GotoPayload, WindowPage
from src.ui.styles import GlobalStyle


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Style
        self.setWindowIcon(GlobalStyle.get_icon())
        self.setStyleSheet(GlobalStyle.create_stylesheet())

        # Window size
        self.setMinimumSize(400, 400)
        self.resize(1000, 700)

        # Page container
        self._stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self._stacked_widget)
        self._pages = {}

        # Pages
        self._register_page(MainPage(), "main")
        self._register_page(ProjectPage(), "project")

        self._goto(GotoPayload("main"))

    def _register_page(self, page: WindowPage, name: str):
        self._pages[name] = page
        self._stacked_widget.addWidget(page)
        page.goto_signal.connect(self._goto)

    @Slot(GotoPayload)
    def _goto(self, payload: GotoPayload):
        if payload.name in self._pages:
            page = self._pages[payload.name]
            self._stacked_widget.setCurrentWidget(page)
            self.setWindowTitle(page.windowTitle())
            page.on_enter(payload.data)
