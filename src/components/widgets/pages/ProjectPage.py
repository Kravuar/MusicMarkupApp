from typing import Any

from PyQt5 import QtWidgets

from src.components.project import Project
from src.components.widgets.multipage.WindowPage import WindowPage


class ProjectPage(WindowPage):
    def __init__(self):
        super().__init__()

        # State
        self.project: Project | None = None

        # Layout
        self.layout = QtWidgets.QVBoxLayout(self)

        # Info
        infoLayout = QtWidgets.QHBoxLayout()

        self.projectName = QtWidgets.QLabel()
        infoLayout.addWidget(self.projectName)

        self.layout.addLayout(infoLayout)

        # Buttons
        buttonsLayout = QtWidgets.QHBoxLayout()

        self.exitButton = QtWidgets.QPushButton("Exit", self)
        self.exitButton.clicked.connect(self.exit)
        buttonsLayout.addWidget(self.exitButton)

        self.layout.addLayout(buttonsLayout)

    def exit(self):
        # TODO: Ask only if changes were made
        answer = QtWidgets.QMessageBox.question(
            self,
            "Closing Project",
            "Do you want to save this project before closing it?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel
        )
        if answer == QtWidgets.QMessageBox.Yes:
            self.project.save()
        elif answer == QtWidgets.QMessageBox.Cancel:
            return
        self.goto("main")

    def onEnter(self, data: Any):
        if not isinstance(data, Project):
            raise TypeError("Data must be of a Project type.")
        self.project = data
        self.projectName.setText(self.project.name)
        # TODO: init stuff
