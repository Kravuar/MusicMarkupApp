from PyQt5 import QtWidgets
from dataclasses import dataclass
from pathlib import Path

from src.components.Styles import GeneralStyleMixin


class ProjectCreationDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.formResult = None

        # Window size
        self.setMinimumWidth(700)

        self.setWindowTitle("Project Creation")
        GeneralStyleMixin.applyStyle(self)

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

        # Dataset directory
        self.layout.addWidget(QtWidgets.QLabel("Dataset Directory:", self))
        self.datasetDirLineEdit = QtWidgets.QLineEdit(self)
        browseButton = QtWidgets.QPushButton("Browse", self)
        browseButton.clicked.connect(self.browseDirectory)

        dirLayout = QtWidgets.QHBoxLayout()
        dirLayout.addWidget(self.datasetDirLineEdit)
        dirLayout.addWidget(browseButton)
        self.layout.addLayout(dirLayout)

        # Buttons
        createButton = QtWidgets.QPushButton("Create", self)
        createButton.clicked.connect(self.onAccept)
        self.layout.addWidget(createButton)

        cancelButton = QtWidgets.QPushButton("Cancel", self)
        cancelButton.clicked.connect(self.reject)
        self.layout.addWidget(cancelButton)

    def browseDirectory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Dataset Directory")
        if directory:
            self.datasetDirLineEdit.setText(directory)

    def onAccept(self):
        path = Path(self.datasetDirLineEdit.text())

        if not path.exists() or not path.is_dir():
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                "The selected directory does not exist or is not a valid directory.",
                QtWidgets.QMessageBox.Close
            )
            return

        self.formResult = ProjectCreationForm(
            name=self.nameLineEdit.text(),
            datasetDir=path,
            description=self.descriptionTextEdit.toPlainText()
        )
        self.accept()

    def showDialog(self):
        dialogResult = self.exec_()
        if dialogResult == QtWidgets.QDialog.Accepted:
            return self.formResult
        return None


@dataclass
class ProjectCreationForm:
    name: str
    datasetDir: Path
    description: str
