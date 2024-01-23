import pickle
from pathlib import Path
from typing import Self

from src.app.markup_data import MarkupData
from src.app.markup_iterator import MarkupIterator
from src.app.markup_settings import MarkupSettings
from src.config import PROJECT_FILE_SUFFIX


class Project:
    def __init__(self, name: str, description: str, dataset_dir: Path):
        self.name = name
        self.description = description
        self._markup_settings = MarkupSettings()
        self._markup_data = MarkupData(dataset_dir)

    def get_dataset_iterator(self) -> MarkupIterator:
        return MarkupIterator(self._markup_data, self._markup_settings.iteration_settings)

    @classmethod
    def load(cls, path: Path) -> Self:
        if not path.exists() or not path.is_file() or path.suffix != PROJECT_FILE_SUFFIX:
            raise FileNotFoundError(f"Invalid project file: {path}")
        try:
            with open(path, 'rb') as file:
                loaded_project = pickle.load(file)
                if not isinstance(loaded_project, Project):
                    raise TypeError("File does not contain MM project.")
                loaded_project._markup_data.update_state()
                return loaded_project
        except Exception as e:
            raise pickle.PickleError(f"Failed to load project from {path}: {e}")

    def save(self, path: Path):
        try:
            with open(path, 'wb') as file:
                pickle.dump(self, file)
        except Exception as e:
            raise pickle.PickleError(f"Failed to save project to {path}: {e}.")

    def export_markup(self, path: Path):
        try:
            with open(path, 'wb') as file:
                pickle.dump(self._markup_data.to_df(), file)
        except Exception as e:
            raise RuntimeError(f"Failed to export markup to {path}: {e}.")

    @property
    def markup_settings(self):
        return self._markup_settings

    @property
    def markup_data(self):
        return self._markup_data
