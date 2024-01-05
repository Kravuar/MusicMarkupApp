import hashlib
import random
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

from src.app.file_system_utils import iterate_files


@dataclass
class MarkupEntry:
    relative_path: Path
    is_marked: bool


class MarkupIndex:
    def __init__(self, directory: Path, suffixes):
        self.state: OrderedDict[str, MarkupEntry] = OrderedDict()
        self._directory: Path = directory
        self._suffixes: str = suffixes
        self._checksum = None
        self.update_state()

    def update_state(self):
        new_state: OrderedDict[str, MarkupEntry] = OrderedDict()  # new one to preserve filesystem files order

        overall_checksum = hashlib.md5()
        for file_path in iterate_files(self._directory, self._suffixes):
            with open(file_path, 'rb') as file:
                data = file.read()
                path_repr = '|'.join(file_path.relative_to(self._directory).parts).encode('utf-8')

                overall_checksum.update(path_repr)
                overall_checksum.update(data)

                file_checksum = hashlib.md5(data).hexdigest()  # TODO: What about collisions
                relative_path = file_path.relative_to(self._directory)

                old_entry = self.state.get(file_checksum)
                is_marked = False if old_entry is None else old_entry.is_marked

                new_state[file_checksum] = MarkupEntry(relative_path, is_marked)

        self.state = new_state
        self._checksum = overall_checksum.hexdigest()

    def markup_iteration(self):
        non_marked = [v for v in self.state.values() if not v.is_marked]

        class MarkupEntryProxy:
            def __init__(self, element: MarkupEntry):
                self._element = element

            @property
            def is_marked(self):
                return self._element.is_marked

            @is_marked.setter
            def is_marked(self, value: bool):
                self._element.is_marked = value
                if not non_marked:
                    raise StopIteration
                non_marked.remove(self._element)

        while non_marked:
            yield MarkupEntryProxy(random.choice(non_marked))

    def __getitem__(self, index) -> MarkupEntry:
        return self.state[index]

    def keys(self):
        return self.state.keys()
