from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import pickle

from src.components.integrity import calculateChecksum, validateDatasetIntegrity


@dataclass
class MarkupSettings:
    # TODO: fragment size, overlap factor. Those can be changed at any time.
    # TODO: manual fragmentation with sliders and stuff.
    pass


class Project:
    name: str
    description: str
    datasetDir: Path
    projectFile: Path
    markupSettings: MarkupSettings
    markupDataset: pd.DataFrame
    datasetDirChecksum: str  # TODO: maintain something like index structure
    currentFileIdx: int  # to be able to recover project upon dataset changes

    def __init__(self, name: str, description: str, projectFileDir: Path, datasetDir: Path):
        self.name = name
        self.description = description
        self.datasetDir = datasetDir
        self.projectFile = projectFileDir / (self.name + '.mmp')
        self.markupSettings = MarkupSettings()
        self.markupDataset = pd.DataFrame(columns=['relativePath', 'start', 'end', 'description'])
        self.datasetDirChecksum = calculateChecksum(self.datasetDir)  # TODO: parallelize this
        self.currentFileIdx = 0


def loadProject(path: Path) -> Project:
    if not path.exists() or not path.is_file() or path.suffix != '.mm':
        raise FileNotFoundError(f"Invalid project file: {path}")
    try:
        with open(path, 'rb') as file:
            loaded_project = pickle.load(file)
            if not isinstance(loaded_project, Project):
                raise TypeError("File does not contain MM project.")
            validateDatasetIntegrity(loaded_project.datasetDir, loaded_project.datasetDirChecksum)
            return loaded_project
    except Exception as e:
        raise pickle.PickleError(f"Failed to load project from {path}: {e}")


def saveProject(project: Project):
    validateDatasetIntegrity(project.datasetDir, project.datasetDirChecksum)
    try:
        with open(project.projectFile, 'wb') as file:
            pickle.dump(project, file)
    except Exception as e:
        raise pickle.PickleError(f"Failed to save project to {project.projectFile}: {e}")


def exportMarkup(project: Project, path: Path):
    try:
        with open(path, 'wb') as file:
            pickle.dump(project.markupDataset, file)
    except Exception as e:
        raise RuntimeError(f"Failed to export markup to {path}: {e}")
