"""Small helpers against injection / resource exhaustion in files pyatlas reads or writes."""
from __future__ import annotations

import zipfile
from typing import Any

from .errors import AtlasBaseException, AtlasErrorCode

# a spreadsheet cell starting with one of these is evaluated as a formula by Excel / LibreOffice
_FORMULA_START = ("=", "+", "-", "@", "\t", "\r")


def neutralize_formula(v: Any) -> Any:
    """CSV/XLSX formula injection: prefix values that a spreadsheet would execute with an apostrophe."""
    if isinstance(v, str) and v.startswith(_FORMULA_START):
        return "'" + v
    return v


def restore_formula_escape(v: str) -> str:
    """Inverse of :func:`neutralize_formula` for values read back from our own exports."""
    if isinstance(v, str) and len(v) > 1 and v[0] == "'" and v[1:].startswith(_FORMULA_START):
        return v[1:]
    return v


def check_zip(z: zipfile.ZipFile, max_uncompressed_bytes: int, what: str = "ZIP") -> None:
    """Zip-bomb protection: total declared uncompressed size and compression ratio."""
    total = 0
    for info in z.infolist():
        total += info.file_size
        if info.compress_size and info.file_size / info.compress_size > 1000 and info.file_size > 50 * 1024 * 1024:
            raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST, f"{what}: suspicious compression ratio in {info.filename}")
    if max_uncompressed_bytes > 0 and total > max_uncompressed_bytes:
        raise AtlasBaseException(AtlasErrorCode.BAD_REQUEST,
                                 f"{what}: uncompressed size {total // (1024 * 1024)} MB exceeds the limit of "
                                 f"{max_uncompressed_bytes // (1024 * 1024)} MB")
