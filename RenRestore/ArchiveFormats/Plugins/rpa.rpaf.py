from typing import BinaryIO, Tuple, Optional

from RenRestore.ArchiveFormats.DefaultFormatUtilities import DefaultFormatUtilities
from RenRestore.ArchiveFormats.Utility import HeaderBasedArchiveFormat, ExtensionBasedArchiveFormat


class RPA1(ExtensionBasedArchiveFormat, DefaultFormatUtilities):
    name = "RPA-1.0"
    extension = ".rpi"

    def find_offset_and_key(self, archive: BinaryIO) -> Tuple[int, Optional[int]]:
        return 0, None


class RPA2(HeaderBasedArchiveFormat, DefaultFormatUtilities):
    name = "RPA-2.0"
    magic_header = b"RPA-2.0"

    def find_offset_and_key(self, archive: BinaryIO) -> Tuple[int, Optional[int]]:
        offset = int.from_bytes(bytes.fromhex(archive.readline()[8:].decode()), 'big')
        key = None
        return offset, key


class RPA3(HeaderBasedArchiveFormat, DefaultFormatUtilities):
    name = "RPA-3.0"
    magic_header = b"RPA-3.0"

    def find_offset_and_key(self, archive: BinaryIO) -> Tuple[int, Optional[int]]:
        raw = archive.readline().split()
        offset = int.from_bytes(bytes.fromhex(raw[1].decode()), 'big')
        key = int.from_bytes(bytes.fromhex(raw[2].decode()), 'big')
        return offset, key


class RPA4(RPA3, DefaultFormatUtilities):
    """Uncommon variants of the RPA-3.0 format."""

    name = "RPA4"
    magic_header = b"unused"

    def detect(self, archive: BinaryIO) -> bool:
        rpa32 = RPA3()
        rpa40 = RPA3()

        rpa32.name = "RPA-3.2"
        rpa40.name = "RPA-4.0"

        rpa32.magic_header = b"RPA-3.2"
        rpa40.magic_header = b"RPA-4.0"

        return rpa32.detect(archive) or rpa40.detect(archive)
