from dataclasses import dataclass, field
from pathlib import Path
from typing import Self, List

import pickle

from src.app.markup import MarkupSettings
from src.app.markup_index import MarkupIndex, MarkupIteratorFilterMode, MarkupIteratorOrderMode
from src.config import AUDIO_FILES_PATTERN, PROJECT_FILE_SUFFIX, MARKUP_FILE_SUFFIX


@dataclass
class MarkupEntry:
    checksum: str
    relative_path: Path
    start: float
    end: float
    description: str
    is_corrupted: bool = field(init=False, default=False)


class Project:
    def __init__(self, name: str, description: str, dataset_dir: Path):
        self.name = name
        self.description = description
        self._markup_settings = MarkupSettings()
        self._markup_entries: List[MarkupEntry] = []
        self._markup_index = MarkupIndex(dataset_dir, AUDIO_FILES_PATTERN)  # TODO: parallelize checksum?

    def get_dataset_iterator(self, filter_mode: MarkupIteratorFilterMode, order_mode: MarkupIteratorOrderMode):
        return self._markup_index.get_iterator(filter_mode, order_mode)

    def update_entry(self, rowId: int, start: float, end: float, description: str):
        if 0 <= rowId < len(self._markup_entries):
            entry = self._markup_entries[rowId]
            entry.start = start
            entry.end = end
            entry.description = description
        else:
            raise IndexError(f"Row with ID {rowId} does not exist.")

    def add_entry(self, checksum: str, relative_path: Path, start: float, end: float, description: str):
        new_entry = MarkupEntry(
            checksum=checksum,
            relative_path=relative_path,
            start=start,
            end=end,
            description=description
        )
        self._markup_entries.append(new_entry)

    def delete_entry(self, rowId: int):
        if 0 <= rowId < len(self._markup_entries):
            del self._markup_entries[rowId]
        else:
            raise IndexError(f"Row with ID {rowId} does not exist.")

    def find_entries(self, checksum: str):
        return [entry for entry in self._markup_entries if entry.checksum == checksum]

    @classmethod
    def load(cls, path: Path) -> Self:
        if not path.exists() or not path.is_file() or path.suffix != PROJECT_FILE_SUFFIX:
            raise FileNotFoundError(f"Invalid project file: {path}")
        try:
            with open(path, 'rb') as file:
                loaded_project = pickle.load(file)
                if not isinstance(loaded_project, Project):
                    raise TypeError("File does not contain MM project.")
                loaded_project._update_state()
                return loaded_project
        except Exception as e:
            raise pickle.PickleError(f"Failed to load project from {path}: {e}")

    def _update_state(self):
        self._markup_index.update_state()
        old_state = set([entry.checksum for entry in self._markup_entries])
        new_state = set(self._markup_index.keys())

        removed_entries = old_state - new_state
        for entry in self._markup_entries:
            if entry.checksum in removed_entries:
                entry.is_corrupted = True

        updated_entries = old_state & new_state
        updated_paths = {checksum: self._markup_index[checksum].relative_path for checksum in updated_entries}
        for entry in self._markup_entries:
            entry.relative_path = updated_paths.get(entry.checksum, entry.relative_path)

    def save(self, path: Path):
        if path.is_dir():
            path = path / (self.name + PROJECT_FILE_SUFFIX)

        if not path.is_file():
            raise ValueError("Provided path isn't valid.")

        try:
            with open(path, 'wb') as file:
                pickle.dump(self, file)
        except Exception as e:
            raise pickle.PickleError(f"Failed to save project to {path}: {e}")

    def export_markup(self, path: Path):
        if not path.is_dir():
            raise ValueError("Path should be an existing directory.")
        path = path / (self.name + MARKUP_FILE_SUFFIX)
        try:
            dataframe = [{'relative_path': str(entry.relative_path),
                          'start': entry.start,
                          'end': entry.end,
                          'description': entry.description,
                          'is_corrupted': entry.is_corrupted}
                         for entry in self._markup_entries]
            with open(path, 'wb') as file:
                pickle.dump(dataframe, file)
        except Exception as e:
            raise RuntimeError(f"Failed to export markup to {path}: {e}")

    @property
    def markup_settings(self):
        return self._markup_settings
