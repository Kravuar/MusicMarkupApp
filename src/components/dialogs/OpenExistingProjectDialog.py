from dataclasses import dataclass

from PyQt5 import QtWidgets
from src.components.Styles import GeneralStyleMixin


class OpenExistingProjectDialog(QtWidgets.QDialog):
    project_file_filter = "MM Project (*.mmp);;All Files (*)"

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.formResult = None

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
        openButton.clicked.connect(self.onAccept)
        self.layout.addWidget(openButton)

        # Cancel Button
        cancelButton = QtWidgets.QPushButton("Cancel", self)
        cancelButton.clicked.connect(self.reject)
        self.layout.addWidget(cancelButton)

    def browseProjectFile(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Project File", "", OpenExistingProjectDialog.project_file_filter)
        if file:
            self.projectFile.setText(file)

    def onAccept(self):
        self.formResult = {
            'project_file': self.projectFile.text()
        }
        self.accept()

    def showDialog(self):
        dialogResult = self.exec_()
        if dialogResult == QtWidgets.QDialog.Accepted:
            return self.formResult
        return None


@dataclass
class ExistingProjectForm:
    path: str
