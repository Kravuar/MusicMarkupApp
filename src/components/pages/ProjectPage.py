from src.components.PageWindow import PageWindow
from PyQt5 import QtWidgets


class ProjectPage(PageWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Page")

        self.exitButton = QtWidgets.QPushButton("Exit", self)
        self.exitButton.clicked.connect(self.onExit)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.exitButton)
        self.layout.addStretch()

    def onExit(self):
        self.goto("main")
