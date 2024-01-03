from PyQt5 import QtWidgets
from src.components.widgets.dialogs.OpenExistingProjectDialog import OpenExistingProjectDialog
from src.components.widgets.dialogs.ProjectCreationDialog import ProjectCreationDialog
from src.components.widgets.multipage.WindowPage import WindowPage


class MainPage(WindowPage):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome")

        # Layout
        self.layout = QtWidgets.QVBoxLayout(self)

        # Buttons
        buttonsLayout = QtWidgets.QVBoxLayout()

        self.createProjectButton = QtWidgets.QPushButton("Create New Project", self)
        self.createProjectButton.clicked.connect(self.onCreate)
        buttonsLayout.addWidget(self.createProjectButton)

        self.openProjectButton = QtWidgets.QPushButton("Open Existing Project", self)
        self.openProjectButton.clicked.connect(self.onOpenExisting)
        buttonsLayout.addWidget(self.openProjectButton)

        self.layout.addLayout(buttonsLayout)

    def onCreate(self):
        project_creation_dialog = ProjectCreationDialog(self)
        result = project_creation_dialog.showDialog()
        if result:
            self.goto("project", result)

    def onOpenExisting(self):
        open_existing_dialog = OpenExistingProjectDialog(self)
        result = open_existing_dialog.showDialog()
        if result:
            self.goto("project", result)
