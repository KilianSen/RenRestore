from abc import ABCMeta, abstractmethod
from typing import BinaryIO, Tuple, Optional, Dict, Iterable, Callable

from RenRestore.logging import get_logger

_log = get_logger()


class ArchiveFormat(metaclass=ABCMeta):
    name: str

    @abstractmethod
    def detect(self, archive: BinaryIO) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def find_offset_and_key(self, archive: BinaryIO) -> Tuple[int, Optional[int]]:
        raise NotImplementedError()

    @abstractmethod
    def preprocess(self, source: BinaryIO) -> BinaryIO:
        raise NotImplementedError()

    @abstractmethod
    def extract(self, index: Dict[str, Iterable[Tuple[int, int, bytes]]], archive: BinaryIO,
                on_exception: Callable[[Exception], ...]) -> Iterable[Tuple[str, Iterable[bytes]]]:
        raise NotImplementedError()

    @abstractmethod
    def postprocess(self, source: BinaryIO) -> BinaryIO:
        raise NotImplementedError()

    @abstractmethod
    def index(self, archive: BinaryIO, offset_and_key: Optional[Tuple[int, int]]) -> Dict[
        str, Iterable[Tuple[int, int, bytes]]]:
        raise NotImplementedError()
