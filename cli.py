"""CLI argument parsing and Config dataclass."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from themes import THEME_NAMES


@dataclass(frozen=True)
class Config:
    directory: Path
    dry_run: bool
    verbose: bool
    theme: str        # theme name or "pick" to trigger interactive picker
    interactive: bool # computed: not --no-interactive AND stdout is a TTY
    no_tree: bool     # suppress tree preview


def parse_args(argv: list[str] | None = None) -> Config:
    from display import is_interactive

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
    parser.add_argument(
        "--theme",
        default="default",
        metavar="NAME",
        help=(
            f"Color theme. Choices: {', '.join(THEME_NAMES)}, pick. "
            "Pass 'pick' for an interactive menu."
        ),
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Disable all interactive prompts. Safe for piped/scripted use.",
    )
    parser.add_argument(
        "--no-tree",
        action="store_true",
        help="Suppress the tree preview of proposed changes.",
    )

    args = parser.parse_args(argv)

    if not args.directory.exists():
        parser.error(f"Directory does not exist: {args.directory}")
    if not args.directory.is_dir():
        parser.error(f"Path is not a directory: {args.directory}")

    if args.theme != "pick" and args.theme not in THEME_NAMES:
        parser.error(
            f"Unknown theme '{args.theme}'. "
            f"Valid choices: {', '.join(THEME_NAMES)}, pick"
        )

    return Config(
        directory=args.directory.resolve(),
        dry_run=args.dry_run,
        verbose=args.verbose,
        theme=args.theme,
        interactive=not args.no_interactive and is_interactive(),
        no_tree=args.no_tree,
    )
