import io
from typing import BinaryIO


class ArchiveWalker:
    def __init__(self, archive: BinaryIO, offset: int, length: int, prefix: bytes):
        self.archive = archive
        self.remaining = length
        self.archive.seek(offset)
        self.data_streams = [io.BytesIO(prefix), self.archive] if prefix else [self.archive]

    def read(self, read_length: int = -1) -> bytes:
        read_length = self._adjust_read_length(read_length)
        result = bytearray()
        while self._can_read(read_length):
            segment = self._read_segment(read_length)
            if segment:
                result.extend(segment)
                read_length -= len(segment)
            else:
                self.data_streams.pop(0)
        self._check_remaining(read_length)
        return bytes(result)

    def _adjust_read_length(self, read_length: int) -> int:
        if read_length < 0 or read_length > self.remaining:
            read_length = self.remaining
        return read_length

    def _can_read(self, read_length: int) -> bool:
        return self.data_streams and self.remaining > 0 and read_length > 0

    def _read_segment(self, read_length: int) -> bytes:
        segment = self.data_streams[0].read(read_length)
        if segment:
            self.remaining -= len(segment)
        return segment

    def _check_remaining(self, read_length: int):
        if self.remaining != 0 and read_length > 0:
            raise EOFError("Unexpected end of archive")