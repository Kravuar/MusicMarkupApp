from PyQt5 import QtWidgets, QtCore
from src.components.WindowPage import WindowPage, GotoPayload
from src.components.Styles import GeneralStyleMixin
from src.components.pages.MainPage import MainPage
from src.components.pages.ProjectPage import ProjectPage


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        GeneralStyleMixin.applyStyle(self)

        # Window size
        self.setMinimumSize(400, 400)
        self.resize(1000, 700)

        # Page container
        self.stackedWidget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stackedWidget)
        self.pages = {}

        # Pages
        self.registerPage(MainPage(), "main")
        self.registerPage(ProjectPage(), "project")

        self.goto(GotoPayload("main"))

    def registerPage(self, page: WindowPage, name: str):
        self.pages[name] = page
        self.stackedWidget.addWidget(page)
        page.gotoSignal.connect(self.goto)

    @QtCore.pyqtSlot(GotoPayload)
    def goto(self, payload: GotoPayload):
        if payload.name in self.pages:
            page = self.pages[payload.name]
            self.stackedWidget.setCurrentWidget(page)
            self.setWindowTitle(page.windowTitle())
            page.onEnter(payload.data)
