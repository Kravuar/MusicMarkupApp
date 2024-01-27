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
    is_corrupted: bool = field(init=False)


@dataclass
class MarkupValue:
    start: float
    end: float
    description: str


@dataclass
class MarkupEntry:
    entry_info: MarkupEntryInfo
    values: List[MarkupValue] = field(default_factory=list)


@dataclass
class MarkupView:
    checksum: str
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
                file_checksum = hashlib.md5(file.read()).hexdigest()
                relative_path = file_path.relative_to(self._directory)

                old_entry = self._data.get(file_checksum)
                old_values = old_entry.values if bool(old_entry) else []

                new_state[file_checksum] = MarkupEntry(
                    MarkupEntryInfo(relative_path),
                    old_values
                )
        self._data = new_state

    def get(self, checksum: str) -> Optional[MarkupView]:
        entry = self._data.get(checksum)
        if entry is not None:
            return MarkupView(checksum, entry)
        return None

    def add(self, checksum: str, markup: MarkupValue):
        self._data[checksum].values.append(markup)

    def update(self, checksum: str, idx: int, markup: MarkupValue):
        self._data[checksum].values[idx] = markup

    def delete(self, checksum: str, idx: int):
        self._data[checksum].values.pop(idx)

    def filter(self, predicate: Callable[[MarkupView], bool]) -> List[MarkupView]:
        return [view for key, entry in self._data.items() if predicate(view := MarkupView(key, entry))]

    def full_path(self, relative_path: Path):
        return self._directory / relative_path

    def to_df(self) -> DataFrame:
        unpacked_rows = [{
            'checksum': checksum,
            'relative_path': markup_entry.entry_info.relative_path,
            'is_corrupted': markup_entry.entry_info.is_corrupted,
            'start': value.start,
            'end': value.end,
            'description': value.description
        } for checksum, markup_entry in self._data.items()
            for value in markup_entry.values
        ]

        return pd.DataFrame(unpacked_rows)
