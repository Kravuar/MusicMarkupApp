from pathlib import Path
from typing import Self

import pandas as pd
import pickle

from src.components.integrity import calculateDirectoryChecksum, validateDirectoryIntegrity, ChecksumError
from src.components.markup import MarkupSettings
from src.components.markupIndex import MarkupIndex
from src.internalSettings import AUDIO_FILES_PATTERN


class Project:
    def __init__(self, name: str, description: str, projectFileDir: Path, datasetDir: Path):
        self.name = name
        self.description = description
        self._datasetDir = datasetDir
        self._projectFile = projectFileDir / (self.name + '.mmp')
        self._markupSettings = MarkupSettings()
        self._markupDataFrame = pd.DataFrame(columns=['checksum', 'relativePath', 'start', 'end', 'description'])
        self._markupIndex = MarkupIndex(self._datasetDir, AUDIO_FILES_PATTERN)
        # TODO: parallelize checksum?
        self._datasetDirChecksum = calculateDirectoryChecksum(
            self._datasetDir,
            AUDIO_FILES_PATTERN
        )

    @classmethod
    def loadProject(cls, path: Path) -> Self:
        if not path.exists() or not path.is_file() or path.suffix != '.mm':
            raise FileNotFoundError(f"Invalid project file: {path}")
        try:
            with open(path, 'rb') as file:
                loaded_project = pickle.load(file)
                if not isinstance(loaded_project, Project):
                    raise TypeError("File does not contain MM project.")
                validateDirectoryIntegrity(
                    loaded_project.datasetDir,
                    AUDIO_FILES_PATTERN,
                    loaded_project.datasetDirChecksum
                )
                return loaded_project
        except ChecksumError as e:
            raise ProjectCorruptedException(loaded_project) from e
        except Exception as e:
            raise pickle.PickleError(f"Failed to load project from {path}: {e}")

    def restore(self):
        self._markupIndex.updateState()
        toUpdate = self._markupDataFrame[self._markupDataFrame['checksum'].isin(self._markupIndex)]
        updated = toUpdate['checksum'].map(lambda checksum: self._markupIndex.state[checksum].relativePath)
        self._markupDataFrame.loc[toUpdate.index, 'relativePath'] = updated

    def save(self):
        try:
            validateDirectoryIntegrity(
                self.datasetDir,
                AUDIO_FILES_PATTERN,
                self.datasetDirChecksum
            )
            with open(self.projectFile, 'wb') as file:
                pickle.dump(self, file)
        except ChecksumError as e:
            raise ProjectCorruptedException(self) from e
        except Exception as e:
            raise pickle.PickleError(f"Failed to save project to {self.projectFile}: {e}")

    def exportMarkup(self, path: Path):
        try:
            with open(path, 'wb') as file:
                pickle.dump(self.markupDataFrame, file)
        except Exception as e:
            raise RuntimeError(f"Failed to export markup to {path}: {e}")

    @property
    def datasetDir(self):
        return self._datasetDir

    @property
    def projectFile(self):
        return self._projectFile

    @property
    def markupSettings(self):
        return self._markupSettings

    @property
    def markupDataFrame(self):
        return self._markupDataFrame

    @property
    def datasetDirChecksum(self):
        return self._datasetDirChecksum


class ProjectCorruptedException(Exception):
    def __init__(self, project: Project):
        self._project = project

    @property
    def project(self):
        return self._project
