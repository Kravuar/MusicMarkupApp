import random
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Any, Optional, Iterator

from src.app.markup_data import MarkupView


class SettingsEnum:
    @dataclass
    class SettingsEnumEntry:
        name: str
        display_name: str
        value: Any

    @classmethod
    @abstractmethod
    def __iter__(cls) -> Iterator[SettingsEnumEntry]:
        pass


@dataclass
class IterationSettings:
    class Filters(SettingsEnum):
        @staticmethod
        def ALL(view: MarkupView) -> bool:
            return True

        @staticmethod
        def NON_VISITED(view: MarkupView) -> bool:
            return len(view.entry.values) == 0

        @classmethod
        def __iter__(cls) -> Iterator[SettingsEnum.SettingsEnumEntry]:
            return iter([
                SettingsEnum.SettingsEnumEntry('all', 'All', cls.ALL),
                SettingsEnum.SettingsEnumEntry('non_visited', 'None Visited', cls.NON_VISITED)
            ])

    class OrderBy(SettingsEnum):
        APPEARANCE = None

        @staticmethod
        def LABEL_COUNT(view: MarkupView) -> Any:
            return len(view.entry.values)

        @classmethod
        def __iter__(cls) -> Iterator[SettingsEnum.SettingsEnumEntry]:
            return iter([
                SettingsEnum.SettingsEnumEntry('appearance', 'Appearance', cls.APPEARANCE),
                SettingsEnum.SettingsEnumEntry('label_count', 'Label Count', cls.LABEL_COUNT)
            ])

    class Index(SettingsEnum):
        @staticmethod
        def SEQUENTIAL(size: int, last_index: int) -> int:
            return (last_index + 1) % size

        @staticmethod
        def RANDOM(size: int, last_index: int) -> int:
            return random.randint(0, size - 1)

        @classmethod
        def __iter__(cls) -> Iterator[SettingsEnum.SettingsEnumEntry]:
            return iter([
                SettingsEnum.SettingsEnumEntry('sequential', 'Sequential', cls.SEQUENTIAL),
                SettingsEnum.SettingsEnumEntry('random', 'Random', cls.RANDOM)
            ])

    # takes view size, previous index, returns new index (default - sequential)
    index_callback: Callable[[int, int], int] = Index.SEQUENTIAL
    # filter predicate (default - all)
    filter_predicate: Callable[[MarkupView], bool] = Filters.ALL
    # key mapper for sorting (default - appearance order)
    order_by: Optional[Callable[[MarkupView], Any]] = OrderBy.APPEARANCE
    # last viewed entry
    last_idx: int = 0


@dataclass
class MarkupSettings:
    iteration_settings: IterationSettings = field(default_factory=IterationSettings)
    # TODO: author regex, title regex
    # TODO: fragment size, overlap factor. Those can be changed at any time.
    # TODO: manual fragmentation with sliders and stuff.
