import threading
from pathlib import Path
from typing import Optional, Callable, List

from PySide6.QtCore import (Qt, Signal, QIODevice, QUrl)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton,
                               QSlider, QLabel, QStyle)

from src.app.audio_converter import Converter


class AudioPlayerWidget(QWidget):
    positionChanged = Signal(int)
    durationChanged = Signal(int)
    mediaStatusChanged = Signal(QMediaPlayer.MediaStatus)

    def __init__(self, time_label_mapper: Callable[[int], str], converters: List[Converter], parent: Optional[QWidget]):
        super().__init__(parent)

        # State
        self._converters = converters
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self._player)
        self._audio_output.setVolume(50)
        self._player.setAudioOutput(self._audio_output)

        self._time_label_mapper = time_label_mapper

        self._player.positionChanged.connect(self._position_changed)
        self._player.durationChanged.connect(self._duration_changed)
        self._player.mediaStatusChanged.connect(self._update_accessibility)
        self._player.mediaStatusChanged.connect(self._convert_if_invalid)
        self._player.mediaStatusChanged.connect(self._hide_show_timestamps)
        self._player.mediaStatusChanged.connect(lambda status: self.mediaStatusChanged.emit(status))

        # Layout
        layout = QHBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout(self)

        self._play_pause_button = QPushButton(self)
        self._play_pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self._play_pause_button.clicked.connect(lambda: self._toggle_play_pause(None))
        self._play_pause_button.setDisabled(True)
        controls_layout.addWidget(self._play_pause_button)

        self._rewind_button = QPushButton(self)
        self._rewind_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
        self._rewind_button.clicked.connect(self._rewind)
        self._rewind_button.setDisabled(True)
        controls_layout.addWidget(self._rewind_button)

        self._forward_button = QPushButton(self)
        self._forward_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))
        self._forward_button.clicked.connect(self._forward)
        self._forward_button.setDisabled(True)
        controls_layout.addWidget(self._forward_button)

        layout.addLayout(controls_layout)

        # Playback slider
        playback_layout = QHBoxLayout(self)

        self._currentTimeLabel = QLabel(self._time_label_mapper(0), self)

        playback_layout.addWidget(self._currentTimeLabel)

        self._slider = QSlider(Qt.Horizontal)
        self._slider.sliderMoved.connect(self.set_position)
        self._slider.setRange(0, 0)
        playback_layout.addWidget(self._slider)

        self._totalTimeLabel = QLabel(self)
        playback_layout.addWidget(self._totalTimeLabel)

        layout.addLayout(playback_layout)

        self.setLayout(layout)

    def discard(self):
        self._player.stop()
        # Can't find an appropriate way to clean up, so I won't

    def open(self, path: Path):
        self.discard()
        self._player.setSource(QUrl.fromLocalFile(path))
        # This is the most retarded part of the QT, dumbass docs, braindead interfaces
        # No idea why its crashes (but sometimes it does not), io is open, readable
        # No matter what IODevice, in memory byte array or any file
        # I feel like something wrong with the combination of setSource, setSourceDevice, even though setSource isn't used

        # Desired implementation:
        # self._player.setSourceDevice(QFile(path))

    def open_from_device(self, source_device: QIODevice):
        self.discard()
        self._player.setSourceDevice(source_device)

    def get_position(self):
        return self._player.position()

    def get_duration(self):
        return self._player.duration()

    def set_position(self, position: int):
        self._player.setPosition(position)

    def _position_changed(self, position: int):
        self._slider.setValue(position)
        self._currentTimeLabel.setText(self._time_label_mapper(position))
        self.positionChanged.emit(position)

    def _duration_changed(self, duration: int):
        self._slider.setRange(0, duration)
        self._totalTimeLabel.setText(self._time_label_mapper(duration))
        self.durationChanged.emit(duration)

    def _rewind(self):
        self.set_position(self._player.position() - 5000)

    def _forward(self):
        self.set_position(self._player.position() + 5000)

    def _toggle_play_pause(self, pause: Optional[bool]):
        if pause is None:
            pause = self._player.isPlaying()
        if pause:
            self._player.pause()
            self._play_pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self._player.play()
            self._play_pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def _update_accessibility(self, status: QMediaPlayer.MediaStatus):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self._play_pause_button.setDisabled(False)
            self._rewind_button.setDisabled(False)
            self._forward_button.setDisabled(False)
            self._slider.setDisabled(False)
        elif status in [QMediaPlayer.MediaStatus.LoadingMedia, QMediaPlayer.MediaStatus.InvalidMedia]:
            self._play_pause_button.setDisabled(True)
            self._rewind_button.setDisabled(True)
            self._forward_button.setDisabled(True)
            self._slider.setDisabled(True)
        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._toggle_play_pause(True)
            self._player.stop()

    def _hide_show_timestamps(self, status: QMediaPlayer.MediaStatus):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self._totalTimeLabel.setVisible(True)
            self._currentTimeLabel.setVisible(True)
        elif status in [QMediaPlayer.MediaStatus.InvalidMedia, QMediaPlayer.MediaStatus.NoMedia]:
            self._totalTimeLabel.setVisible(False)
            self._currentTimeLabel.setVisible(False)

    def _convert_if_invalid(self, status: QMediaPlayer.MediaStatus):
        if status == QMediaPlayer.MediaStatus.InvalidMedia:
            threading.Thread(target=self._try_convert_and_open).start()

    def _try_convert_and_open(self):
        invalid_source = self._player.sourceDevice()
        if invalid_source is not None:
            converter = next((conv for conv in self._converters if conv.supports_source(invalid_source)), None)

            if converter is not None:
                try:
                    self._player.mediaStatusChanged.emit(QMediaPlayer.MediaStatus.LoadingMedia)
                    converted = converter.convert(invalid_source)
                    self.open_from_device(converted)
                except Exception:
                    pass
