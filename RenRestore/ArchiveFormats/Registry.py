import importlib.util
import os
from abc import ABCMeta
from inspect import isabstract
from typing import Set, Type, FrozenSet

from RenRestore.ArchiveFormats.Format import ArchiveFormat
from RenRestore.logging import get_logger

_log = get_logger()


class ArchiveFormatRegistry(metaclass=ABCMeta):
    __formats: Set[Type["ArchiveFormat"]]

    def __init__(self):
        self.__formats = set()

    def __add__(self, other: Type["ArchiveFormat"]):
        if other in self.__formats:
            _log.debug(f"Version {other.name} is already in the list of versions.")
            return False

        self.__formats.add(other)
        _log.debug(f"Added version {other.name} to the list of versions.")
        return True

    def __sub__(self, other: Type["ArchiveFormat"]):
        if other not in self.__formats:
            _log.debug(f"Version {other.name} is not in the list of versions.")
            return False

        self.__formats.remove(other)
        _log.debug(f"Removed version {other.name} from the list of versions.")
        return True

    def __contains__(self, item: Type["ArchiveFormat"]):
        return item in self.__formats

    @property
    def formats(self) -> FrozenSet[Type["ArchiveFormat"]]:
        return frozenset(self.__formats)


class NullRegistry(ArchiveFormatRegistry):
    """
        A registry that does not contain any formats.
    """

    __formats = frozenset()


class AutoRegistry(ArchiveFormatRegistry):
    """
        This registry will work like a plugin loader, watching a directory and importing every file ending in .rpaf.py
    """

    format_directory: str

    def __init__(self, format_directory: str):
        super().__init__()
        self.format_directory = format_directory
        self.load_formats()

    def load_formats(self):
        """
        Load all formats in the format directory into the registry
        :return:
        """
        for file in os.listdir(self.format_directory):
            if not file.endswith(".rpaf.py"):
                continue
            spec = importlib.util.spec_from_file_location(file[:-9], os.path.join(self.format_directory, file))
            module = importlib.util.module_from_spec(spec)
            e = spec.loader.exec_module(module)
            for attr in dir(module):
                if not isinstance(getattr(module, attr), type):
                    continue
                if not issubclass(getattr(module, attr), ArchiveFormat):
                    continue

                if isabstract(getattr(module, attr)):
                    continue
                if getattr(module, attr) in self:
                    continue

                self + getattr(module, attr)
