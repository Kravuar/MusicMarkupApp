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
from src.ui.styles import GeneralStyleMixin


@dataclass
class GotoPayload:
    name: str
    data: Any = None


class WindowPage(QtWidgets.QWidget):
    goto_signal = QtCore.pyqtSignal(GotoPayload)

    def __init__(self):
        super().__init__()
        GeneralStyleMixin.apply_style(self)

    def on_enter(self, data: Any):
        pass

    def _on_exit(self):
        pass

    def _goto(self, name: str, data: Any = None):
        self._on_exit()
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


class ProjectPage(WindowPage):
    _DEFAULT_ORDER_MODE = MarkupIteratorOrderMode.UNORDERED
    _DEFAULT_FILTER_MODE = MarkupIteratorFilterMode.NON_LABELED

    def __init__(self):
        super().__init__()

        # State
        self._project: Project | None = None
        self._iterator: MarkupIterator | None = None
        self._current_iteration_data = None

        # Layout
        layout = QtWidgets.QVBoxLayout(self)

        # Tabs
        tabs = QtWidgets.QTabWidget(self)
        layout.addWidget(tabs)

        # Project Details Tab
        project_details_tab = QtWidgets.QWidget(tabs)
        tabs.addTab(project_details_tab, "Project Details")

        # Project Details Layout
        project_details_layout = QtWidgets.QVBoxLayout(project_details_tab)
        project_details_tab.setLayout(project_details_layout)

        project_name_label = QtWidgets.QLabel("Project Name:", project_details_tab)
        self._project_name_line_edit = QtWidgets.QLineEdit(project_details_tab)
        project_details_layout.addWidget(project_name_label)
        project_details_layout.addWidget(self._project_name_line_edit)

        project_description_label = QtWidgets.QLabel("Description:", project_details_tab)
        self._project_description_line_edit = QtWidgets.QTextEdit(project_details_tab)
        project_details_layout.addWidget(project_description_label)
        project_details_layout.addWidget(self._project_description_line_edit)

        layout.addWidget(QtWidgets.QLabel("Project File Path:", self))
        self._project_file_directory_line_edit = QtWidgets.QLineEdit(self)
        browse_button = QtWidgets.QPushButton("Browse", self)
        browse_button.clicked.connect(self._browse_project_file_directory)

        # Detail tab buttons
        detail_tab_button_layout = QtWidgets.QHBoxLayout(project_details_tab)

        detail_tab_save_button = QtWidgets.QPushButton("Save Changes", project_details_tab)
        detail_tab_save_button.clicked.connect(self._save_details)
        detail_tab_button_layout.addWidget(detail_tab_save_button)

        export_markup_button = QtWidgets.QPushButton("Export Markup", project_details_tab)
        export_markup_button.clicked.connect(self._export_markup)
        detail_tab_button_layout.addWidget(export_markup_button)

        project_details_layout.addLayout(detail_tab_button_layout)

        # Markup Tab
        markup_tab = QtWidgets.QWidget(tabs)
        tabs.addTab(markup_tab, "Markup")

        # Markup Layout
        markup_layout = QtWidgets.QVBoxLayout(markup_tab)
        markup_tab.setLayout(markup_layout)

        # TODO: visualize audio file, play button and stuff
        # Entry info
        entry_info_label = QtWidgets.QLabel("Entry Info:", markup_tab)
        self._data_info = QtWidgets.QLabel(markup_tab)
        markup_layout.addWidget(entry_info_label)
        markup_layout.addWidget(self._data_info)

        # Iteration Order Mode (Ordered/Unordered)
        self._iteration_order_mode_toggle_group = QtWidgets.QButtonGroup(markup_tab)
        iteration_mode_label = QtWidgets.QLabel("Iteration Order Mode:", markup_tab)
        markup_layout.addWidget(iteration_mode_label)
        self._iteration_order_mode_button_mapping = bidict()

        ordered_mode_name = "Ordered"
        ordered_radio_button = QtWidgets.QRadioButton(ordered_mode_name, markup_tab)
        self._iteration_order_mode_toggle_group.addButton(ordered_radio_button, 1)
        self._iteration_order_mode_button_mapping[1] = MarkupIteratorOrderMode.ORDERED
        markup_layout.addWidget(ordered_radio_button)

        unordered_mode_name = "Unordered"
        unordered_radio_button = QtWidgets.QRadioButton(unordered_mode_name, markup_tab)
        self._iteration_order_mode_toggle_group.addButton(unordered_radio_button, 2)
        self._iteration_order_mode_button_mapping[2] = MarkupIteratorOrderMode.UNORDERED
        markup_layout.addWidget(unordered_radio_button)

        self._iteration_order_mode_toggle_group.buttonClicked[int].connect(self._order_mode_changed)
        default_order_button_id = self._iteration_order_mode_button_mapping.inverse[ProjectPage._DEFAULT_ORDER_MODE]
        self._iteration_order_mode_toggle_group.button(default_order_button_id).toggle()

        # Iteration Filter Mode (All/Non Labeled)
        self._iteration_filter_mode_toggle_group = QtWidgets.QButtonGroup(markup_tab)
        iteration_mode_label = QtWidgets.QLabel("Iteration Filter Mode:", markup_tab)
        markup_layout.addWidget(iteration_mode_label)
        self._iteration_filter_mode_button_mapping = bidict()

        non_filtered_mode_name = "All entries"
        non_filtered_radio_button = QtWidgets.QRadioButton(non_filtered_mode_name, markup_tab)
        self._iteration_filter_mode_toggle_group.addButton(non_filtered_radio_button, 1)
        self._iteration_filter_mode_button_mapping[1] = MarkupIteratorFilterMode.ALL
        markup_layout.addWidget(non_filtered_radio_button)

        non_labeled_filter_mode_name = "Non Labeled"
        non_labeled_filter_radio_button = QtWidgets.QRadioButton(non_labeled_filter_mode_name, markup_tab)
        self._iteration_filter_mode_toggle_group.addButton(non_labeled_filter_radio_button, 2)
        self._iteration_filter_mode_button_mapping[2] = MarkupIteratorFilterMode.NON_LABELED
        markup_layout.addWidget(non_labeled_filter_radio_button)

        self._iteration_filter_mode_toggle_group.buttonClicked[int].connect(self._filter_mode_changed)
        default_filter_button_id = self._iteration_filter_mode_button_mapping.inverse[ProjectPage._DEFAULT_FILTER_MODE]
        self._iteration_filter_mode_toggle_group.button(default_filter_button_id).toggle()

        # Description input
        description_label = QtWidgets.QLabel("Description:", markup_tab)
        self._description_input_line_edit = QtWidgets.QLineEdit(markup_tab)
        markup_layout.addWidget(description_label)
        markup_layout.addWidget(self._description_input_line_edit)

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

    def on_enter(self, data):
        try:
            if not isinstance(data, Project):
                raise TypeError("Data must be of a Project type.")
            self._project = data

            self._project_name_line_edit.setText(self._project.name)
            self._project_description_line_edit.setPlainText(self._project.description)
            self._project_file_directory_line_edit.setText(str(self._project.project_file))

            # TODO: Persist iterator
            self._iterator = self._project.get_dataset_iterator(ProjectPage._DEFAULT_FILTER_MODE, ProjectPage._DEFAULT_ORDER_MODE)

            self._move_next()
        except Exception as e:
            print(e)

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

    def _save_details(self):
        errors = self._validate_details()
        if errors:
            show_error_message(errors, self)
            return

        self._project.name = self._project_name_line_edit.text()
        self._project.description = self._project_description_line_edit.toPlainText()
        self._project.project_file = Path(self._project_file_directory_line_edit.text())

        self._project.save()

    def _export_markup(self):
        # TODO: Retrieve dir path from dialog
        # self._project.export_markup(path)
        pass

    def _save_markup(self):
        errors = self._validate_markup()
        if errors:
            show_error_message(errors, self)
            return

        checksum, relative_path, *other = self._current_iteration_data
        start = 0  # TODO: yeah, todo this
        end = 0  #
        self._project.add_entry(checksum, relative_path, start, end, self._description_input_line_edit.text())
        
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

    def _browse_project_file_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Project File Directory")
        if directory:
            self._project_file_directory_line_edit.setText(directory)

    def _validate_markup(self):
        errors = dict(filter(None, [
            validate_required_field(self._description_input_line_edit.text(), "Description"),
        ]))
        return errors

    def _validate_details(self):
        errors = dict(filter(None, [
            validate_required_field(self._project_name_line_edit.text(), "Name"),
            validate_required_field(self._project_description_line_edit.toPlainText(), "Description"),
            validate_required_directory(self._project_file_directory_line_edit.text(), "Project File Directory"),
        ]))
        return errors
