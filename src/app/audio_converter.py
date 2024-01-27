import io
import tempfile
from pathlib import Path

from midi2audio import FluidSynth
from pydub import AudioSegment

from src.config import MIDI_SF_PATH


def convert_to_mp3(file_path: Path) -> bytes:
    audio_format = file_path.suffix.replace('.', '').lower()

    if audio_format in ['mid', 'midi']:
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td) / 'temp'
            FluidSynth(MIDI_SF_PATH).midi_to_audio(file_path, temp)

            wav_audio = AudioSegment.from_wav(temp)
            mp3_buffer = io.BytesIO()
            wav_audio.export(mp3_buffer, format='mp3')
            return mp3_buffer.getvalue()
    else:
        audio = AudioSegment.from_file(file_path, format=audio_format)
        mp3 = io.BytesIO()

        if audio_format != 'mp3':
            audio.export(mp3, format='mp3')

        return mp3.getvalue()
