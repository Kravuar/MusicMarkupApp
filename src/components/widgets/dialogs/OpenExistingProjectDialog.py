from dataclasses import dataclass
from pathlib import Path

from PyQt5 import QtWidgets

from src.components.formValidation import showErrorMessage, validateRequiredFile
from src.components.project import loadProject, Project
from src.components.widgets.style.Styles import GeneralStyleMixin


class OpenExistingProjectDialog(QtWidgets.QDialog):
    project_file_filter = "MM Project (*.mmp);;All Files (*)"

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        GeneralStyleMixin.applyStyle(self)
        self.setWindowTitle("Open Project")

        # State
        self.project: Project | None = None

        # Window size
        self.setMinimumWidth(700)

        # Layout
        self.layout = QtWidgets.QVBoxLayout(self)

        # Project file
        self.layout.addWidget(QtWidgets.QLabel("Project file:", self))
        self.projectFile = QtWidgets.QLineEdit(self)
        browseButton = QtWidgets.QPushButton("Browse", self)
        browseButton.clicked.connect(self.browseProjectFile)

        dirLayout = QtWidgets.QHBoxLayout()
        dirLayout.addWidget(self.projectFile)
        dirLayout.addWidget(browseButton)
        self.layout.addLayout(dirLayout)

        # Buttons
        buttonLayout = QtWidgets.QHBoxLayout()

        openButton = QtWidgets.QPushButton("Open", self)
        openButton.clicked.connect(self.openProject)
        buttonLayout.addWidget(openButton)

        cancelButton = QtWidgets.QPushButton("Cancel", self)
        cancelButton.clicked.connect(self.reject)
        buttonLayout.addWidget(cancelButton)

        self.layout.addLayout(buttonLayout)

    def showDialog(self):
        dialogResult = self.exec_()
        if dialogResult == QtWidgets.QDialog.Accepted:
            return self.project
        return None

    def browseProjectFile(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Project File", "",
                                                        OpenExistingProjectDialog.project_file_filter)
        if file:
            self.projectFile.setText(file)

    def openProject(self):
        errors = self.__validate__()
        if errors:
            showErrorMessage(errors, self)
            return

        try:
            self.project = loadProject(Path(self.projectFile.text()))
            self.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                "Couldn't load project: " + str(e),
                QtWidgets.QMessageBox.Close
            )

    def __validate__(self):
        errors = dict(filter(None, [
            validateRequiredFile(Path(self.projectFile.text()), "Project File"),
        ]))
        return errors
