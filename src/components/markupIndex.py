import hashlib
import random
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path


class MarkupIndex:
    def __init__(self, directory: Path, pattern: str):
        self.state: OrderedDict[str, MarkupEntry] = OrderedDict()
        self._directory: Path = directory
        self._pattern: str = pattern
        self.updateState()

    def updateState(self):
        newState: OrderedDict[str, MarkupEntry] = OrderedDict()  # new one to preserve filesystem files order

        matchedFiles = self._directory.rglob(self._pattern)
        for filePath in matchedFiles:
            with open(filePath, 'rb') as file:
                checksum = hashlib.md5(file.read()).hexdigest()  # TODO: What about collisions
                relativePath = filePath.relative_to(self._directory)

                oldEntry = self.state.get(checksum)
                isMarked = False if oldEntry is None else oldEntry.isMarked

                newState[checksum] = MarkupEntry(relativePath, isMarked)

        self.state = newState

    def markupIteration(self):
        nonMarked = [v for v in self.state.values() if not v.isMarked]

        class MarkupEntryProxy:
            def __init__(self, element: MarkupEntry):
                self._element = element

            @property
            def isMarked(self):
                return self._element.isMarked

            @isMarked.setter
            def isMarked(self, value: bool):
                self._element.isMarked = value
                if not nonMarked:
                    raise StopIteration
                nonMarked.remove(self._element)

        while nonMarked:
            yield MarkupEntryProxy(random.choice(nonMarked))


@dataclass
class MarkupEntry:
    relativePath: Path
    isMarked: bool
