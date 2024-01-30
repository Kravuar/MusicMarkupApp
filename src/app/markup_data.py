import hashlib
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Callable

import pandas as pd
from pandas import DataFrame

from src.app.file_system_utils import iterate_files
from src.config import AUDIO_FILES_PATTERN


@dataclass
class MarkupEntryInfo:
    relative_path: Path
    is_corrupted: bool = False


@dataclass
class MarkupValue:
    start: int
    end: int
    description: str


@dataclass
class MarkupEntry:
    entry_info: MarkupEntryInfo
    values: List[MarkupValue] = field(default_factory=list)


@dataclass
class MarkupView:
    md5: str
    entry: MarkupEntry


class MarkupData:
    def __init__(self, dataset_dir: Path):
        self._directory: Path = dataset_dir
        self._data: OrderedDict[str, MarkupEntry] = OrderedDict()
        self.update_state()

    def update_state(self):
        new_state: OrderedDict[str, MarkupEntry] = OrderedDict()
        for file_path in iterate_files(self._directory, AUDIO_FILES_PATTERN):
            with open(file_path, 'rb') as file:
                file_md5 = hashlib.md5(file.read()).hexdigest()
                relative_path = file_path.relative_to(self._directory)

                old_entry = self._data.get(file_md5)
                old_values = old_entry.values if bool(old_entry) else []

                new_state[file_md5] = MarkupEntry(
                    MarkupEntryInfo(relative_path),
                    old_values
                )
        for old_md5, old_entry in self._data.items():
            if old_md5 not in new_state:
                old_entry.entry_info.is_corrupted = True
                new_state[old_md5] = old_entry
        self._data = new_state

    def get(self, md5: str) -> Optional[MarkupView]:
        entry = self._data.get(md5)
        if entry is not None:
            return MarkupView(md5, entry)
        return None

    def add(self, md5: str, markup: MarkupValue, index: int = 0):
        self._data[md5].values.insert(index, markup)

    def update(self, md5: str, idx: int, markup: MarkupValue):
        self._data[md5].values[idx] = markup

    def delete(self, md5: str, idx: int):
        self._data[md5].values.pop(idx)

    def filter(self, predicate: Callable[[MarkupView], bool]) -> List[MarkupView]:
        return [view for key, entry in self._data.items() if predicate(view := MarkupView(key, entry))]

    def absolute_path(self, relative_path: Path):
        return self._directory / relative_path

    def refresh_entry(self, md5):
        entry = self._data.get(md5, None)
        if entry:
            path = self._directory / entry.entry_info.relative_path
            entry.entry_info.is_corrupted = not path.exists()

    def to_df(self) -> DataFrame:
        unpacked_rows = [{
            'md5': md5,
            'relative_path': markup_entry.entry_info.relative_path,
            'is_corrupted': markup_entry.entry_info.is_corrupted,
            'start': value.start,
            'end': value.end,
            'description': value.description
        } for md5, markup_entry in self._data.items()
            for value in markup_entry.values
        ]

        return pd.DataFrame(unpacked_rows)
