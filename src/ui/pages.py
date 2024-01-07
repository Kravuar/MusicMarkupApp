import sys
from dataclasses import dataclass
from pathlib import Path
from bidict import bidict

from src.app.form_validation import show_error_message, validate_required_field, validate_required_directory
from src.app.markup_index import NonLabeledMarkupIterator, MarkupIterator, MarkupIteratorFilterMode, \
    MarkupIteratorOrderMode
from src.ui.dialogs import ProjectCreationDialog, OpenExistingProjectDialog
from typing import Any

from PyQt5 import QtWidgets, QtCore

from src.app.project import Project
from src.config import PROJECT_FILE_SUFFIX


@dataclass
class GotoPayload:
    name: str
    data: Any = None


class WindowPage(QtWidgets.QWidget):
    goto_signal = QtCore.pyqtSignal(GotoPayload)

    def __init__(self):
        super().__init__()

    def on_enter(self, data: Any):
        pass

    def _goto(self, name: str, data: Any = None):
        self.goto_signal.emit(GotoPayload(name, data))


class MainPage(WindowPage):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome")

        # Layout
        layout = QtWidgets.QVBoxLayout(self)

        # Buttons
        buttons_layout = QtWidgets.QVBoxLayout()

        create_project_button = QtWidgets.QPushButton("Create New Project", self)
        create_project_button.clicked.connect(self._on_create)
        buttons_layout.addWidget(create_project_button)

        open_project_button = QtWidgets.QPushButton("Open Existing Project", self)
        open_project_button.clicked.connect(self._on_open_existing)
        buttons_layout.addWidget(open_project_button)

        exit_button = QtWidgets.QPushButton("Exit", self)
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
        QtWidgets.QApplication.instance().exit(0)


class ProjectPage(WindowPage):
    _DEFAULT_ORDER_MODE = MarkupIteratorOrderMode.UNORDERED
    _DEFAULT_FILTER_MODE = MarkupIteratorFilterMode.NON_LABELED
    _SAVE_AS_FILE_FILTER = f"MM Project (*{PROJECT_FILE_SUFFIX});;All Files (*)"

    def __init__(self):
        super().__init__()

        # State
        self._project: Project | None = None
        self._project_path: Path | None = None
        self._iterator: MarkupIterator | None = None
        self._current_iteration_data = None

        # Layout
        layout = QtWidgets.QVBoxLayout(self)

        # Tabs
        tabs = QtWidgets.QTabWidget(self)
        layout.addWidget(tabs)

        # Project Details Tab
        details_tab_scroll = QtWidgets.QScrollArea(self)
        details_tab_scroll.setWidgetResizable(True)
        project_details_tab = QtWidgets.QWidget(details_tab_scroll)
        details_tab_scroll.setWidget(project_details_tab)

        tabs.addTab(details_tab_scroll, "Project Details")

        # Project Details Layout
        project_details_layout = QtWidgets.QVBoxLayout(project_details_tab)
        project_details_tab.setLayout(project_details_layout)

        # Project Name
        project_name_label = QtWidgets.QLabel("Project Name:", project_details_tab)
        self._project_name_line_edit = QtWidgets.QLineEdit(project_details_tab)
        project_details_layout.addWidget(project_name_label)
        project_details_layout.addWidget(self._project_name_line_edit)

        # Description
        project_description_label = QtWidgets.QLabel("Description:", project_details_tab)
        self._project_description_line_edit = QtWidgets.QTextEdit(project_details_tab)
        project_details_layout.addWidget(project_description_label)
        project_details_layout.addWidget(self._project_description_line_edit)

        # Detail tab buttons
        detail_tab_button_layout = QtWidgets.QHBoxLayout(project_details_tab)

        exit_button = QtWidgets.QPushButton("Close Project", self)
        exit_button.clicked.connect(self._close_project)
        detail_tab_button_layout.addWidget(exit_button)

        detail_tab_save_button = QtWidgets.QPushButton("Save", project_details_tab)
        detail_tab_save_button.clicked.connect(lambda: self._save_project(in_existing=True))
        detail_tab_button_layout.addWidget(detail_tab_save_button)

        detail_tab_save_as_button = QtWidgets.QPushButton("Save As", project_details_tab)
        detail_tab_save_as_button.clicked.connect(lambda: self._save_project(in_existing=False))
        detail_tab_button_layout.addWidget(detail_tab_save_as_button)

        export_markup_button = QtWidgets.QPushButton("Export Markup", project_details_tab)
        export_markup_button.clicked.connect(self._export_markup)
        detail_tab_button_layout.addWidget(export_markup_button)

        project_details_layout.addLayout(detail_tab_button_layout)

        # Markup Tab
        markup_tab_scroll = QtWidgets.QScrollArea(self)
        markup_tab_scroll.setWidgetResizable(True)
        markup_tab = QtWidgets.QWidget(markup_tab_scroll)
        markup_tab_scroll.setWidget(markup_tab)

        tabs.addTab(markup_tab_scroll, "Markup")

        # Markup Layout
        markup_layout = QtWidgets.QVBoxLayout(markup_tab)
        markup_tab.setLayout(markup_layout)

        # TODO: visualize audio file, play button and stuff
        # Entry info
        entry_info_label = QtWidgets.QLabel("Entry Info:", markup_tab)
        self._data_info = QtWidgets.QLabel(markup_tab)
        markup_layout.addWidget(entry_info_label)
        markup_layout.addWidget(self._data_info)

        # Description input
        description_label = QtWidgets.QLabel("Description:", markup_tab)
        self._description_input_text_edit = QtWidgets.QTextEdit(markup_tab)
        self._description_input_text_edit.setMinimumHeight(300)
        markup_layout.addWidget(description_label)
        markup_layout.addWidget(self._description_input_text_edit)

        # Navigation Buttons
        buttons_layout = QtWidgets.QHBoxLayout(markup_tab)

        markup_tab_save_button = QtWidgets.QPushButton("Save", markup_tab)
        markup_tab_save_button.clicked.connect(self._save_markup)
        buttons_layout.addWidget(markup_tab_save_button)

        skip_button = QtWidgets.QPushButton("Skip", markup_tab)
        skip_button.clicked.connect(self._move_next)
        buttons_layout.addWidget(skip_button)

        markup_layout.addLayout(buttons_layout)

        # TODO: Display existing descriptions from dataframe

        # Markup Settings Tab
        markup_settings_tab_scroll = QtWidgets.QScrollArea(self)
        markup_settings_tab_scroll.setWidgetResizable(True)
        markup_settings_tab = QtWidgets.QWidget(markup_settings_tab_scroll)
        markup_settings_tab_scroll.setWidget(markup_settings_tab)

        tabs.addTab(markup_settings_tab_scroll, "Markup Settings")

        # Markup Settings Layout
        markup_settings_layout = QtWidgets.QVBoxLayout(markup_settings_tab)
        markup_settings_tab.setLayout(markup_settings_layout)

        # Iteration Order Mode (Ordered/Unordered)
        order_mode_button_layout = QtWidgets.QHBoxLayout(markup_settings_tab)

        self._iteration_order_mode_toggle_group = QtWidgets.QButtonGroup(markup_settings_tab)
        iteration_mode_label = QtWidgets.QLabel("Iteration Order Mode:", markup_settings_tab)
        order_mode_button_layout.addWidget(iteration_mode_label)
        self._iteration_order_mode_button_mapping = bidict()

        ordered_mode_name = "Ordered"
        ordered_radio_button = QtWidgets.QRadioButton(ordered_mode_name, markup_settings_tab)
        self._iteration_order_mode_toggle_group.addButton(ordered_radio_button, 1)
        self._iteration_order_mode_button_mapping[1] = MarkupIteratorOrderMode.ORDERED
        order_mode_button_layout.addWidget(ordered_radio_button)

        unordered_mode_name = "Unordered"
        unordered_radio_button = QtWidgets.QRadioButton(unordered_mode_name, markup_settings_tab)
        self._iteration_order_mode_toggle_group.addButton(unordered_radio_button, 2)
        self._iteration_order_mode_button_mapping[2] = MarkupIteratorOrderMode.UNORDERED
        order_mode_button_layout.addWidget(unordered_radio_button)

        markup_settings_layout.addLayout(order_mode_button_layout)

        self._iteration_order_mode_toggle_group.buttonClicked[int].connect(self._order_mode_changed)
        default_order_button_id = self._iteration_order_mode_button_mapping.inverse[ProjectPage._DEFAULT_ORDER_MODE]
        self._iteration_order_mode_toggle_group.button(default_order_button_id).toggle()

        # Iteration Filter Mode (All/Non Labeled)
        filter_mode_button_layout = QtWidgets.QHBoxLayout(markup_settings_tab)

        self._iteration_filter_mode_toggle_group = QtWidgets.QButtonGroup(markup_settings_tab)
        iteration_mode_label = QtWidgets.QLabel("Iteration Filter Mode:", markup_settings_tab)
        filter_mode_button_layout.addWidget(iteration_mode_label)
        self._iteration_filter_mode_button_mapping = bidict()

        non_filtered_mode_name = "All entries"
        non_filtered_radio_button = QtWidgets.QRadioButton(non_filtered_mode_name, markup_settings_tab)
        self._iteration_filter_mode_toggle_group.addButton(non_filtered_radio_button, 1)
        self._iteration_filter_mode_button_mapping[1] = MarkupIteratorFilterMode.ALL
        filter_mode_button_layout.addWidget(non_filtered_radio_button)

        non_labeled_filter_mode_name = "Non Labeled"
        non_labeled_filter_radio_button = QtWidgets.QRadioButton(non_labeled_filter_mode_name, markup_settings_tab)
        self._iteration_filter_mode_toggle_group.addButton(non_labeled_filter_radio_button, 2)
        self._iteration_filter_mode_button_mapping[2] = MarkupIteratorFilterMode.NON_LABELED
        filter_mode_button_layout.addWidget(non_labeled_filter_radio_button)

        markup_settings_layout.addLayout(filter_mode_button_layout)

        self._iteration_filter_mode_toggle_group.buttonClicked[int].connect(self._filter_mode_changed)
        default_filter_button_id = self._iteration_filter_mode_button_mapping.inverse[ProjectPage._DEFAULT_FILTER_MODE]
        self._iteration_filter_mode_toggle_group.button(default_filter_button_id).toggle()

    def on_enter(self, data):
        if isinstance(data, tuple):
            project, path = tuple
            if not isinstance(project, Project) or not isinstance(path, Path):
                raise ValueError("Tuple must contain a Project and its Path.")
            self._project = project
            self._project_path = path
        else:
            if not isinstance(data, Project):
                raise ValueError("Data should be a Project instance.")
            self._project = data
            self._project_path = None

        self._project_name_line_edit.setText(self._project.name)
        self._project_description_line_edit.setPlainText(self._project.description)
        self.setWindowTitle(f"Project | {self._project.name}")  # TODO: huh?

        # TODO: Persist iterator
        self._iterator = self._project.get_dataset_iterator(ProjectPage._DEFAULT_FILTER_MODE, ProjectPage._DEFAULT_ORDER_MODE)

        self._move_next()

    def _move_next(self):
        if self._iterator.remaining == 0:
            decision = QtWidgets.QMessageBox.question(
                self,
                "Dataset is exhausted",
                "Dataset is fully labeled, do you want to switch no infinite mode?",
                QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No
            )
            if decision == QtWidgets.QMessageBox.Yes:
                button_id = self._iteration_filter_mode_button_mapping.inverse[MarkupIteratorFilterMode.ALL]
                self._iteration_filter_mode_toggle_group.button(button_id).toggle()
        self._current_iteration_data = next(self._iterator)

        # TODO: better info
        checksum, relative_path, *other = self._current_iteration_data
        self._data_info.setText(f"Checksum: {checksum}, Relative Path: {relative_path}")

    def _save_project(self, in_existing: bool):
        validation_errors = dict(filter(None, [
            validate_required_field(self._project_name_line_edit.text(), "Name"),
            validate_required_field(self._project_description_line_edit.toPlainText(), "Description"),
        ]))
        if validation_errors:
            show_error_message(validation_errors, self)
            return

        if in_existing and not self._project_path:
            QtWidgets.QMessageBox.critical(
                self,
                "Project Saving Error",
                "This project doesn't have an associated file. Please select a file to save it.",
                QtWidgets.QMessageBox.Ok
            )

        if in_existing and self._project_path:
            path = self._project_path
        else:
            path = Path(QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Save As",
                filter=ProjectPage._SAVE_AS_FILE_FILTER
            )[0])

        self._project.name = self._project_name_line_edit.text()
        self._project.description = self._project_description_line_edit.toPlainText()
        try:
            self._project.save(path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Project Saving Error",
                str(e),
                QtWidgets.QMessageBox.Ok
            )

    def _export_markup(self):
        # TODO: Retrieve dir path from dialog
        # self._project.export_markup(path)
        pass

    def _save_markup(self):
        validation_errors = dict(filter(None, [
            validate_required_field(self._description_input_text_edit.toPlainText(), "Description"),
        ]))
        if validation_errors:
            show_error_message(validation_errors, self)
            return

        checksum, relative_path, *other = self._current_iteration_data
        start = 0  # TODO: yeah, todo this
        end = 0  #
        self._project.add_entry(checksum, relative_path, start, end, self._description_input_text_edit.text())
        
        if isinstance(self._iterator, NonLabeledMarkupIterator):
            mark_labeled_callback = other[0]
            mark_labeled_callback()
            
        self._move_next()

    def _order_mode_changed(self, order_mode_id):
        self._iterator.mode = self._iteration_order_mode_button_mapping[order_mode_id]

    def _filter_mode_changed(self, filter_mode_id):
        filter_mode = self._iteration_filter_mode_button_mapping[filter_mode_id]
        order_mode_id = self._iteration_order_mode_toggle_group.checkedId()
        order_mode = self._iteration_order_mode_button_mapping[order_mode_id]
        self._iterator = self._project.get_dataset_iterator(filter_mode, order_mode)

    def _close_project(self):
        # TODO: Ask only if changes were made
        message_box = QtWidgets.QMessageBox(self)
        message_box.setWindowTitle("Closing Project")
        message_box.setText("All progress will be lost. Do you want to save this project before closing it?")
        message_box.addButton(QtWidgets.QMessageBox.Save)
        message_box.addButton("Save As", QMessageBox.YesRole)
        message_box.addButton(QtWidgets.QMessageBox.No)
        message_box.addButton(QtWidgets.QMessageBox.Cancel)

        answer = message_box.exec_()
        if answer == QMessageBox.Save:
            print('save')
            # self._save_project(in_existing=True)
        elif message_box.clickedButton().text() == "Save As":
            print('save as')
            # self._save_project(in_existing=False)
        elif answer == QMessageBox.Cancel:
            return
        self._project = None
        self._project_path = None
        self.goto("main")
