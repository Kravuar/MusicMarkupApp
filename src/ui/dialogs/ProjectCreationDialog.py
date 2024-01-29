from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QWidget, QDialog, QMessageBox, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, \
    QFileDialog, QTextEdit

from src.app.form_validation import validate_required_field, show_error_message, validate_required_directory
from src.app.project import Project
from src.ui.pages.ProjectPage import ProjectPage


class ProjectCreationDialog(QDialog):
    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)
        self.setWindowTitle("Create Project")

        # State
        self._project: Project | None = None

        # Window size
        self.setMinimumWidth(700)

        # Layout
        layout = QVBoxLayout(self)

        # Project name
        layout.addWidget(QLabel("Name:", self))
        self._name_line_edit = QLineEdit(self)
        layout.addWidget(self._name_line_edit)

        # Description
        layout.addWidget(QLabel("Description:", self))
        self._description_text_edit = QTextEdit(self)
        layout.addWidget(self._description_text_edit)

        # Dataset directory
        layout.addWidget(QLabel("Dataset Directory:", self))
        self._dataset_directory_line_edit = QLineEdit(self)
        browse_button = QPushButton("Browse", self)
        browse_button.clicked.connect(self._browse_dataset_directory)

        dataset_directory_input_layout = QHBoxLayout()
        dataset_directory_input_layout.addWidget(self._dataset_directory_line_edit)
        dataset_directory_input_layout.addWidget(browse_button)
        layout.addLayout(dataset_directory_input_layout)

        # Buttons
        button_layout = QHBoxLayout()

        create_button = QPushButton("Create", self)
        create_button.clicked.connect(self._create_project)
        button_layout.addWidget(create_button)

        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def show_dialog(self):
        dialog_result = self.exec()
        if dialog_result == QDialog.DialogCode.Accepted:
            return ProjectPage.OnEntryData(self._project)
        return None

    def _browse_dataset_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Dataset Directory")
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
            QMessageBox.critical(
                self,
                "Error",
                "Couldn't create project: " + str(e),
                QMessageBox.StandardButton.Close
            )

    def _validate(self):
        errors = dict(filter(None, [
            validate_required_field(self._name_line_edit.text(), "Name"),
            validate_required_directory(self._dataset_directory_line_edit.text(), "Dataset directory")
        ]))
        return errors
