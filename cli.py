"""CLI argument parsing and Config dataclass."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    directory: Path
    dry_run: bool
    verbose: bool


def parse_args(argv: list[str] | None = None) -> Config:
    parser = argparse.ArgumentParser(
        description="Organize font files by font family name."
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing fonts to organize.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without modifying the filesystem.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed processing information.",
    )

    args = parser.parse_args(argv)

    if not args.directory.exists():
        parser.error(f"Directory does not exist: {args.directory}")
    if not args.directory.is_dir():
        parser.error(f"Path is not a directory: {args.directory}")

    return Config(
        directory=args.directory.resolve(),
        dry_run=args.dry_run,
        verbose=args.verbose,
    )
