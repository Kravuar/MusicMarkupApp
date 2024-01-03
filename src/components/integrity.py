import hashlib
from pathlib import Path


class ChecksumError(Exception):
    pass


def calculateChecksum(directory: Path) -> str:
    hashMD5 = hashlib.md5()
    for filePath in sorted(directory.rglob('*')):
        if filePath.is_file():
            with open(filePath, 'rb') as file:
                hashMD5.update(file.read())
    return hashMD5.hexdigest()


def validateDatasetIntegrity(datasetDir: Path, checksum: str):
    current_checksum = calculateChecksum(datasetDir)
    if current_checksum != checksum:
        raise ChecksumError("Dataset integrity compromised. Checksums do not match.")
