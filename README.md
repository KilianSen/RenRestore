# RenRestore - Python RPA Extractor Library

[![PyPI - Python Version](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![GitHub](https://img.shields.io/github/license/KilianSen/RenRestore)](https://github.com/KilianSen/RenRestore/blob/master/LICENSE)

## About

RenRestore is a Python library that allows you to extract files from RenPy's RPA archives.

## Installation

Currently, RenRestore is only available as source code. 

## Usage

```python
import logging
from RenRestore import RenRestore

log = logging.getLogger("RenRestore")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

restorer = RenRestore(create_output_directory=True)
restorer.extract_files("scripts.rpa", "output")
```