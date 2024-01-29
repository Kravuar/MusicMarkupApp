from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Type

from PySide6.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QPushButton, QTabWidget, QScrollArea, \
    QLabel, QLineEdit, QTextEdit, QHBoxLayout, QFormLayout, QComboBox, QFileDialog, QGroupBox

from src.app.form_validation import show_error_message, validate_required_field
from src.app.markup_data import MarkupValue
from src.app.markup_iterator import MarkupIterator
from src.app.markup_settings import IterationSettings, SettingsEnum
from src.app.project import Project
from src.config import SAVE_PROJECT_AS_FILE_FILTER, SAVE_DATAFRAME_AS_FILE_FILTER
from src.ui.components.MarkupContainer import MarkupContainerWidget
from src.ui.components.MarkupEntriesList import MarkupEntriesWidget
from src.ui.components.MusicPlayer import AudioPlayerWidget
from src.ui.components.RangeSlider import LabeledRangeSlider
from src.ui.pages.WindowPage import WindowPage


def _time_label_mapper(time_in_ms: int):
    seconds = int(time_in_ms / 1000)
    minutes = int(seconds / 60)
    seconds -= minutes * 60
    return f'{minutes:02d}:{seconds:02d}'


class ProjectPage(WindowPage):
    @dataclass
    class OnEntryData:
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
        self.tabs = QTabWidget(self)
        exit_button = QPushButton('Close', self)
        exit_button.clicked.connect(self._close_project)
        self.tabs.setCornerWidget(exit_button)
        layout.addWidget(self.tabs)

        # Markup Tab
        markup_tab_scroll = QScrollArea(self)
        markup_tab_scroll.setWidgetResizable(True)
        markup_tab = QWidget(markup_tab_scroll)
        markup_tab_scroll.setWidget(markup_tab)

        self.tabs.addTab(markup_tab_scroll, "Markup")

        # Markup Layout
        markup_layout = QVBoxLayout(markup_tab)
        markup_tab.setLayout(markup_layout)

        # Entry info
        entry_info_group_box = QGroupBox('Current', self)
        entry_info_layout = QVBoxLayout(entry_info_group_box)

        self._entry_info = QLabel(markup_tab)
        entry_info_layout.addWidget(self._entry_info)

        # Playback Player
        self._player = AudioPlayerWidget(_time_label_mapper, self)
        entry_info_layout.addWidget(self._player)

        entry_info_group_box.setLayout(entry_info_layout)
        markup_layout.addWidget(entry_info_group_box)

        # Range Selection Slider
        range_selection_group_box = QGroupBox('Range Selection', self)
        range_slider_layout = QVBoxLayout(range_selection_group_box)

        self._range_slider = LabeledRangeSlider(_time_label_mapper, parent=self)
        range_slider_layout.addWidget(self._range_slider)

        range_selection_group_box.setLayout(range_slider_layout)
        markup_layout.addWidget(range_selection_group_box)

        self._player.durationChanged.connect(self._media_changed)

        # Description input
        description_group_box = QGroupBox('Description', self)
        description_layout = QVBoxLayout(description_group_box)

        self._description_input_text_edit = QTextEdit(markup_tab)
        self._description_input_text_edit.setMinimumHeight(250)
        description_layout.addWidget(self._description_input_text_edit)

        description_group_box.setLayout(description_layout)
        markup_layout.addWidget(description_group_box)

        # Navigation Buttons
        buttons_layout = QHBoxLayout(markup_tab)

        markup_tab_save_button = QPushButton("Save", markup_tab)
        markup_tab_save_button.clicked.connect(self._save_markup)
        buttons_layout.addWidget(markup_tab_save_button)

        next_button = QPushButton("Next", markup_tab)
        next_button.clicked.connect(self._move_next)
        buttons_layout.addWidget(next_button)

        markup_layout.addLayout(buttons_layout)

        # Entry List
        markup_entries_group_box = QGroupBox('Visible Entries', self)
        markup_entries_layout = QVBoxLayout(markup_entries_group_box)
        self._markup_entries = MarkupEntriesWidget(self)
        self._markup_entries.itemSelected.connect(self._entry_selected)
        self._markup_entries.setMinimumHeight(200)
        markup_entries_layout.addWidget(self._markup_entries)
        markup_entries_group_box.setLayout(markup_entries_layout)
        markup_layout.addWidget(markup_entries_group_box)

        # History
        history_group_box = QGroupBox('Existing Labels', self)
        history_layout = QVBoxLayout(history_group_box)

        self._history = MarkupContainerWidget(_time_label_mapper, self)
        self._history.delete_signal.connect(self._delete_markup)
        history_layout.addWidget(self._history)

        history_group_box.setLayout(history_layout)
        markup_layout.addWidget(history_group_box)

        # Markup Settings Tab
        markup_settings_tab_scroll = QScrollArea(self)
        markup_settings_tab_scroll.setWidgetResizable(True)
        markup_settings_tab = QWidget(markup_settings_tab_scroll)
        markup_settings_tab_scroll.setWidget(markup_settings_tab)

        self.tabs.addTab(markup_settings_tab_scroll, "Markup Settings")

        # Markup Settings Layout
        markup_settings_layout = QFormLayout(self)
        markup_settings_tab.setLayout(markup_settings_layout)

        # Iteration Order Mode
        self._order_mode_combobox = self._create_settings_combobox(IterationSettings.OrderBy)
        markup_settings_layout.addRow("Iteration Order Mode:", self._order_mode_combobox)

        # Iteration Filter Mode
        self._filter_mode_combobox = self._create_settings_combobox(IterationSettings.Filters)
        markup_settings_layout.addRow("Iteration Filter Mode:", self._filter_mode_combobox)

        # Iteration Index Mode
        self._index_mode_combobox = self._create_settings_combobox(IterationSettings.Index)
        markup_settings_layout.addRow("Iteration Index Mode:", self._index_mode_combobox)

        # Project Details Tab
        details_tab_scroll = QScrollArea(self)
        details_tab_scroll.setWidgetResizable(True)
        project_details_tab = QWidget(details_tab_scroll)
        details_tab_scroll.setWidget(project_details_tab)

        self.tabs.addTab(details_tab_scroll, "Project Details")

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

    def on_enter(self, data: OnEntryData):
        # State
        self._project = data.project
        self._project_path = data.path
        self._iterator = self._project.get_dataset_iterator()

        # Settings Synchronization
        current_index_mode = self._project.markup_settings.iteration_settings.index_callback
        self._index_mode_combobox.setCurrentIndex(
            next(i for i, v in enumerate(IterationSettings.Index.getOptions()) if v.value == current_index_mode))

        current_order_mode = self._project.markup_settings.iteration_settings.order_by
        self._order_mode_combobox.setCurrentIndex(
            next(i for i, v in enumerate(IterationSettings.OrderBy.getOptions()) if v.value == current_order_mode))

        current_filter_mode = self._project.markup_settings.iteration_settings.filter_predicate
        self._filter_mode_combobox.setCurrentIndex(
            next(i for i, v in enumerate(IterationSettings.Filters.getOptions()) if v.value == current_filter_mode))

        # UI Synchronization
        self._prepare_entry()
        self._project_name_line_edit.setText(self._project.name)
        self._project_description_line_edit.setPlainText(self._project.description)
        self._description_input_text_edit.clear()
        self._markup_entries.set_entries(self._iterator.list())
        self.setWindowTitle(f"Project | {self._project.name}")  # TODO: huh?

    def _create_settings_combobox(self, settings_enum: Type[SettingsEnum]):
        combobox = QComboBox(self)
        for entry in settings_enum.getOptions():
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

        self._iterator.refresh_view()

        self._markup_entries.set_entries(self._iterator.list())

    def _move_next(self):
        self._iterator.next()
        self._prepare_entry()

    def _media_changed(self, duration: int):
        self._range_slider.set_range_limit(0, duration)
        self._range_slider.set_range(0, self._project.markup_settings.min_duration_in_ms)
        self._range_slider.set_min_range(self._project.markup_settings.min_duration_in_ms)
        self._history.set_markups(self._iterator.last_accessed_entry.entry.values, duration)

    def _prepare_entry(self):
        # TODO: better info
        if self._iterator.last_accessed_entry is None:
            QMessageBox.question(
                self,
                "Dataset is exhausted",
                "Dataset is fully exhausted, you may try to change iteration settings in order to find more entries.",
                QMessageBox.StandardButton.Ok
            )
        else:
            relative_path = self._iterator.last_accessed_entry.entry.entry_info.relative_path

            self._player.open(self._project.markup_data.full_path(relative_path))
            self._entry_info.setText(str(relative_path))

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

    def _save_markup(self):
        validation_errors = dict(filter(None, [
            validate_required_field(self._description_input_text_edit.toPlainText(), "Description")
        ]))
        if validation_errors:
            show_error_message(validation_errors, self)
            return

        start, end = self._range_slider.get_range()
        markup = MarkupValue(
                start,
                end,
                self._description_input_text_edit.toPlainText()
            )

        self._project.markup_data.add(self._iterator.last_accessed_entry.md5, markup, 0)
        self._history.add_markup(markup, self._player.get_duration(), 0)

    def _delete_markup(self, markup_index: int):
        self._project.markup_data.delete(
            self._iterator.last_accessed_entry.md5,
            markup_index
        )

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
        self._iterator = None

        self._player.discard()

        self._goto("main")

    def _entry_selected(self, md5: str):
        self._iterator.last_accessed_entry = md5
        self._prepare_entry()
