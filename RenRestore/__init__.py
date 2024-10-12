import os
import time
import traceback
from collections.abc import Callable
from typing import (
    Tuple,
    Optional,
    Type,
    FrozenSet, Set, )

from RenRestore.ArchiveFormats.Format import ArchiveFormat
from RenRestore.ArchiveFormats.Registry import ArchiveFormatRegistry, AutoRegistry
from RenRestore.errors import (
    ErrorExtractingFile,
    AmbiguousArchiveFormatError,
    UnknownArchiveFormatError, FormatError,
)
from RenRestore.logging import get_logger

_logger = logging.get_logger()


class RenRestore:
    """A class for extracting RPA archives."""

    output_path: str
    create_output_directory: bool
    continue_on_error: bool

    extra_formats: FrozenSet[Type[ArchiveFormat]]
    """Additional formats that are not in the registry."""

    format_registry: ArchiveFormatRegistry
    """The registry that will be used to detect the archive format."""

    @property
    def formats(self) -> FrozenSet[Type[ArchiveFormat]]:
        """
            The formats that the library will use to extract/detect the archive.
        """
        return self.format_registry.formats | self.extra_formats

    def __init__(self,
                 output_path: Optional[str] = None,
                 create_output_directory: bool = False,
                 continue_on_error: bool = False,
                 format_registry: ArchiveFormatRegistry = None,
                 extra_formats: Optional[FrozenSet[Type[ArchiveFormat]]] = None) -> None:

        self.format_registry = format_registry
        if not format_registry:
            self.format_registry = AutoRegistry(
                os.path.join(os.path.abspath(os.path.dirname(__file__)), "ArchiveFormats", "Plugins"))

        self.extra_formats = extra_formats if extra_formats else frozenset()

        self.output_path = os.path.abspath(output_path) if output_path else os.getcwd()
        self.create_output_directory = create_output_directory

        self.continue_on_error = continue_on_error

    def extract_files(self,
                      file_path: str,
                      output_override: Optional[str] = None,
                      format_override: Optional[Type[ArchiveFormat]] = None,
                      offset_and_key_override: Optional[Tuple[int, int]] = None) -> None:
        """
        Extracts files from an archive.

        :param file_path: The path to the archive.
        :param output_override: The path to the output directory.
        :param format_override: The format to use to extract the archive.
        :param offset_and_key_override: The offset and key to use to extract the archive.

        :raises ErrorExtractingFile: If an error occurs while extracting a file.

        :raises UnknownArchiveFormatError: If the archive format is unknown. No format was detected.
        This could be a not supported format or an error in the archive/plugin.

        :raises AmbiguousArchiveFormatError: While detecting the archive format, more than one format was detected.
        This could be an implementation error, a problem with the archive.

        :raises FormatError: Is an exception wrapper for any error that occurs while processing the archive,
        this is defined in the format plugin and should be a state that is not recoverable,
        therefore the extraction should be stopped or the error ignored.

        :raises NotADirectoryError: If the output path is not a directory.

        :raises OSError: If an error occurs while opening the archive.
        """

        output_path = os.path.abspath(output_override) if output_override else self.output_path
        file_path = os.path.abspath(file_path)

        _logger.info(f"Extracting files from {file_path}.")

        if self.create_output_directory and not os.path.exists(output_path):
            _logger.debug(f"Creating output directory: {output_path}")
            os.makedirs(output_path)

        if not os.path.isdir(output_path):
            raise NotADirectoryError(f"The output path {output_path} is not a directory.")

        _logger.debug(f"Output directory: {output_path}")
        archive_format = format_override() if format_override else (
            self.detect_archive_format(file_path, False, self.formats))

        if archive_format is None:
            raise UnknownArchiveFormatError(set())

        def try_catch_method[X, Y](source: X, method: Callable[[X], Y],
                                   on_exception: Callable[[Exception], ...] | Exception) -> Y:
            """
            Tries to call a method with an object as a parameter and catches any exception that occurs.

            :param source: The object to pass to the method.
            :param method: The method to call.
            :param on_exception: The method to call if an exception occurs. If this is an exception, it will be raised.

            :return: The result of the method.
            """
            try:
                return method(source)
            except Exception as err:
                _logger.debug(f"Exception bordered in {method.__name__}: {err}")
                if isinstance(on_exception, Exception):
                    raise on_exception from err
                on_exception(err)

        def on_exception_in_extract(raised_error: Exception) -> None:
            """
            Handles an exception that occurs while extracting a file.

            :param raised_error: The exception that occurred.

            :raises ErrorExtractingFile: If the error is not a FormatError and continue_on_error is False.

            :return: None
            """
            if not self.continue_on_error:
                if isinstance(raised_error, FormatError):
                    raise raised_error
                raise ErrorExtractingFile(traceback.format_exc()) from raised_error

            _logger.error(f"Extractions exception: {raised_error} continuing per instruction.")

        with (try_catch_method(open(file_path, "rb"), archive_format.preprocess, FormatError) as archive):
            try:
                offset_and_key = offset_and_key_override
                if not offset_and_key_override:
                    _logger.debug(f"Finding padding and key for {file_path}")
                    offset_and_key = archive_format.find_offset_and_key(archive)
                _logger.debug(f"Using offset and key found: {offset_and_key}")

                _logger.debug(f"Indexing {file_path}")
                index = archive_format.index(archive, offset_and_key)
                _logger.debug(f"Extracting {file_path}")
                extract = archive_format.extract(index, archive, on_exception_in_extract)
                _logger.debug(f"Writing files to {output_path}")
                for target_file, segments in extract:

                    target_file_path = os.path.join(output_path, target_file)

                    if not os.path.exists(os.path.dirname(target_file_path)):
                        os.makedirs(os.path.dirname(target_file_path))

                    with try_catch_method(open(target_file_path, "wb"),
                                          archive_format.postprocess, FormatError) as output_file:
                        for segment in segments:
                            output_file.write(segment)
            except Exception as error:
                on_exception_in_extract(error)

    def detect_archive_format(self,
                              archive: str,
                              use_registered_formats: bool = True,
                              additional_formats: FrozenSet[Type[ArchiveFormat]] = None) -> ArchiveFormat:
        """
        Detects the archive format of the archive.

        :param archive: The path to the archive.
        :param use_registered_formats: Whether to use the registered formats.
        :param additional_formats: Additional formats to use to detect the archive format.

        :raises UnknownArchiveFormatError: If the archive format is unknown. No format was detected.
        This could be a not supported format or an error in the archive/plugin.

        :raises AmbiguousArchiveFormatError: While detecting the archive format, more than one format was detected.
        This could be an implementation error, a problem with the archive.

        :raises OSError: If an error occurs while opening the archive.

        :return: The archive format that was detected.
        """

        formats = additional_formats if additional_formats else set()
        if use_registered_formats:
            formats |= self.formats

        matches: Set[Type[ArchiveFormat]] = set()
        with open(archive, "rb") as file:
            for possible_format in formats:
                if possible_format().detect(file):
                    matches.add(possible_format)
                file.seek(0)

        if len(matches) == 0:
            raise UnknownArchiveFormatError(matches)

        if len(matches) > 1:
            raise AmbiguousArchiveFormatError(matches)

        return next(iter(matches))()
