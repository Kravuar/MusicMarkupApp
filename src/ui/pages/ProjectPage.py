from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Type

from PySide6.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QPushButton, QTabWidget, QScrollArea, \
    QLabel, QLineEdit, QTextEdit, QHBoxLayout, QFormLayout, QComboBox, QFileDialog

from src.app.form_validation import show_error_message, validate_required_field
from src.app.markup_data import MarkupValue
from src.app.markup_iterator import MarkupIterator
from src.app.markup_settings import IterationSettings, SettingsEnum
from src.app.project import Project
from src.config import SAVE_PROJECT_AS_FILE_FILTER, SAVE_DATAFRAME_AS_FILE_FILTER
from src.ui.pages.WindowPage import WindowPage


class ProjectPage(WindowPage):
    @dataclass
    class EntryData:
        project: Project
        path: Optional[Path] = None

    def __init__(self):
        super().__init__()

        # State
        self._project: Optional[Project] = None
        self._project_path: Optional[Path] = None
        self._iterator: Optional[MarkupIterator] = None

        # Layout
        layout = QVBoxLayout(self)

        # Tabs
        tabs = QTabWidget(self)
        layout.addWidget(tabs)

        # Markup Tab
        markup_tab_scroll = QScrollArea(self)
        markup_tab_scroll.setWidgetResizable(True)
        markup_tab = QWidget(markup_tab_scroll)
        markup_tab_scroll.setWidget(markup_tab)

        tabs.addTab(markup_tab_scroll, "Markup")

        # Markup Layout
        markup_layout = QVBoxLayout(markup_tab)
        markup_tab.setLayout(markup_layout)

        # TODO: visualize audio file, play button and stuff
        # Entry info
        entry_info_label = QLabel("Entry Info:", markup_tab)
        self._data_info = QLabel(markup_tab)
        markup_layout.addWidget(entry_info_label)
        markup_layout.addWidget(self._data_info)

        # Description input
        description_label = QLabel("Description:", markup_tab)
        self._description_input_text_edit = QTextEdit(markup_tab)
        self._description_input_text_edit.setMinimumHeight(300)
        markup_layout.addWidget(description_label)
        markup_layout.addWidget(self._description_input_text_edit)

        # Navigation Buttons
        buttons_layout = QHBoxLayout(markup_tab)

        markup_tab_save_button = QPushButton("Save", markup_tab)
        markup_tab_save_button.clicked.connect(self._save_markup)
        buttons_layout.addWidget(markup_tab_save_button)

        next_button = QPushButton("Next", markup_tab)
        next_button.clicked.connect(self._move_next)
        buttons_layout.addWidget(next_button)

        markup_layout.addLayout(buttons_layout)

        # TODO: Display existing descriptions from dataframe

        # Markup Settings Tab
        markup_settings_tab_scroll = QScrollArea(self)
        markup_settings_tab_scroll.setWidgetResizable(True)
        markup_settings_tab = QWidget(markup_settings_tab_scroll)
        markup_settings_tab_scroll.setWidget(markup_settings_tab)

        tabs.addTab(markup_settings_tab_scroll, "Markup Settings")

        # Markup Settings Layout
        markup_settings_layout = QFormLayout(self)
        markup_settings_tab.setLayout(markup_settings_layout)

        # Iteration Order Mode
        self._order_mode_combobox = self._create_combobox(IterationSettings.OrderBy)
        markup_settings_layout.addRow("Iteration Order Mode:", self._order_mode_combobox)

        # Iteration Filter Mode
        self._filter_mode_combobox = self._create_combobox(IterationSettings.Filters)
        markup_settings_layout.addRow("Iteration Filter Mode:", self._filter_mode_combobox)

        # Iteration Index Mode
        self._index_mode_combobox = self._create_combobox(IterationSettings.Index)
        markup_settings_layout.addRow("Iteration Index Mode:", self._index_mode_combobox)

        # Project Details Tab
        details_tab_scroll = QScrollArea(self)
        details_tab_scroll.setWidgetResizable(True)
        project_details_tab = QWidget(details_tab_scroll)
        details_tab_scroll.setWidget(project_details_tab)

        tabs.addTab(details_tab_scroll, "Project Details")

        # Project Details Layout
        project_details_layout = QVBoxLayout(project_details_tab)
        project_details_tab.setLayout(project_details_layout)

        # Project Name
        project_name_label = QLabel("Project Name:", project_details_tab)
        self._project_name_line_edit = QLineEdit(project_details_tab)
        project_details_layout.addWidget(project_name_label)
        project_details_layout.addWidget(self._project_name_line_edit)

        # Description
        project_description_label = QLabel("Description:", project_details_tab)
        self._project_description_line_edit = QTextEdit(project_details_tab)
        project_details_layout.addWidget(project_description_label)
        project_details_layout.addWidget(self._project_description_line_edit)

        # Detail tab buttons
        detail_tab_button_layout = QHBoxLayout(project_details_tab)

        exit_button = QPushButton("Close Project", self)
        exit_button.clicked.connect(self._close_project)
        detail_tab_button_layout.addWidget(exit_button)

        detail_tab_save_button = QPushButton("Save", project_details_tab)
        detail_tab_save_button.clicked.connect(lambda: self._save_project(in_existing=True))
        detail_tab_button_layout.addWidget(detail_tab_save_button)

        detail_tab_save_as_button = QPushButton("Save As", project_details_tab)
        detail_tab_save_as_button.clicked.connect(lambda: self._save_project(in_existing=False))
        detail_tab_button_layout.addWidget(detail_tab_save_as_button)

        export_markup_button = QPushButton("Export Markup", project_details_tab)
        export_markup_button.clicked.connect(self._export_markup)
        detail_tab_button_layout.addWidget(export_markup_button)

        project_details_layout.addLayout(detail_tab_button_layout)

    def on_enter(self, data: EntryData):
        self._project = data.project
        self._project_path = data.path

        self._project_name_line_edit.setText(self._project.name)
        self._project_description_line_edit.setPlainText(self._project.description)
        self.setWindowTitle(f"Project | {self._project.name}")  # TODO: huh?

        self._iterator = self._project.get_dataset_iterator()

        self._move_next()

    def _create_combobox(self, settings_enum: Type[SettingsEnum]):
        combobox = QComboBox(self)
        for entry in settings_enum():
            combobox.addItem(entry.display_name, entry.value)
        combobox.currentIndexChanged.connect(self._settings_changed)
        return combobox

    def _settings_changed(self):
        order_mode = self._order_mode_combobox.currentData()
        filter_mode = self._filter_mode_combobox.currentData()
        index_mode = self._index_mode_combobox.currentData()

        self._project.markup_settings.iteration_settings.order_by = order_mode
        self._project.markup_settings.iteration_settings.filter_predicate = filter_mode
        self._project.markup_settings.iteration_settings.index_callback = index_mode

    def _move_next(self):
        if not self._iterator.next():
            QMessageBox.question(
                self,
                "Dataset is exhausted",
                "Dataset is fully exhausted, you may try to change iteration settings in order to find more entries.",
                QMessageBox.StandardButton.Ok
            )
        else:
            self._display_entry()

    def _display_entry(self):
        # TODO: better info
        checksum = self._iterator.last_accessed_entry.checksum
        relative_path = self._iterator.last_accessed_entry.entry.entry_info.relative_path
        self._data_info.setText(
            f"Checksum: {checksum}, Relative Path: {relative_path}"
        )

    def _save_project(self, in_existing: bool):
        validation_errors = dict(filter(None, [
            validate_required_field(self._project_name_line_edit.text(), "Name"),
            validate_required_field(self._project_description_line_edit.toPlainText(), "Description"),
        ]))
        if validation_errors:
            show_error_message(validation_errors, self)
            return

        if in_existing and not self._project_path:
            QMessageBox.critical(
                self,
                "Project Saving Error",
                "This project doesn't have an associated file. Please select a file to save it.",
                QMessageBox.StandardButton.Ok
            )

        if in_existing and self._project_path:
            path = self._project_path
        else:
            path = Path(QFileDialog.getSaveFileName(
                self,
                "Save Project As",
                filter=SAVE_PROJECT_AS_FILE_FILTER
            )[0])

        self._project.name = self._project_name_line_edit.text()
        self._project.description = self._project_description_line_edit.toPlainText()
        try:
            self._project.save(path)
            self._project_path = path
        except Exception as e:
            QMessageBox.critical(
                self,
                "Project Saving Error",
                str(e),
                QMessageBox.StandardButton.Ok
            )

    def _export_markup(self):
        path = Path(QFileDialog.getSaveFileName(
            self,
            "Save Markup As",
            filter=SAVE_DATAFRAME_AS_FILE_FILTER
        )[0])
        try:
            self._project.export_markup(path)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Markup Export Error",
                str(e),
                QMessageBox.StandardButton.Ok
            )

    def _update_markup(self, label_idx: int):
        validation_errors = dict(filter(None, [
            validate_required_field(self._description_input_text_edit.toPlainText(), "Description"),
            # validate_non_equal_fields(self._fragment_start, self._fragment_end, "Fragment Start", "Fragment End")
        ]))
        if validation_errors:
            show_error_message(validation_errors, self)
            return

        start = 0  # TODO: yeah, todo this
        end = 0  #

        self._project.markup_data.update(
            self._iterator.last_accessed_entry.checksum,
            label_idx,
            MarkupValue(
                start,
                end,
                self._description_input_text_edit.toPlainText()
            )
        )
        self._display_entry()

    def _save_markup(self):
        validation_errors = dict(filter(None, [
            validate_required_field(self._description_input_text_edit.toPlainText(), "Description"),
            # validate_non_equal_fields(self._fragment_start, self._fragment_end, "Fragment Start", "Fragment End")
        ]))
        if validation_errors:
            show_error_message(validation_errors, self)
            return

        start = 0  # TODO: yeah, todo this
        end = 0  #

        self._project.markup_data.add(
            self._iterator.last_accessed_entry.checksum,
            MarkupValue(
                start,
                end,
                self._description_input_text_edit.toPlainText()
            )
        )
        self._display_entry()

    def _delete_markup(self, label_idx: int):
        self._project.markup_data.delete(
            self._iterator.last_accessed_entry.checksum,
            label_idx
        )
        self._display_entry()

    def _close_project(self):
        # TODO: Ask only if changes were made
        message_box = QMessageBox(self)
        message_box.setWindowTitle("Closing Project")
        message_box.setText("All progress will be lost. Do you want to save this project before closing it?")
        message_box.addButton(QMessageBox.StandardButton.Save)
        message_box.addButton("Save As", QMessageBox.ButtonRole.YesRole)
        message_box.addButton(QMessageBox.StandardButton.No)
        message_box.addButton(QMessageBox.StandardButton.Cancel)

        answer = message_box.exec()
        if answer == QMessageBox.StandardButton.Save:
            self._save_project(in_existing=True)
        elif message_box.clickedButton().text() == "Save As":
            self._save_project(in_existing=False)
        elif answer == QMessageBox.StandardButton.Cancel:
            return
        self._project = None
        self._project_path = None
        self._goto("main")