from dataclasses import dataclass

from PySide6.QtWidgets import QVBoxLayout, QPushButton, QApplication

from src.ui.dialogs.OpenExistingProjectDialog import OpenExistingProjectDialog
from src.ui.dialogs.ProjectCreationDialog import ProjectCreationDialog
from src.ui.pages.ProjectPage import WindowPage


class MainPage(WindowPage):
    @dataclass
    class EntryData:
        pass

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome")
        self.resize(300, 300)

        # Layout
        layout = QVBoxLayout(self)

        # Buttons
        buttons_layout = QVBoxLayout()

        open_project_button = QPushButton("Open Existing Project", self)
        open_project_button.clicked.connect(self._on_open_existing)
        buttons_layout.addWidget(open_project_button)

        create_project_button = QPushButton("Create New Project", self)
        create_project_button.clicked.connect(self._on_create)
        buttons_layout.addWidget(create_project_button)

        exit_button = QPushButton("Exit", self)
        exit_button.clicked.connect(MainPage._on_exit)
        buttons_layout.addWidget(exit_button)

        layout.addLayout(buttons_layout)

    def _on_create(self):
        project_creation_dialog = ProjectCreationDialog(self)
        result = project_creation_dialog.show_dialog()
        if result:
            self._goto("project", result)

    def _on_open_existing(self):
        open_existing_dialog = OpenExistingProjectDialog(self)
        result = open_existing_dialog.show_dialog()
        if result:
            self._goto("project", result)

    @staticmethod
    def _on_exit():
        QApplication.instance().exit(0)
