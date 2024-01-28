from pathlib import Path
from typing import Optional, Callable

from PySide6.QtCore import (Qt, Signal, QBuffer, QIODevice)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton,
                               QSlider, QLabel, QStyle)

from src.app.audio_converter import convert_to_mp3


class AudioPlayerWidget(QWidget):
    positionChanged = Signal(int)
    durationChanged = Signal(int)

    def __init__(self, time_label_mapper: Callable[[int], str], parent: Optional[QWidget]):
        super().__init__(parent)

        # State
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._audio_output.setVolume(50)
        self._player.setAudioOutput(self._audio_output)
        self._buffer = None
        self._player.positionChanged.connect(self._position_changed)
        self._player.durationChanged.connect(self._duration_changed)
        self._time_label_mapper = time_label_mapper

        # Layout
        layout = QHBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout(self)

        self._play_button = QPushButton(self)
        self._play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self._play_button.clicked.connect(self._player.play)
        controls_layout.addWidget(self._play_button)

        pause_button = QPushButton(self)
        pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        pause_button.clicked.connect(self._player.pause)
        controls_layout.addWidget(pause_button)

        rewind_button = QPushButton(self)
        rewind_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
        rewind_button.clicked.connect(self._rewind)
        controls_layout.addWidget(rewind_button)

        forward_button = QPushButton(self)
        forward_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))
        forward_button.clicked.connect(self._forward)
        controls_layout.addWidget(forward_button)

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
        if self._buffer is not None:
            self._buffer.data().clear()
            self._buffer.close()
            self._buffer = None

    def open(self, path: Path):
        self.discard()
        self._buffer = QBuffer()
        self._buffer.setData(convert_to_mp3(path))
        self._buffer.open(QIODevice.ReadOnly)
        self._player.setSourceDevice(self._buffer, 'audio/mp3')

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
