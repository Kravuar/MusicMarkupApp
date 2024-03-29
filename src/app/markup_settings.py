import random
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Any, Optional, Iterator, Iterable

from src.app.markup_data import MarkupView


class SettingsEnum:
    @dataclass
    class SettingsEnumEntry:
        name: str
        display_name: str
        value: Any

    @classmethod
    @abstractmethod
    def getOptions(cls) -> Iterator[SettingsEnumEntry]:
        pass


@dataclass
class IterationSettings:
    class Filters(SettingsEnum):
        @staticmethod
        def NON_CORRUPTED(view: MarkupView) -> bool:
            return not view.entry.entry_info.is_corrupted

        @staticmethod
        def ALL(view: MarkupView) -> bool:
            return True

        @staticmethod
        def NON_VISITED(view: MarkupView) -> bool:
            return len(view.entry.values) == 0

        @classmethod
        def getOptions(cls) -> Iterable[SettingsEnum.SettingsEnumEntry]:
            return [
                SettingsEnum.SettingsEnumEntry('non_corrupted', 'Non Corrupted', cls.NON_CORRUPTED),
                SettingsEnum.SettingsEnumEntry('all', 'All', cls.ALL),
                SettingsEnum.SettingsEnumEntry('non_visited', 'None Visited', cls.NON_VISITED)
            ]

    class OrderBy(SettingsEnum):
        APPEARANCE = None

        @staticmethod
        def LABEL_COUNT(view: MarkupView) -> Any:
            return len(view.entry.values)

        @classmethod
        def getOptions(cls) -> Iterable[SettingsEnum.SettingsEnumEntry]:
            return [
                SettingsEnum.SettingsEnumEntry('appearance', 'Appearance', cls.APPEARANCE),
                SettingsEnum.SettingsEnumEntry('label_count', 'Label Count', cls.LABEL_COUNT)
            ]

    class Index(SettingsEnum):
        @staticmethod
        def SEQUENTIAL(size: int, last_index: int) -> int:
            return (last_index + 1) % size

        @staticmethod
        def RANDOM(size: int, last_index: int) -> int:
            return random.randint(0, size - 1)

        @classmethod
        def getOptions(cls) -> Iterable[SettingsEnum.SettingsEnumEntry]:
            return [
                SettingsEnum.SettingsEnumEntry('sequential', 'Sequential', cls.SEQUENTIAL),
                SettingsEnum.SettingsEnumEntry('random', 'Random', cls.RANDOM)
            ]

    # takes view size, previous index, returns new index (default - sequential)
    index_callback: Callable[[int, int], int] = Index.SEQUENTIAL
    # filter predicate (default - all)
    filter_predicate: Callable[[MarkupView], bool] = Filters.NON_CORRUPTED
    # key mapper for sorting (default - appearance order)
    order_by: Optional[Callable[[MarkupView], Any]] = OrderBy.APPEARANCE
    # last viewed entry
    last_idx: int = 0


@dataclass
class MarkupSettings:
    iteration_settings: IterationSettings = field(default_factory=IterationSettings)
    min_duration_in_ms: int = 5000
    # TODO: author regex, title regex
    # TODO: fragment size, overlap factor. Those can be changed at any time.
    # TODO: manual fragmentation with sliders and stuff.
