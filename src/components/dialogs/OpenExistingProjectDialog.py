from dataclasses import dataclass
from pathlib import Path

from PyQt5 import QtWidgets
from src.components.Styles import GeneralStyleMixin


class OpenExistingProjectDialog(QtWidgets.QDialog):
    project_file_filter = "MM Project (*.mmp);;All Files (*)"

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)

        # Window size
        self.setMinimumWidth(700)

        self.setWindowTitle("Project Creation")
        GeneralStyleMixin.applyStyle(self)

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

        # Open Button
        openButton = QtWidgets.QPushButton("Open", self)
        openButton.clicked.connect(self.openProject)
        self.layout.addWidget(openButton)

        # Cancel Button
        cancelButton = QtWidgets.QPushButton("Cancel", self)
        cancelButton.clicked.connect(self.reject)
        self.layout.addWidget(cancelButton)

    def browseProjectFile(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Project File", "", OpenExistingProjectDialog.project_file_filter)
        if file:
            self.projectFile.setText(file)

    def openProject(self):
        projectFile = self.projectFile.text()
        if not projectFile:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                "Project file is a required field.",
                QtWidgets.QMessageBox.Close
            )
            return

        path = Path(projectFile)
        if not path.exists() or not path.is_file():
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                "The selected file does not exist or is not a valid project file.",
                QtWidgets.QMessageBox.Close
            )
            return

        # TODO: additional validation
        self.accept()

    def showDialog(self):
        dialogResult = self.exec_()
        if dialogResult == QtWidgets.QDialog.Accepted:
            return ExistingProjectForm(Path(self.projectFile.text()))
        return None


@dataclass
class ExistingProjectForm:
    path: Path
