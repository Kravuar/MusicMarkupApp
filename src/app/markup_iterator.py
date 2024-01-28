from typing import Optional, List

from src.app.markup_data import MarkupData, MarkupView
from src.app.markup_settings import IterationSettings


class MarkupIterator:
    def __init__(self, data: MarkupData, settings: IterationSettings):
        self._data = data
        self._settings = settings
        self._iteration_list: List[MarkupView] = []
        self.refresh_view()

    def refresh_view(self):
        self._iteration_list = self._data.filter(self._settings.filter_predicate)
        if self._settings.order_by is not None:
            self._iteration_list.sort(key=self._settings.order_by)

    def list(self):
        return tuple(self._iteration_list)

    def next(self) -> Optional[MarkupView]:
        entry = None
        while self._iteration_list:
            size = len(self._iteration_list)
            self._settings.last_idx = self._settings.index_callback(size, self._settings.last_idx) % size

            if self._settings.last_idx < 0:
                self._settings.last_idx += size

            next_entry = self._iteration_list[self._settings.last_idx]
            if self._settings.filter_predicate(next_entry):
                entry = next_entry
                break
            else:
                self._iteration_list.pop(self._settings.last_idx)

        return entry

    @property
    def last_accessed_entry(self) -> Optional[MarkupView]:
        if self._settings.last_idx not in range(0, len(self._iteration_list)):
            return None
        return self._iteration_list[self._settings.last_idx]

    @last_accessed_entry.setter
    def last_accessed_entry(self, checksum: str):
        idx = next((idx for idx, entry in enumerate(self._iteration_list) if entry.checksum == checksum), None)
        if idx is not None:
            self._settings.last_idx = idx
