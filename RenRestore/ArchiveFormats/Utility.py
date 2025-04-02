import pathlib
import typing
from abc import ABCMeta
from typing import BinaryIO, Callable, Iterable, Optional

from RenRestore import ArchiveFormatRegistry
from RenRestore.logging import _logger as __logger
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
    def postprocess(self, source: BinaryIO) -> BinaryIO:
        return source


class NoPreprocess(ArchiveFormat, metaclass=ABCMeta):
    def preprocess(self, source: BinaryIO) -> BinaryIO:
        return source


class NoPrePostprocess(NoPostprocess, NoPreprocess, metaclass=ABCMeta):
    pass

def inject_process_in_format[X: typing.Type[ArchiveFormat]](format: X, preprocess: Optional[Callable[[BinaryIO], BinaryIO]] = None, postprocess: Optional[Callable[[BinaryIO], BinaryIO]] = None) -> typing.Type[X]:
    def pass_through(source: BinaryIO) -> BinaryIO:
        return source

    class InterceptedFormat(format):
        def postprocess(self, source: BinaryIO) -> BinaryIO:
            return (postprocess if postprocess is not None else pass_through)(super().postprocess(source))

        def preprocess(self, source: BinaryIO) -> BinaryIO:
            return (preprocess if preprocess is not None else pass_through)(super().preprocess(source))

    __logger.debug(
        f"Created new class {InterceptedFormat} that inherits from {format} and overrides postprocess to {postprocess}")

    return InterceptedFormat


def inject_process_in_registry[X: ArchiveFormatRegistry](registry: X, preprocess: Optional[Callable[[BinaryIO], BinaryIO]] = None, postprocess: Optional[Callable[[BinaryIO], BinaryIO]] = None) -> X:

    __logger.debug(f"Injecting postprocess {postprocess} into registry {registry}")

    # Get the arguments of the registry constructor and their values
    registry_arguments = {
        arg: getattr(registry, arg) for arg in
        (
            type(registry).__init__.__code__.co_varnames[1:] if
            type(registry).__init__.__code__.co_varnames[0] == "self" else
            type(registry).__init__.__code__.co_varnames
        )
    }

    # Create a new instance of the registry
    new_registry = type(registry)(**registry_arguments)
    new_registry._formats = set()

    __logger.debug(f"Created new {type(new_registry)} registry with arguments {registry_arguments}")

    # Iterate over all the formats in the registry
    for archive_format in registry.formats:

        # Create a new class that inherits from the original class
        # and overrides the postprocess method
        new_format: typing.Type[ArchiveFormat] = inject_process_in_format(archive_format, preprocess, postprocess)
        new_registry + new_format
        __logger.debug(f"Injected postprocess format {new_format} in {archive_format}")

    __logger.debug(f"Injected postprocess into registry {new_registry}!")
    return new_registry

def inject_multi_process_in_registry[X: ArchiveFormatRegistry](registry: X,
                                                               preprocessors: Optional[Iterable[Callable[[BinaryIO], BinaryIO]]] = None,
                                                               postprocessors: Optional[Iterable[Callable[[BinaryIO], BinaryIO]]] = None) -> X:
    __logger.debug(f"Injecting multiple postprocessors {" -> ".join([p.__repr__() for p in postprocessors][::-1])} into registry {registry}")

    current_registry = registry

    for preprocessor in (preprocessors if preprocessors is not None else [])[::-1]:
        current_registry = inject_process_in_registry(current_registry, preprocessor, None)

    for postprocessor in (postprocessors if postprocessors is not None else [])[::-1]:
        current_registry = inject_process_in_registry(current_registry, None, postprocessor)


    return current_registry