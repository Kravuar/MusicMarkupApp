import os

from PyQt5 import QtWidgets
from pathlib import Path


def validateRequiredField(value, fieldName):
    if not value:
        return fieldName, f"Field is required."


def validateRequiredFile(path: str, fieldName):
    return __validateRequiredPath__(path, fieldName, False)


def validateRequiredDirectory(path: str, fieldName):
    return __validateRequiredPath__(path, fieldName, True)


def __validateRequiredPath__(path: str, fieldName, isDir):
    requiredError = validateRequiredField(path, fieldName)
    if requiredError:
        return requiredError

    path_obj = Path(path)
    fileTypeMatches = path_obj.is_dir() if isDir else path_obj.is_file()
    if not (path_obj.exists() and fileTypeMatches):
        return fieldName, f"The selected path is not a valid {'directory' if isDir else 'file'}."


def showErrorMessage(errors, parent):
    QtWidgets.QMessageBox.critical(
        parent,
        "Form Errors",
        __formatErrors__(errors),
        QtWidgets.QMessageBox.Close
    )


def __formatErrors__(errors):
    if not errors:
        return "No errors"

    error_strings = [f"{field} -> {message}" for field, message in errors.items()]
    return os.linesep.join(error_strings)
