from pathlib import Path
from typing import Self

import pandas as pd
import pickle

from src.app.markup import MarkupSettings
from src.app.markup_index import MarkupIndex
from src.config import AUDIO_FILES_PATTERN, PROJECT_FILE_SUFFIX


class Project:
    def __init__(self, name: str, description: str, project_file_dir: Path, dataset_dir: Path):
        self.name = name
        self.description = description
        self._dataset_dir = dataset_dir
        self._project_file = project_file_dir / (self.name + PROJECT_FILE_SUFFIX)
        self._markup_settings = MarkupSettings()
        self._markup_dataframe = pd.DataFrame(
            columns=['relative_path', 'start', 'end', 'description', 'is_corrupted'],
            index=pd.Index([], name='checksum')
        )
        self._markup_index = MarkupIndex(self._dataset_dir, AUDIO_FILES_PATTERN)  # TODO: parallelize checksum?

    @classmethod
    def load(cls, path: Path) -> Self:
        if not path.exists() or not path.is_file() or path.suffix != PROJECT_FILE_SUFFIX:
            raise FileNotFoundError(f"Invalid project file: {path}")
        try:
            with open(path, 'rb') as file:
                loaded_project = pickle.load(file)
                if not isinstance(loaded_project, Project):
                    raise TypeError("File does not contain MM project.")
                loaded_project.update_state()
                loaded_project.project_file = path
                return loaded_project
        except Exception as e:
            raise pickle.PickleError(f"Failed to load project from {path}: {e}")

    def update_state(self):
        self._markup_index.update_state()
        old_state = set(self._markup_dataframe.index)
        new_state = set(self._markup_index.keys())

        removed_entries = old_state - new_state
        self._markup_dataframe.loc[self._markup_dataframe.index.isin(removed_entries), 'is_corrupted'] = True

        updated_entries = old_state & new_state
        updated_paths = {checksum: self._markup_index[checksum].relative_path for checksum in updated_entries}
        self._markup_dataframe.update(pd.DataFrame.from_dict(updated_paths, orient='index', columns=['relative_path']))

    def save(self):
        try:
            with open(self.project_file, 'wb') as file:
                pickle.dump(self, file)
        except Exception as e:
            raise pickle.PickleError(f"Failed to save project to {self.project_file}: {e}")

    def export_markup(self, path: Path):
        try:
            with open(path, 'wb') as file:
                pickle.dump(self.markup_data_frame, file)
        except Exception as e:
            raise RuntimeError(f"Failed to export markup to {path}: {e}")

    @property
    def dataset_dir(self):
        return self._dataset_dir

    @property
    def project_file(self):
        return self._project_file

    @project_file.setter
    def project_file(self, path: Path):
        self._project_file = path

    @property
    def markup_settings(self):
        return self._markup_settings

    @property
    def markup_data_frame(self):
        return self._markup_dataframe
