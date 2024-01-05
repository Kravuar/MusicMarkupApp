from src.app.form_validation import validate_required_file
from PyQt5 import QtWidgets
from pathlib import Path

from src.app.form_validation import validate_required_field, show_error_message, validate_required_directory
from src.app.project import Project
from src.ui.styles import GeneralStyleMixin


class OpenExistingProjectDialog(QtWidgets.QDialog):
    project_file_filter = "MM Project (*.mmp);;All Files (*)"

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        GeneralStyleMixin.apply_style(self)
        self.setWindowTitle("Open Project")

        # State
        self.project: Project | None = None

        # Window size
        self.setMinimumWidth(700)

        # Layout
        self.layout = QtWidgets.QVBoxLayout(self)

        # Project file
        self.layout.addWidget(QtWidgets.QLabel("Project file:", self))
        self.project_file = QtWidgets.QLineEdit(self)
        browse_button = QtWidgets.QPushButton("Browse", self)
        browse_button.clicked.connect(self.browse_project_file)

        dir_layout = QtWidgets.QHBoxLayout()
        dir_layout.addWidget(self.project_file)
        dir_layout.addWidget(browse_button)
        self.layout.addLayout(dir_layout)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        open_button = QtWidgets.QPushButton("Open", self)
        open_button.clicked.connect(self.open_project)
        button_layout.addWidget(open_button)

        cancel_button = QtWidgets.QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        self.layout.addLayout(button_layout)

    def show_dialog(self):
        dialog_result = self.exec_()
        if dialog_result == QtWidgets.QDialog.Accepted:
            return self.project
        return None

    def browse_project_file(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Project File",
            "",
            OpenExistingProjectDialog.project_file_filter
        )
        if file:
            self.project_file.setText(file)

    def open_project(self):
        errors = self.__validate__()
        if errors:
            show_error_message(errors, self)
            return

        try:
            self.project = Project.load(Path(self.project_file.text()))
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
            validate_required_file(self.project_file.text(), "Project File"),
        ]))
        return errors


class ProjectCreationDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        GeneralStyleMixin.apply_style(self)
        self.setWindowTitle("Create Project")

        # State
        self.project: Project | None = None

        # Window size
        self.setMinimumWidth(700)

        # Layout
        self.layout = QtWidgets.QVBoxLayout(self)

        # Project name
        self.layout.addWidget(QtWidgets.QLabel("Name:", self))
        self.name_line_edit = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.name_line_edit)

        # Description
        self.layout.addWidget(QtWidgets.QLabel("Description:", self))
        self.description_text_edit = QtWidgets.QTextEdit(self)
        self.layout.addWidget(self.description_text_edit)

        # Project file path
        self.layout.addWidget(QtWidgets.QLabel("Project File Path:", self))
        self.project_file_directory_line_edit = QtWidgets.QLineEdit(self)
        browse_button = QtWidgets.QPushButton("Browse", self)
        browse_button.clicked.connect(self.browse_project_file_directory)

        project_directory_input_layout = QtWidgets.QHBoxLayout()
        project_directory_input_layout.addWidget(self.project_file_directory_line_edit)
        project_directory_input_layout.addWidget(browse_button)
        self.layout.addLayout(project_directory_input_layout)

        # Dataset directory
        self.layout.addWidget(QtWidgets.QLabel("Dataset Directory:", self))
        self.dataset_directory_line_edit = QtWidgets.QLineEdit(self)
        browse_button = QtWidgets.QPushButton("Browse", self)
        browse_button.clicked.connect(self.browse_dataset_directory)

        dataset_directory_input_layout = QtWidgets.QHBoxLayout()
        dataset_directory_input_layout.addWidget(self.dataset_directory_line_edit)
        dataset_directory_input_layout.addWidget(browse_button)
        self.layout.addLayout(dataset_directory_input_layout)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()

        create_button = QtWidgets.QPushButton("Create", self)
        create_button.clicked.connect(self.create_project)
        button_layout.addWidget(create_button)

        cancel_button = QtWidgets.QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        self.layout.addLayout(button_layout)

    def show_dialog(self):
        dialog_result = self.exec_()
        if dialog_result == QtWidgets.QDialog.Accepted:
            return self.project
        return None

    def browse_project_file_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Project File Directory")
        if directory:
            self.project_file_directory_line_edit.setText(directory)

    def browse_dataset_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Dataset Directory")
        if directory:
            self.dataset_directory_line_edit.setText(directory)

    def create_project(self):
        errors = self.__validate__()
        if errors:
            show_error_message(errors, self)
            return

        try:
            self.project = Project(
                self.name_line_edit.text(),
                self.description_text_edit.toPlainText(),
                Path(self.project_file_directory_line_edit.text()),
                Path(self.dataset_directory_line_edit.text()),
            )
            self.project.save()
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
            validate_required_field(self.name_line_edit.text(), "Name"),
            validate_required_directory(self.dataset_directory_line_edit.text(), "Dataset directory"),
            validate_required_directory(self.project_file_directory_line_edit.text(), "Project file directory")
        ]))
        return errors
