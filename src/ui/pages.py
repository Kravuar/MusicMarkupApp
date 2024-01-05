from dataclasses import dataclass

from src.ui.dialogs import ProjectCreationDialog, OpenExistingProjectDialog
from typing import Any

from PyQt5 import QtWidgets, QtCore

from src.app.project import Project
from src.ui.styles import GeneralStyleMixin


@dataclass
class GotoPayload:
    name: str
    data: Any = None


class WindowPage(QtWidgets.QWidget):
    goto_signal = QtCore.pyqtSignal(GotoPayload)

    def __init__(self):
        super().__init__()
        GeneralStyleMixin.apply_style(self)

    def on_enter(self, data: Any):
        pass

    def on_exit(self):
        pass

    def goto(self, name: str, data: Any = None):
        self.on_exit()
        self.goto_signal.emit(GotoPayload(name, data))


class MainPage(WindowPage):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome")

        # Layout
        self.layout = QtWidgets.QVBoxLayout(self)

        # Buttons
        buttons_layout = QtWidgets.QVBoxLayout()

        self.create_project_button = QtWidgets.QPushButton("Create New Project", self)
        self.create_project_button.clicked.connect(self.on_create)
        buttons_layout.addWidget(self.create_project_button)

        self.open_project_button = QtWidgets.QPushButton("Open Existing Project", self)
        self.open_project_button.clicked.connect(self.on_open_existing)
        buttons_layout.addWidget(self.open_project_button)

        self.layout.addLayout(buttons_layout)

    def on_create(self):
        project_creation_dialog = ProjectCreationDialog(self)
        result = project_creation_dialog.show_dialog()
        if result:
            self.goto("project", result)

    def on_open_existing(self):
        open_existing_dialog = OpenExistingProjectDialog(self)
        result = open_existing_dialog.show_dialog()
        if result:
            self.goto("project", result)


class ProjectPage(WindowPage):
    def __init__(self):
        super().__init__()

        # State
        self.project: Project | None = None

        # Layout
        self.layout = QtWidgets.QVBoxLayout(self)

        # Info
        info_layout = QtWidgets.QHBoxLayout()

        self.project_name = QtWidgets.QLabel()
        info_layout.addWidget(self.project_name)

        self.layout.addLayout(info_layout)

        # Buttons
        buttons_layout = QtWidgets.QHBoxLayout()

        self.exit_button = QtWidgets.QPushButton("Exit", self)
        self.exit_button.clicked.connect(self.exit)
        buttons_layout.addWidget(self.exit_button)

        self.layout.addLayout(buttons_layout)

    def exit(self):
        # TODO: Ask only if changes were made
        answer = QtWidgets.QMessageBox.question(
            self,
            "Closing Project",
            "Do you want to save this project before closing it?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel,
            QtWidgets.QMessageBox.Yes
        )
        if answer == QtWidgets.QMessageBox.Yes:
            self.project.save()
        elif answer == QtWidgets.QMessageBox.Cancel:
            return
        self.goto("main")

    def on_enter(self, data: Any):
        if not isinstance(data, Project):
            raise TypeError("Data must be of a Project type.")
        self.project = data
        self.project_name.setText(self.project.name)
        # TODO: init stuff
