"""Custom exceptions for Data Manager."""


class DataManagerError(Exception):
    """Base exception for Data Manager."""


class UnsupportedFormatError(DataManagerError):
    """Raised when file format is not supported."""

    def __init__(self, extension: str, supported: list):
        super().__init__(
            f"Unsupported format: '{extension}'. "
            f"Supported: {', '.join(supported)}"
        )


class DataLoadError(DataManagerError):
    """Raised when data loading fails."""

    def __init__(self, path: str, reason: str):
        super().__init__(f"Failed to load '{path}': {reason}")


class DataSaveError(DataManagerError):
    """Raised when data saving fails."""

    def __init__(self, path: str, reason: str):
        super().__init__(f"Failed to save '{path}': {reason}")


class FileNotFoundError(DataManagerError):
    """Raised when file does not exist."""

    def __init__(self, path: str):
        super().__init__(f"File not found: {path}")
