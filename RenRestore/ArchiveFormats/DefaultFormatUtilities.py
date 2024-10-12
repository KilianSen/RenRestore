import os
import pickle
import time
import zlib
from abc import ABCMeta
from collections.abc import Callable
from typing import BinaryIO, Optional, Tuple, Dict, cast, Iterable, Union

from RenRestore import FormatError, logging
from RenRestore.ArchiveFormats.Format import ArchiveFormat
from RenRestore.ArchiveFormats.Walker import ArchiveWalker
from RenRestore.ArchiveFormats.UtilityFormats import NoPrePostprocess

_logger = logging.get_logger()

class DefaultArchiveIndex(ArchiveFormat, metaclass=ABCMeta):
    def index(self, archive: BinaryIO, offset_and_key: Optional[Tuple[int, int]]) -> Dict[str, Iterable[Tuple[int, int, bytes]]]:
        offset: int
        key: Optional[int]

        if offset_and_key:
            offset, key = offset_and_key
        else:
            offset, key = self.find_offset_and_key(archive)

        archive.seek(offset)
        index: Dict[bytes, Iterable[Union[Tuple[int, int], Tuple[int, int, bytes]]]] = pickle.loads(zlib.decompress(archive.read()), encoding="bytes")
        normalize = lambda entry: [
            (*cast(Tuple[int, int], part), b"") if len(part) == 2 else cast(Tuple[int, int, bytes], part) for
            part in entry]

        if key is not None:
            # deobfuscate the index
            normal_index = {
                path: [(offset ^ key, length ^ key, start) for offset, length, start in normalize(entry)]
                for path, entry in index.items()}
        else:
            # normalise the index
            normal_index = {path: normalize(entry) for path, entry in index.items()}

        stringify = lambda path: path if isinstance(path, str) else path.decode("utf-8", "backslashreplace")

        return {stringify(path).replace("/", os.sep): data for path, data in normal_index.items()}


class DefaultArchiveExtraction(ArchiveFormat, metaclass=ABCMeta):
    def extract(self, index: Dict[str, Iterable[Tuple[int, int, bytes]]], archive: BinaryIO,
                on_exception: Callable[[Exception], ...]) -> Iterable[Tuple[str, Iterable[bytes]]]:
        for file_number, (path, data) in enumerate(index.items()):
            try:
                _logger.info(f"[{file_number / len(index):.1%}] Extracted: {path}")
                file_walk = ArchiveWalker(archive, *next(iter(data)))
                yield path, iter(file_walk.read, b"")

            except Exception as error:
                on_exception(error)


class DefaultFormatUtilities(NoPrePostprocess, DefaultArchiveIndex, DefaultArchiveExtraction, metaclass=ABCMeta):
    pass
