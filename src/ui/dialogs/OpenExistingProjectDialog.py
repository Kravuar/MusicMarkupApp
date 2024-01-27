from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, \
    QMessageBox

from src.app.form_validation import show_error_message, validate_required_file
from src.app.project import Project
from src.config import PROJECT_FILE_SUFFIX
from src.ui.pages.ProjectPage import ProjectPage


class OpenExistingProjectDialog(QDialog):
    _PROJECT_FILE_FILTER = f"MM Project (*{PROJECT_FILE_SUFFIX});;All Files (*)"

    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)
        self.setWindowTitle("Open Project")

        # State
        self._project: Project | None = None
        self._path: Path | None = None

        # Window size
        self.setMinimumWidth(700)

        # Layout
        layout = QVBoxLayout(self)

        # Project file
        layout.addWidget(QLabel("Project file:", self))
        self._project_file_line_edit = QLineEdit(self)
        browse_button = QPushButton("Browse", self)
        browse_button.clicked.connect(self._browse_project_file)

        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self._project_file_line_edit)
        dir_layout.addWidget(browse_button)
        layout.addLayout(dir_layout)

        # Buttons
        button_layout = QHBoxLayout()

        open_button = QPushButton("Open", self)
        open_button.clicked.connect(self._open_project)
        button_layout.addWidget(open_button)

        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def show_dialog(self) -> Optional[ProjectPage.EntryData]:
        dialog_result = self.exec()
        if dialog_result == QDialog.DialogCode.Accepted:
            return ProjectPage.EntryData(self._project, self._path)
        return None

    def _browse_project_file(self):
        file, _ = QFileDialog.getOpenFileName(
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
            self._path = Path(self._project_file_line_edit.text())
            self._project = Project.load(self._path)
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                "Couldn't load project: " + str(e),
                QMessageBox.StandardButton.Close
            )

    def _validate(self):
        errors = dict(filter(None, [
            validate_required_file(self._project_file_line_edit.text(), "Project File"),
        ]))
        return errors
