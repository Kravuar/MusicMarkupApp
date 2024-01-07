from pathlib import Path
from typing import Self

import pandas as pd
import pickle

from src.app.markup import MarkupSettings
from src.app.markup_index import MarkupIndex, MarkupIteratorFilterMode, MarkupIteratorOrderMode
from src.config import AUDIO_FILES_PATTERN, PROJECT_FILE_SUFFIX, MARKUP_FILE_SUFFIX


class Project:
    def __init__(self, name: str, description: str, dataset_dir: Path):
        self.name = name
        self.description = description
        self._markup_settings = MarkupSettings()
        self._markup_dataframe = pd.DataFrame(
            columns=['relative_path', 'start', 'end', 'description', 'is_corrupted'],
            index=pd.Index([], name='checksum')
        )
        self._markup_index = MarkupIndex(dataset_dir, AUDIO_FILES_PATTERN)  # TODO: parallelize checksum?

    def get_dataset_iterator(self, filter_mode: MarkupIteratorFilterMode, order_mode: MarkupIteratorOrderMode):
        return self._markup_index.get_iterator(filter_mode, order_mode)

    def add_entry(self, checksum: str, relative_path: Path, start: float, end: float, description: str):
        self._markup_dataframe[checksum] = [relative_path, start, end, description]

    def find_entries(self, checksum: str):
        return self._markup_dataframe[self._markup_dataframe['checksum'] == checksum]

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
        old_state = set(self._markup_dataframe.index)
        new_state = set(self._markup_index.keys())

        removed_entries = old_state - new_state
        self._markup_dataframe.loc[self._markup_dataframe.index.isin(removed_entries), 'is_corrupted'] = True

        updated_entries = old_state & new_state
        updated_paths = {checksum: self._markup_index[checksum].relative_path for checksum in updated_entries}
        self._markup_dataframe.update(pd.DataFrame.from_dict(updated_paths, orient='index', columns=['relative_path']))

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
            with open(path, 'wb') as file:
                pickle.dump(self._markup_dataframe, file)
        except Exception as e:
            raise RuntimeError(f"Failed to export markup to {path}: {e}")

    @property
    def markup_settings(self):
        return self._markup_settings
