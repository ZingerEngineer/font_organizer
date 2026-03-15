"""File discovery and classification."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

FONT_EXTENSIONS: frozenset[str] = frozenset({".ttf", ".otf", ".woff", ".woff2"})


def is_font_file(path: Path) -> bool:
    return path.suffix.lower() in FONT_EXTENSIONS


def scan_directory(directory: Path) -> Iterator[Path]:
    """Yield all files (not directories) under directory recursively."""
    for path in directory.rglob("*"):
        if path.is_file():
            yield path


def partition_files(directory: Path) -> tuple[list[Path], list[Path]]:
    """Return (font_files, non_font_files) from a recursive directory scan."""
    fonts: list[Path] = []
    non_fonts: list[Path] = []
    for path in scan_directory(directory):
        if is_font_file(path):
            fonts.append(path)
        else:
            non_fonts.append(path)
    return fonts, non_fonts
