from PyQt5 import QtWidgets
from dataclasses import dataclass
from pathlib import Path

from src.components.formValidation import validateRequiredField, __validateRequiredPath__, showErrorMessage, \
    validateRequiredDirectory
from src.components.project import Project, saveProject
from src.components.widgets.style.Styles import GeneralStyleMixin


class ProjectCreationDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        GeneralStyleMixin.applyStyle(self)
        self.setWindowTitle("Create Project")

        # State
        self.project: Project | None = None

        # Window size
        self.setMinimumWidth(700)

        # Layout
        self.layout = QtWidgets.QVBoxLayout(self)

        # Project name
        self.layout.addWidget(QtWidgets.QLabel("Name:", self))
        self.nameLineEdit = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.nameLineEdit)

        # Description
        self.layout.addWidget(QtWidgets.QLabel("Description:", self))
        self.descriptionTextEdit = QtWidgets.QTextEdit(self)
        self.layout.addWidget(self.descriptionTextEdit)

        # Project file path
        self.layout.addWidget(QtWidgets.QLabel("Project File Path:", self))
        self.projectFileDirectoryLineEdit = QtWidgets.QLineEdit(self)
        browseButton = QtWidgets.QPushButton("Browse", self)
        browseButton.clicked.connect(self.browseProjectFileDirectory)

        projectDirectoryInputLayout = QtWidgets.QHBoxLayout()
        projectDirectoryInputLayout.addWidget(self.projectFileDirectoryLineEdit)
        projectDirectoryInputLayout.addWidget(browseButton)
        self.layout.addLayout(projectDirectoryInputLayout)

        # Dataset directory
        self.layout.addWidget(QtWidgets.QLabel("Dataset Directory:", self))
        self.datasetDirectoryLineEdit = QtWidgets.QLineEdit(self)
        browseButton = QtWidgets.QPushButton("Browse", self)
        browseButton.clicked.connect(self.browseDatasetDirectory)

        datasetDirectoryInputLayout = QtWidgets.QHBoxLayout()
        datasetDirectoryInputLayout.addWidget(self.datasetDirectoryLineEdit)
        datasetDirectoryInputLayout.addWidget(browseButton)
        self.layout.addLayout(datasetDirectoryInputLayout)

        # Buttons
        buttonLayout = QtWidgets.QHBoxLayout()

        createButton = QtWidgets.QPushButton("Create", self)
        createButton.clicked.connect(self.createProject)
        buttonLayout.addWidget(createButton)

        cancelButton = QtWidgets.QPushButton("Cancel", self)
        cancelButton.clicked.connect(self.reject)
        buttonLayout.addWidget(cancelButton)

        self.layout.addLayout(buttonLayout)

    def showDialog(self):
        dialogResult = self.exec_()
        if dialogResult == QtWidgets.QDialog.Accepted:
            return self.project
        return None

    def browseProjectFileDirectory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Project File Directory")
        if directory:
            self.projectFileDirectoryLineEdit.setText(directory)

    def browseDatasetDirectory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Dataset Directory")
        if directory:
            self.datasetDirectoryLineEdit.setText(directory)

    def createProject(self):
        errors = self.__validate__()
        if errors:
            showErrorMessage(errors, self)
            return

        try:
            self.project = Project(
                self.nameLineEdit.text(),
                self.descriptionTextEdit.toPlainText(),
                Path(self.projectFileDirectoryLineEdit.text()),
                Path(self.datasetDirectoryLineEdit.text()),
            )
            saveProject(self.project)
            self.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                "Couldn't create project: " + str(e),
                QtWidgets.QMessageBox.Close
            )

    def __validate__(self):
        errors = dict(filter(None, [
            validateRequiredField(self.nameLineEdit.text(), "Name"),
            validateRequiredDirectory(self.datasetDirectoryLineEdit.text(), "Dataset directory"),
            validateRequiredDirectory(self.projectFileDirectoryLineEdit.text(), "Project file directory")
        ]))
        return errors
