from typing import Any

from src.components.WindowPage import WindowPage
from PyQt5 import QtWidgets

from src.components.dialogs.OpenExistingProjectDialog import ExistingProjectForm
from src.components.dialogs.ProjectCreationDialog import ProjectCreationForm


class ProjectPage(WindowPage):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Page")

        self.exitButton = QtWidgets.QPushButton("Exit", self)
        self.exitButton.clicked.connect(self.exit)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.exitButton)
        self.layout.addStretch()

    def exit(self):
        self.goto("main")

    def onEnter(self, data: Any):
        if isinstance(data, ExistingProjectForm):
            self.__onExistingProject(data)
        elif isinstance(data, ProjectCreationForm):
            self.__onProjecCreation(data)
        else:
            raise TypeError()

    def __onExistingProject(self, data: ExistingProjectForm):
        print("Existing: " + str(data.path))

    def __onProjecCreation(self, data: ProjectCreationForm):
        print("Creating: " + data.name)
        print(str(data.datasetDir))

# TODO: class holding all project info
