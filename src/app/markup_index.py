import enum
import hashlib
import random
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass
from math import inf
from pathlib import Path

from src.app.file_system_utils import iterate_files


@dataclass
class MarkupEntry:
    relative_path: Path
    is_labeled: bool


class MarkupIteratorOrderMode(enum.Enum):
    ORDERED = 1,
    UNORDERED = 2


class MarkupIteratorFilterMode(enum.Enum):
    ALL = 1,
    NON_LABELED = 2


class MarkupIndex:
    def __init__(self, directory: Path, suffixes):
        self._state: OrderedDict[str, MarkupEntry] = OrderedDict()
        self._directory: Path = directory
        self._suffixes: str = suffixes
        self._checksum = None
        self.update_state()

    def update_state(self):
        new_state: OrderedDict[str, MarkupEntry] = OrderedDict()

        overall_checksum = hashlib.md5()
        for file_path in iterate_files(self._directory, self._suffixes):
            with open(file_path, 'rb') as file:
                data = file.read()
                path_repr = '|'.join(file_path.relative_to(self._directory).parts).encode('utf-8')

                overall_checksum.update(path_repr)
                overall_checksum.update(data)

                file_checksum = hashlib.md5(data).hexdigest()  # TODO: What about collisions
                relative_path = file_path.relative_to(self._directory)

                old_entry = self._state.get(file_checksum)
                is_labeled = False if old_entry is None else old_entry.is_labeled

                new_state[file_checksum] = MarkupEntry(relative_path, is_labeled)

        self._state = new_state
        self._checksum = overall_checksum.hexdigest()

    def __getitem__(self, index) -> MarkupEntry:
        return self._state[index]

    def keys(self):
        return self._state.keys()

    def get_iterator(self, filter_mode: MarkupIteratorFilterMode, order_mode: MarkupIteratorOrderMode):
        # TODO: All this iterators stuff looks very bad
        if filter_mode == MarkupIteratorFilterMode.ALL:
            return InfiniteMarkupIterator(self._state, order_mode)
        elif filter_mode == MarkupIteratorFilterMode.NON_LABELED:
            return NonLabeledMarkupIterator(self._state, order_mode)
        else:
            raise ValueError(f"Invalid filter mode: {filter_mode}")


class MarkupIterator(ABC):
    def __init__(self, mode: MarkupIteratorOrderMode):
        self._mode: MarkupIteratorOrderMode = mode
        self._element_provider = None
        self.mode = mode

    def __iter__(self):
        return self

    def __next__(self):
        if not self._has_next():
            raise StopIteration

        return self._element_provider()

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, new_mode: MarkupIteratorOrderMode):
        if new_mode == MarkupIteratorOrderMode.UNORDERED:
            self._element_provider = self._get_unordered_entry
        elif new_mode == MarkupIteratorOrderMode.ORDERED:
            self._element_provider = self._get_ordered_entry()
        else:
            raise RuntimeError(f"Invalid order mode: {new_mode}")

        self._mode = new_mode

    @abstractmethod
    def _has_next(self):
        pass

    @abstractmethod
    def _get_unordered_entry(self):
        pass

    @abstractmethod
    def _get_ordered_entry(self):
        pass

    @property
    @abstractmethod
    def remaining(self):
        pass


class InfiniteMarkupIterator(MarkupIterator):
    def __init__(self, entries: OrderedDict[str, MarkupEntry], mode: MarkupIteratorOrderMode):
        super().__init__(mode)
        self._entries = OrderedDict(entries)
        self._list_view = list(entries.items())

    def _get_unordered_entry(self):
        return random.choice(self._list_view)

    def _get_ordered_entry(self):
        key = next(iter(self._entries))
        self._entries.move_to_end(key)
        return key, self._entries[key]

    def _has_next(self):
        return bool(self._entries)

    @property
    def remaining(self):
        return inf


class NonLabeledMarkupIterator(MarkupIterator):
    def __init__(self, entries: OrderedDict[str, MarkupEntry], mode: MarkupIteratorOrderMode):
        super().__init__(mode)
        self._non_labeled = OrderedDict({k: v for k, v in entries.items() if not v.is_labeled})

    def _get_unordered_entry(self):
        k, v = random.choice(list(self._non_labeled.items()))  # Fkit, lists go brrr (100x slower than ordered)
        return k, v.relative_path, self._mark_labeled_callback(k)

    def _get_ordered_entry(self):
        # Retrieves first item in dict, moves it to the end (so that dict is shifted)
        key = next(iter(self._non_labeled))
        self._non_labeled.move_to_end(key)
        return key, self._non_labeled[key].relative_path, self._mark_labeled_callback(key)

    def _mark_labeled_callback(self, key: str):
        def mark_labeled():
            entry = self._non_labeled.pop(key, None)
            if entry:
                entry.is_labeled = True

        return mark_labeled

    def _has_next(self):
        return bool(self._non_labeled)

    @property
    def remaining(self):
        return len(self._non_labeled)
