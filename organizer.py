"""Orchestration — wires all modules together."""

from __future__ import annotations

from pathlib import Path

import display
from cli import Config
from filesystem import move_font, trash_file
from metadata import get_family_name
from scanner import find_empty_dirs, is_font_file, scan_directory
from themes import ThemeSpec, get_theme


# ---------------------------------------------------------------------------
# Internal logging shim
# ---------------------------------------------------------------------------

def _log(tag: str, message: str, theme: ThemeSpec, config: Config) -> None:
    """Gate VERBOSE lines, then delegate rendering to display."""
    if tag == "VERBOSE" and not config.verbose:
        return
    display.render_log_line(tag, message, theme)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_moves(fonts: list[Path]) -> list[tuple[Path, str]]:
    """Return (path, family_name) pairs for tree preview. No filesystem side effects."""
    result: list[tuple[Path, str]] = []
    for path in fonts:
        family_name, _ = get_family_name(path)
        if family_name:
            result.append((path, family_name))
    return result


def _is_already_organized(path: Path, family_name: str) -> bool:
    return path.parent.name == family_name


# ---------------------------------------------------------------------------
# Per-file processors
# ---------------------------------------------------------------------------

def process_font(path: Path, root_dir: Path, config: Config, theme: ThemeSpec) -> None:
    """Extract family name, check organization status, move if needed."""
    family_name, source = get_family_name(path)

    if not family_name:
        _log("ERROR", f"Unable to determine family name: {path.name}", theme, config)
        return

    _log("VERBOSE", f"Family '{family_name}' (source: {source}) — {path.name}", theme, config)

    if _is_already_organized(path, family_name):
        _log("SKIP", f"{path.name} — already in {family_name}/", theme, config)
        return

    family_dir = root_dir / family_name

    if config.dry_run:
        _log("DRY", f"Would move {path.name} → {family_name}/", theme, config)
        return

    try:
        destination = move_font(path, family_dir, dry_run=False)
        _log("FONT", f"{path.name} → {destination.parent.name}/", theme, config)
    except PermissionError:
        _log("ERROR", f"Permission denied: {path.name} — try: sudo font-organizer {path.parent}", theme, config)
    except Exception as exc:
        _log("ERROR", f"Failed to move {path.name}: {exc}", theme, config)


def process_non_font(path: Path, config: Config, theme: ThemeSpec) -> None:
    """Trash a non-font file."""
    if config.dry_run:
        _log("DRY", f"Would trash {path.name}", theme, config)
        return

    try:
        trash_file(path, dry_run=False)
        _log("TRASH", f"{path.name} → recycle bin", theme, config)
    except PermissionError:
        _log("ERROR", f"Permission denied: {path.name} — try: sudo font-organizer {path.parent}", theme, config)
    except RuntimeError as exc:
        _log("ERROR", str(exc), theme, config)


def process_empty_dir(path: Path, config: Config, theme: ThemeSpec) -> None:
    """Trash an empty directory."""
    if config.dry_run:
        _log("DRY", f"Would trash empty dir: {path.name}/", theme, config)
        return

    try:
        trash_file(path, dry_run=False)
        _log("TRASH", f"{path.name}/ → recycle bin (empty dir)", theme, config)
    except PermissionError:
        _log("ERROR", f"Permission denied: {path.name}/ — try: sudo font-organizer {path.parent}", theme, config)
    except RuntimeError as exc:
        _log("ERROR", str(exc), theme, config)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run(config: Config) -> None:
    """Scan directory, preview changes, confirm, then execute."""

    # 1. Resolve theme — run picker if requested
    theme_name = config.theme if config.theme != "pick" else "default"
    theme = get_theme(theme_name)

    if config.theme == "pick":
        if config.interactive:
            chosen = display.run_theme_picker("default")
            theme = get_theme(chosen)
        else:
            display.render_log_line(
                "VERBOSE",
                "--theme pick requires an interactive terminal. Using 'default'.",
                theme,
            )

    # 2. Scan with progress spinner
    _log("VERBOSE", f"Scanning: {config.directory}", theme, config)

    fonts: list[Path] = []
    non_fonts: list[Path] = []

    with display.scan_progress("Scanning for fonts...", theme) as progress:
        task = progress.add_task("", total=None)
        for path in scan_directory(config.directory):
            progress.advance(task)
            if is_font_file(path):
                fonts.append(path)
            else:
                non_fonts.append(path)

    # 3. Find pre-existing empty directories
    pre_empty = find_empty_dirs(config.directory)

    # 4. Summary panel
    display.print_summary_panel(len(fonts), len(non_fonts), config.directory, theme)

    # 5. Tree preview (unless suppressed)
    if not config.no_tree:
        moves = _compute_moves(fonts)
        tree = display.build_proposal_tree(
            config.directory, moves, non_fonts, theme, empty_dirs=pre_empty
        )
        display.print_tree(tree)

    # 6. Confirmation gate (skip in dry-run — it's already preview-only)
    if not config.dry_run and config.interactive:
        if not display.confirm_proceed(theme):
            _log("VERBOSE", "Aborted by user.", theme, config)
            return

    # 7. Execute — Pass 1: fonts
    _log("VERBOSE", f"Found {len(fonts)} font(s), {len(non_fonts)} non-font(s)", theme, config)
    for path in fonts:
        process_font(path, config.directory, config, theme)

    # Pass 2: non-fonts
    for path in non_fonts:
        process_non_font(path, config, theme)

    # Pass 3: empty directories — loop handles cascading:
    # trashing a deep empty dir may expose a now-empty parent
    if not config.dry_run:
        empties = find_empty_dirs(config.directory)
        while empties:
            for d in empties:
                process_empty_dir(d, config, theme)
            empties = find_empty_dirs(config.directory)
    else:
        # In dry-run show pre-existing empties; post-move empties are unpredictable
        for d in pre_empty:
            process_empty_dir(d, config, theme)
