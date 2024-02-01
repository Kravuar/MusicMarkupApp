AUDIO_FILES_PATTERN = ['.mp3', '.wav', '.flac', '.ogg', '.midi', '.mid']
MIDI_SF_PATH = 'resources/SGM-V2.01.sf2'
PROJECT_FILE_SUFFIX = '.mmp'
MARKUP_FILE_SUFFIX = '.mmd'
SAVE_PROJECT_AS_FILE_FILTER = f"MM Project (*{PROJECT_FILE_SUFFIX});;All Files (*)"
SAVE_DATAFRAME_AS_FILE_FILTER = f"DataFrame (*{MARKUP_FILE_SUFFIX});;All Files (*)"
OPENAI_EXPANDER_MODEL = 'gryphe/mythomax-L2-13b'
OPENAI_SYSTEM_EXPANDER_PROMPT = 'Вы музыкальный продюсер, помогающий описать музыкальный датасет, вам будут предоставлены небольшие текстовые описания музыкальных фрагментов, вам нужно их расширить (придерживаясь стиля общения и терминологии продюсера).'
