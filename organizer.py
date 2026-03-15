"""Orchestration — wires all modules together."""

from __future__ import annotations

from pathlib import Path

from cli import Config
from filesystem import move_font, trash_file
from metadata import get_family_name
from scanner import partition_files


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def log(tag: str, message: str, config: Config) -> None:
    """Print a tagged log line. Suppresses [VERBOSE] when verbose=False."""
    if tag == "VERBOSE" and not config.verbose:
        return
    print(f"[{tag}] {message}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_already_organized(path: Path, family_name: str) -> bool:
    """Return True if the font already lives inside its correct family directory."""
    return path.parent.name == family_name


# ---------------------------------------------------------------------------
# Per-file processors
# ---------------------------------------------------------------------------

def process_font(path: Path, root_dir: Path, config: Config) -> None:
    """Extract family name, check organization status, move if needed."""
    family_name, source = get_family_name(path)

    if not family_name:
        log("ERROR", f"Unable to determine family name: {path.name}", config)
        return

    log("VERBOSE", f"Family '{family_name}' (source: {source}) — {path.name}", config)

    if is_already_organized(path, family_name):
        log("SKIP", f"{path.name} — already in {family_name}/", config)
        return

    family_dir = root_dir / family_name

    if config.dry_run:
        log("DRY", f"Would move {path.name} → {family_name}/", config)
        return

    try:
        destination = move_font(path, family_dir, dry_run=False)
        log("FONT", f"{path.name} → {destination.parent.name}/", config)
    except PermissionError:
        log("ERROR", f"Permission denied: {path.name} — try: sudo font-organizer {path.parent}", config)
    except Exception as exc:
        log("ERROR", f"Failed to move {path.name}: {exc}", config)


def process_non_font(path: Path, config: Config) -> None:
    """Trash a non-font file."""
    if config.dry_run:
        log("DRY", f"Would trash {path.name}", config)
        return

    try:
        trash_file(path, dry_run=False)
        log("TRASH", f"{path.name} → recycle bin", config)
    except PermissionError:
        log("ERROR", f"Permission denied: {path.name} — try: sudo font-organizer {path.parent}", config)
    except RuntimeError as exc:
        log("ERROR", str(exc), config)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run(config: Config) -> None:
    """Scan directory and process all files."""
    log("VERBOSE", f"Scanning: {config.directory}", config)

    fonts, non_fonts = partition_files(config.directory)

    log("VERBOSE", f"Found {len(fonts)} font(s), {len(non_fonts)} non-font(s)", config)

    # Pass 1 — move fonts into family directories
    for path in fonts:
        process_font(path, config.directory, config)

    # Pass 2 — trash non-font files
    for path in non_fonts:
        process_non_font(path, config)
