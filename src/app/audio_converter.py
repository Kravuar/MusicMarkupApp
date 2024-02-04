import subprocess
from abc import abstractmethod, ABC
from pathlib import Path

from PySide6.QtCore import QIODevice, QTemporaryFile, QFile

from src.config import MIDI_SF_PATH


class Converter(ABC):
    @abstractmethod
    def supports_source(self, source: QIODevice) -> bool:
        pass

    @abstractmethod
    def convert(self, source: QIODevice) -> QIODevice:
        pass


class MidiToWAVConverter(Converter):

    def supports_source(self, source: QIODevice) -> bool:
        is_file = isinstance(source, QFile)
        is_midi = Path(source.fileName()).suffix in ['.mid', '.midi']
        return is_file and is_midi

    def convert(self, source: QIODevice) -> QIODevice:
        if not isinstance(source, QFile):
            raise ValueError("Provided QIODevice isn't supported by this converter.")

        converted = QTemporaryFile()
        if converted.open():
            subprocess.call(['fluidsynth', '-ni', MIDI_SF_PATH, source.fileName(), '-F', converted.fileName(), '-r', '44100'])
            return converted
        else:
            raise IOError('Could not create file for MIDI conversion.')


CONVERTERS = [MidiToWAVConverter()]
