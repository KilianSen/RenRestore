import pathlib
from abc import ABCMeta
from typing import BinaryIO

from RenRestore.ArchiveFormats.Walker import ArchiveWalker
from RenRestore.ArchiveFormats.Format import ArchiveFormat


class ExtensionBasedArchiveFormat(ArchiveFormat, metaclass=ABCMeta):
    extension: str

    def detect(self, archive: BinaryIO) -> bool:
        return (pathlib.Path(archive.name).suffix[1::].lower().replace(".", "") ==
                self.extension.lower().replace(".", ""))


class HeaderBasedArchiveFormat(ArchiveFormat, metaclass=ABCMeta):
    magic_header: bytes

    def detect(self, archive: BinaryIO) -> bool:
        # Read the first few bytes of the archive and check if it matches the header
        first_bytes = archive.read(len(self.magic_header))
        archive.seek(0)
        return first_bytes == self.magic_header


class NoPostprocess(ArchiveFormat, metaclass=ABCMeta):
    def postprocess(self, source: ArchiveWalker) -> ArchiveWalker:
        return source


class NoPreprocess(ArchiveFormat, metaclass=ABCMeta):
    def preprocess(self, source: BinaryIO) -> BinaryIO:
        return source


class NoPrePostprocess(NoPostprocess, NoPreprocess, metaclass=ABCMeta):
    pass
