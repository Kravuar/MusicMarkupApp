from src.app.form_validation import validate_required_file
from PyQt5 import QtWidgets
from pathlib import Path

from src.app.form_validation import validate_required_field, show_error_message, validate_required_directory
from src.app.project import Project
from src.config import PROJECT_FILE_SUFFIX


class OpenExistingProjectDialog(QtWidgets.QDialog):
    _PROJECT_FILE_FILTER = f"MM Project (*{PROJECT_FILE_SUFFIX});;All Files (*)"

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("Open Project")

        # State
        self._project: Project | None = None

        # Window size
        self.setMinimumWidth(700)

        # Layout
        layout = QtWidgets.QVBoxLayout(self)

        # Project file
        layout.addWidget(QtWidgets.QLabel("Project file:", self))
        self._project_file_line_edit = QtWidgets.QLineEdit(self)
        browse_button = QtWidgets.QPushButton("Browse", self)
        browse_button.clicked.connect(self._browse_project_file)

        dir_layout = QtWidgets.QHBoxLayout()
        dir_layout.addWidget(self._project_file_line_edit)
        dir_layout.addWidget(browse_button)
        layout.addLayout(dir_layout)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        open_button = QtWidgets.QPushButton("Open", self)
        open_button.clicked.connect(self._open_project)
        button_layout.addWidget(open_button)

        cancel_button = QtWidgets.QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def show_dialog(self):
        dialog_result = self.exec_()
        if dialog_result == QtWidgets.QDialog.Accepted:
            return self._project
        return None

    def _browse_project_file(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Project File",
            "",
            OpenExistingProjectDialog._PROJECT_FILE_FILTER
        )
        if file:
            self._project_file_line_edit.setText(file)

    def _open_project(self):
        errors = self._validate()
        if errors:
            show_error_message(errors, self)
            return

        try:
            self._project = Project.load(Path(self._project_file_line_edit.text()))
            self.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                "Couldn't load project: " + str(e),
                QtWidgets.QMessageBox.Close
            )

    def _validate(self):
        errors = dict(filter(None, [
            validate_required_file(self._project_file_line_edit.text(), "Project File"),
        ]))
        return errors


class ProjectCreationDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("Create Project")

        # State
        self._project: Project | None = None

        # Window size
        self.setMinimumWidth(700)

        # Layout
        layout = QtWidgets.QVBoxLayout(self)

        # Project name
        layout.addWidget(QtWidgets.QLabel("Name:", self))
        self._name_line_edit = QtWidgets.QLineEdit(self)
        layout.addWidget(self._name_line_edit)

        # Description
        layout.addWidget(QtWidgets.QLabel("Description:", self))
        self._description_text_edit = QtWidgets.QTextEdit(self)
        layout.addWidget(self._description_text_edit)

        # Dataset directory
        layout.addWidget(QtWidgets.QLabel("Dataset Directory:", self))
        self._dataset_directory_line_edit = QtWidgets.QLineEdit(self)
        browse_button = QtWidgets.QPushButton("Browse", self)
        browse_button.clicked.connect(self._browse_dataset_directory)

        dataset_directory_input_layout = QtWidgets.QHBoxLayout()
        dataset_directory_input_layout.addWidget(self._dataset_directory_line_edit)
        dataset_directory_input_layout.addWidget(browse_button)
        layout.addLayout(dataset_directory_input_layout)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        create_button = QtWidgets.QPushButton("Create", self)
        create_button.clicked.connect(self._create_project)
        button_layout.addWidget(create_button)

        cancel_button = QtWidgets.QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def show_dialog(self):
        dialog_result = self.exec_()
        if dialog_result == QtWidgets.QDialog.Accepted:
            return self._project
        return None

    def _browse_dataset_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Dataset Directory")
        if directory:
            self._dataset_directory_line_edit.setText(directory)

    def _create_project(self):
        errors = self._validate()
        if errors:
            show_error_message(errors, self)
            return

        try:
            self._project = Project(
                self._name_line_edit.text(),
                self._description_text_edit.toPlainText(),
                Path(self._dataset_directory_line_edit.text()),
            )
            self.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                "Couldn't create project: " + str(e),
                QtWidgets.QMessageBox.Close
            )

    def _validate(self):
        errors = dict(filter(None, [
            validate_required_field(self._name_line_edit.text(), "Name"),
            validate_required_directory(self._dataset_directory_line_edit.text(), "Dataset directory")
        ]))
        return errors
