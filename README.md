# RenRestore - Python RPA Extractor Library

[![PyPI - Python Version](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![GitHub](https://img.shields.io/github/license/KilianSen/RenRestore)](https://github.com/KilianSen/RenRestore/blob/master/LICENSE)

## About

RenRestore is a Python library that allows you to extract files from RenPy's RPA archives.

## Archive Format Support
There are many different versions of the RPA archive format, some official and many unofficial. 
Therefor, RenRestore allows you to implement your own RPA archive format by subclassing the `ArchiveFormat` class.
The implemented archive formats can then be added to an `ArchiveFormatRegistry`.
This Registry can then be passed to the `RenRestore` class, which when tasked with extracting files from an RPA archive,
will try to detect the archive format and use the corresponding implementation (if available).

There is also the `AutoRegistry`, which will load in all available archive formats (file extension `.rpaf.py`) in a given directory.
This is used by default when creating a new `RenRestore` object, 
with the directory being the `/RenRestore/ArchiveFormats/Plugins/` directory.
By default, this directory contains some of the most common RPA archive formats.

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

log = logging.getLogger("RenRestore")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

class CustomArchiveFormat(ArchiveFormat):
    def __init__(self):
        super().__init__("CustomArchiveFormat", "Custom Archive Format", ["custom"])

    def extract(self, archive_path: str, output_directory: str):
        print(f"Extracting {archive_path} with {self.name} to {output_directory}")

registry = ArchiveFormatRegistry()

registry + CustomArchiveFormat # Yes, i know this is cursed, but currently the way to add an archive format to the registry.

restorer = RenRestore(create_output_directory=True, archive_format_registry=registry)

restorer.extract_files("custom_archive.custom", "output")
```