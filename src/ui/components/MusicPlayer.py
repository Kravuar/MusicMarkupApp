from pathlib import Path
from typing import Optional

from PySide6.QtCore import (Qt, Signal, QBuffer, QIODevice)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton,
                               QSlider, QLabel, QStyle)

from src.app.audio_converter import convert_to_mp3


class AudioPlayerWidget(QWidget):
    positionChanged = Signal(int)

    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)

        # State
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._audio_output.setVolume(50)
        self._player.setAudioOutput(self._audio_output)
        self._buffer = QBuffer()
        self._player.positionChanged.connect(self._position_changed)
        self._player.durationChanged.connect(self._duration_changed)

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

        # Slider
        time_layout = QHBoxLayout(self)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.sliderMoved.connect(self.set_position)
        self.slider.setRange(0, 0)

        self.currentTimeLabel = QLabel('00:00', self)
        self.totalTimeLabel = QLabel('00:00', self)

        time_layout.addWidget(self.currentTimeLabel)
        time_layout.addWidget(self.slider)
        time_layout.addWidget(self.totalTimeLabel)

        layout.addLayout(time_layout)

        self.setLayout(layout)

    def set_file(self, path: Path):
        self._buffer.close()
        self._buffer.setData(convert_to_mp3(path))
        self._buffer.open(QIODevice.ReadOnly)

        self._player.setSourceDevice(self._buffer, 'audio/mp3')

    def get_position(self):
        return self._player.position()

    def set_position(self, position: int):
        self._player.setPosition(position)

    def _position_changed(self, position: int):
        self.slider.setValue(position)
        self._update_time_label(self.currentTimeLabel, position)
        self.positionChanged.emit(position)

    def _duration_changed(self, duration: int):
        self.slider.setRange(0, duration)
        self._update_time_label(self.totalTimeLabel, duration)

    @staticmethod
    def _update_time_label(label, time_in_ms):
        seconds = int(time_in_ms / 1000)
        minutes = int(seconds / 60)
        seconds -= minutes * 60
        label.setText(f'{minutes:02d}:{seconds:02d}')

    def _rewind(self):
        self.set_position(self._player.position() - 5000)

    def _forward(self):
        self.set_position(self._player.position() + 5000)
