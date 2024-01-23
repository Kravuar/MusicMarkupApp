import os
from pathlib import Path

from PySide6.QtWidgets import QMessageBox


def validate_required_field(value, field_name):
    if not value:
        return field_name, f"Field is required."


def validate_non_equal_fields(first, second, first_field_name, second_field_name):
    if first == second:
        return first_field_name, f"Field should not be equal to {second_field_name}."


def validate_required_file(path: str, field_name):
    return _validate_required_path(path, field_name, False)


def validate_required_directory(path: str, field_name):
    return _validate_required_path(path, field_name, True)


def _validate_required_path(path: str, field_name, is_dir):
    required_error = validate_required_field(path, field_name)
    if required_error:
        return required_error

    path_obj = Path(path)
    file_type_matches = path_obj.is_dir() if is_dir else path_obj.is_file()
    if not (path_obj.exists() and file_type_matches):
        return field_name, f"The selected path is not a valid {'directory' if is_dir else 'file'}."


def show_error_message(errors, parent):
    QMessageBox.critical(
        parent,
        "Form Errors",
        _format_errors(errors),
        QMessageBox.StandardButton.Close
    )


def _format_errors(errors):
    if not errors:
        return "No errors"

    error_strings = [f"{field} -> {message}" for field, message in errors.items()]
    return os.linesep.join(error_strings)
