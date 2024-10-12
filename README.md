# RenRestore - Python RPA Extractor Library

[![PyPI - Python Version](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![GitHub](https://img.shields.io/github/license/KilianSen/RenRestore)](https://github.com/KilianSen/RenRestore/blob/master/LICENSE)

## About

RenRestore extracts files from RenPy's RPA archives. It supports various RPA formats, both official and unofficial. You can implement custom formats by subclassing `ArchiveFormat` and adding them to an `ArchiveFormatRegistry`. The `RenRestore` class uses this registry to detect and handle different archive formats.

The `AutoRegistry` loads all available formats (with `.rpaf.py` extension) from the `/RenRestore/ArchiveFormats/Plugins/` directory by default.

## Installation

Currently, RenRestore is only available as source code. 

## Usage

### AutoRegistry
```python
import logging
from RenRestore import RenRestore

log = logging.getLogger("RenRestore")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

restorer = RenRestore(create_output_directory=True)
restorer.extract_files("scripts.rpa", "output")
```

### Custom Archive Format

```python
import logging
from RenRestore import RenRestore, ArchiveFormat, ArchiveFormatRegistry
from typing import Dict, Iterable, Tuple, Optional, BinaryIO, Callable

log = logging.getLogger("RenRestore")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)


class CustomArchiveFormat(ArchiveFormat):
    def extract(self, index: Dict[str, Iterable[Tuple[int, int, bytes]]], archive: BinaryIO,
                on_exception: Callable[[Exception], ...]) -> Iterable[Tuple[str, Iterable[bytes]]]:
        pass

    def index(self, archive: BinaryIO, offset_and_key: Optional[Tuple[int, int]]) -> Dict[
        str, Iterable[Tuple[int, int, bytes]]]:
        pass

    def postprocess(self, source: BinaryIO) -> BinaryIO:
        pass

    def preprocess(self, source: BinaryIO) -> BinaryIO:
        pass

    def find_offset_and_key(self, archive: BinaryIO) -> Tuple[int, Optional[int]]:
        pass

    def detect(self, archive: BinaryIO) -> bool:
        pass


registry = ArchiveFormatRegistry()

registry + CustomArchiveFormat  # Yes, i know this is cursed, but currently the way to add an archive format to the registry.

restorer = RenRestore(create_output_directory=True, format_registry=registry)

restorer.extract_files("custom_archive.custom", "output")
```