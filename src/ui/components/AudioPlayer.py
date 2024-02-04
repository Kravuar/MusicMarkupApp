from pathlib import Path
from typing import Callable, Optional

from PySide6.QtCore import Signal, QUrl, Qt, Slot
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QStyle, QLabel, QSlider, QVBoxLayout


class AudioPlayer(QWidget):
    _DEFAULT_VOLUME = 0.3

    positionChanged = Signal(int)
    durationChanged = Signal(int)
    mediaStatusChanged = Signal(QMediaPlayer.MediaStatus)

    def __init__(self, time_label_mapper: Callable[[int], str], parent: Optional[QWidget]):
        super().__init__(parent)

        # State
        self._time_label_mapper = time_label_mapper
        self._player: Optional[QMediaPlayer] = None
        self._audio_output: Optional[QAudioOutput] = None

        # Layout
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # Controls
        controls_layout = QVBoxLayout(self)

        # Buttons
        buttons_layout = QHBoxLayout(self)
        self._play_pause_button = QPushButton(self)
        self._play_pause_button.clicked.connect(self.toggle_play_pause)
        self._play_pause_button.setDisabled(True)
        buttons_layout.addWidget(self._play_pause_button)

        self._rewind_button = QPushButton(self)
        self._rewind_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
        self._rewind_button.clicked.connect(self.rewind)
        self._rewind_button.setDisabled(True)
        buttons_layout.addWidget(self._rewind_button)

        self._forward_button = QPushButton(self)
        self._forward_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))
        self._forward_button.clicked.connect(self.forward)
        self._forward_button.setDisabled(True)
        buttons_layout.addWidget(self._forward_button)

        controls_layout.addLayout(buttons_layout)

        # Volume
        playback_volume_layout = QHBoxLayout(self)
        volume_label = QLabel("Volume", self)
        playback_volume_layout.addWidget(volume_label)
        self._volume_slider = QSlider(Qt.Orientation.Horizontal)
        self._volume_slider.sliderMoved.connect(lambda value: self.set_volume(value / 100))
        self._volume_slider.setRange(0, 100)
        playback_volume_layout.addWidget(self._volume_slider, 1)
        controls_layout.addLayout(playback_volume_layout)

        layout.addLayout(controls_layout, 2)

        # Playback
        playback_time_layout = QHBoxLayout(self)
        self._currentTimeLabel = QLabel(self._time_label_mapper(0), self)
        playback_time_layout.addWidget(self._currentTimeLabel)

        self._playback_slider = QSlider(Qt.Orientation.Horizontal)
        self._playback_slider.sliderMoved.connect(self.set_position)
        self._playback_slider.setRange(0, 0)
        playback_time_layout.addWidget(self._playback_slider)

        self._totalTimeLabel = QLabel(self)
        playback_time_layout.addWidget(self._totalTimeLabel)

        layout.addLayout(playback_time_layout, 8)

    def discard(self):
        if self._player is not None:
            self._player.stop()
        self._player = None
        self._audio_output = None
        # Can't find an appropriate way to clean up, so I won't

    def open_from_file(self, path: Path):
        self.discard()
        self._reinit_player()
        self._player.setSource(QUrl.fromLocalFile(path))

    @Slot(float)
    def set_volume(self, volume: float):
        self._audio_output.setVolume(volume)

    def get_position(self):
        return self._player.position()

    def get_duration(self):
        return self._player.duration()

    @Slot(int)
    def set_position(self, position: int):
        self._player.setPosition(position)

    def pause(self):
        self._player.pause()

    def play(self):
        if self._player.hasAudio():
            self._player.play()

    def rewind(self):
        self.set_position(self._player.position() - 5000)

    def forward(self):
        self.set_position(self._player.position() + 5000)

    def toggle_play_pause(self):
        if self._player.isPlaying():
            self.pause()
        else:
            self.play()

    @Slot(int)
    def _update_volume_slider(self, volume: int):
        volume = max(0, min(volume, 100))
        self._volume_slider.setValue(volume)

    @Slot(int)
    def _update_slider_position(self, position: int):
        self._playback_slider.setValue(position)
        self._currentTimeLabel.setText(self._time_label_mapper(position))

    @Slot(int)
    def _update_slider_duration(self, duration: int):
        self._playback_slider.setRange(0, duration)
        self._totalTimeLabel.setText(self._time_label_mapper(duration))

    def _update_play_pause_to_pause(self):
        self._play_pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def _update_play_pause_to_play(self):
        self._play_pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    @Slot(bool)
    def _update_play_pause_ui(self, playing: bool):
        if playing:
            self._update_play_pause_to_pause()
        else:
            self._update_play_pause_to_play()

    @Slot(bool)
    def _hide_show_timestamps(self, show: bool):
        self._totalTimeLabel.setVisible(show)
        self._currentTimeLabel.setVisible(show)

    @Slot(bool)
    def _enable_controls(self, enable: bool):
        self._play_pause_button.setEnabled(enable)
        self._rewind_button.setEnabled(enable)
        self._forward_button.setEnabled(enable)
        self._playback_slider.setEnabled(enable)

    def _reinit_player(self):
        # Maybe this is how It's supposed to work?
        self._playback_slider.setValue(0)
        self._hide_show_timestamps(False)
        self._enable_controls(False)
        self._update_play_pause_to_play()

        self._player = QMediaPlayer(self)
        volume = self._audio_output.volume() if self._audio_output else self._DEFAULT_VOLUME
        self._audio_output = QAudioOutput(self._player)
        self._player.setAudioOutput(self._audio_output)

        self._player.positionChanged.connect(self._update_slider_position)
        self._player.durationChanged.connect(self._update_slider_duration)
        self._player.hasAudioChanged.connect(self._hide_show_timestamps)
        self._player.hasAudioChanged.connect(self._enable_controls)
        self._player.hasAudioChanged.connect(self._update_play_pause_to_play)

        self._player.positionChanged.connect(self.positionChanged.emit)
        self._player.durationChanged.connect(self.durationChanged.emit)
        self._player.mediaStatusChanged.connect(self.mediaStatusChanged.emit)
        self._player.playingChanged.connect(self._update_play_pause_ui)

        self._audio_output.volumeChanged.connect(lambda v: self._update_volume_slider(v * 100))
        self._audio_output.setVolume(volume)

    # class ConverterTask(QRunnable):
    #     class Signals(QObject):
    #         converted = Signal(Optional[QIODevice])
    #
    #     def __init__(self, invalid_device: QIODevice, converters: Iterable[Converter]):
    #         super().__init__()
    #         self._invalid_device = invalid_device
    #         self._converters = converters
    #         self.signals = self.Signals()
    #
    #     @Slot()
    #     def run(self):
    #         converter = next((conv for conv in self._converters if conv.supports_source(self._invalid_device)), None)
    #
    #         if converter is not None:
    #             try:
    #                 converted = converter.convert(self._invalid_device)
    #                 self.signals.converted.emit(converted)
    #             except Exception:
    #                 pass
    #
    # def _convert_if_invalid(self, status: QMediaPlayer.MediaStatus):
    #     if status == QMediaPlayer.MediaStatus.InvalidMedia:
    #         invalid_device = self._player.sourceDevice()
    #         if invalid_device:
    #             pool = QThreadPool.globalInstance()
    #             worker = self.ConverterTask(invalid_device, self._converters)
    #             worker.signals.converted.connect(self._try_open_converted)
    #             pool.start(worker)
    #
    # def _try_open_converted(self, converted: QIODevice):
    #     self.open_from_device(converted)
