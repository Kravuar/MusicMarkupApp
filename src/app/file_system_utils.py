from pathlib import Path


def iterate_files(directory_path, suffixes):
    directory = Path(directory_path)
    for file_path in directory.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in suffixes:
            yield file_path
