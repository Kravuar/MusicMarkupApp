from PyQt5 import QtWidgets
from src.components.PageWindow import PageWindow
from src.components.dialogs.OpenExistingProjectDialog import OpenExistingProjectDialog
from src.components.dialogs.ProjectCreationDialog import ProjectCreationDialog


class MainPage(PageWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Page")

        self.createProjectButton = QtWidgets.QPushButton("Create New Project", self)
        self.createProjectButton.clicked.connect(self.onCreate)

        self.openProjectButton = QtWidgets.QPushButton("Open Existing Project", self)
        self.openProjectButton.clicked.connect(self.onOpenExisting)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.createProjectButton)
        self.layout.addWidget(self.openProjectButton)
        self.layout.addStretch()

    def onCreate(self):
        project_creation_dialog = ProjectCreationDialog(self)
        result = project_creation_dialog.showDialog()
        if result:
            self.goto("project")

    def onOpenExisting(self):
        open_existing_dialog = OpenExistingProjectDialog(self)
        result = open_existing_dialog.showDialog()
        if result:
            print("Project Opened:", result.path)
            self.goto("project")
