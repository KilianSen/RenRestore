from typing import Set, Type

from RenRestore.ArchiveFormats.Format import ArchiveFormat


class RenRestoreError(Exception):
    """Any error specific to RenRestore."""
    pass


class UnknownArchiveFormatError(RenRestoreError):
    def __init__(self, detected: Set[Type[ArchiveFormat]]) -> None:
        self.versions = detected
        super().__init__(f"Unknown archive format detected: {detected}")


class AmbiguousArchiveFormatError(RenRestoreError):
    def __init__(self, detected: Set[Type[ArchiveFormat]]) -> None:
        self.versions = detected
        super().__init__(f"Ambiguous archive version detected: {detected}")


class ErrorExtractingFile(RenRestoreError):
    def __init__(self, msg: str) -> None:
        super().__init__(f"Error extracting file: {msg}")


class FormatError(RenRestoreError):
    wrapped: Exception

    def __init__(self, exc: Exception) -> None:
        self.wrapped = exc
        super().__init__(f"Error in archive format: {exc}")
