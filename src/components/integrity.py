import hashlib
from pathlib import Path


class ChecksumError(Exception):
    pass

def calculateDirectoryChecksum(directory: Path, pattern: str) -> str:
    hashMD5 = hashlib.md5()
    for filePath in directory.rglob(pattern):
        if filePath.is_file():
            with open(filePath, 'rb') as file:
                hashMD5.update(file.read())
    return hashMD5.hexdigest()


def validateDirectoryIntegrity(directory: Path, pattern: str, checksum: str):
    current_checksum = calculateDirectoryChecksum(directory, pattern)
    if current_checksum != checksum:
        raise ChecksumError("Dataset integrity compromised. Checksums do not match.")
