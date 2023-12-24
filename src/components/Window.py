from PyQt5 import QtWidgets, QtCore
from src.components.PageWindow import PageWindow
from src.components.Styles import GeneralStyleMixin
from src.components.pages.MainPage import MainPage
from src.components.pages.ProjectPage import ProjectPage


class Window(QtWidgets.QMainWindow):
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

        self.goto("main")

    def registerPage(self, widget: PageWindow, name):
        self.pages[name] = widget
        self.stackedWidget.addWidget(widget)
        widget.gotoSignal.connect(self.goto)

    @QtCore.pyqtSlot(str)
    def goto(self, name):
        if name in self.pages:
            page = self.pages[name]
            self.stackedWidget.setCurrentWidget(page)
            self.setWindowTitle(page.windowTitle())
