"""Orchestration — wires all modules together."""

from __future__ import annotations

from pathlib import Path

from . import display
from . import grouper
from .cli import Config
from .filesystem import make_font_filename, move_font, trash_file
from .metadata import get_family_name, get_variant_name
from .scanner import find_empty_dirs, is_font_file, scan_directory
from .themes import ThemeSpec, get_theme


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

def _normalize_dir_name(family_name: str) -> str:
    """Title-case a family name for use as a directory name."""
    return family_name.strip().title()


def _build_raw_family_map(fonts: list[Path]) -> dict[Path, str]:
    """Return {path: raw_family_name} for every font that has a family name."""
    result: dict[Path, str] = {}
    for path in fonts:
        name, _ = get_family_name(path)
        if name:
            result[path] = name
    return result


def _compute_moves(
    fonts: list[Path],
    raw_family_map: dict[Path, str],
    canonical_map: dict[str, str],
) -> list[tuple[Path, str, str]]:
    """Return (path, dir_name, new_filename) triples for the tree preview.

    Uses canonical family names so the preview reflects the actual grouping.
    No filesystem side effects.
    """
    result: list[tuple[Path, str, str]] = []
    for path in fonts:
        raw_name = raw_family_map.get(path)
        if not raw_name:
            continue
        canonical = canonical_map.get(raw_name, raw_name)
        meta_variant, _ = get_variant_name(path, raw_name)
        variant = grouper.derive_variant(raw_name, canonical, meta_variant)
        dir_name = _normalize_dir_name(canonical)
        new_filename = make_font_filename(canonical, variant, path.suffix)
        result.append((path, dir_name, new_filename))
    return result


def _is_already_organized(path: Path, dir_name: str, new_filename: str) -> bool:
    """Return True only when the file is in the correct dir AND has the right name."""
    return path.parent.name == dir_name and path.name == new_filename


# ---------------------------------------------------------------------------
# Per-file processors
# ---------------------------------------------------------------------------

def process_font(
    path: Path,
    root_dir: Path,
    config: Config,
    theme: ThemeSpec,
    canonical_family: str | None = None,
    original_family: str | None = None,
) -> None:
    """Rename and move a font into its (canonical) family directory.

    When canonical_family is provided the caller has already resolved grouping;
    otherwise family name is extracted fresh from metadata.
    """
    if canonical_family is not None:
        family_name = canonical_family
        fam_source = "grouped" if original_family and original_family != canonical_family else "metadata"
        raw_name = original_family or canonical_family
        meta_variant, var_source = get_variant_name(path, raw_name)
        variant_name = grouper.derive_variant(raw_name, canonical_family, meta_variant)
        if variant_name != meta_variant:
            var_source = "grouped"
    else:
        family_name, fam_source = get_family_name(path)
        if not family_name:
            _log("ERROR", f"Unable to determine family name: {path.name}", theme, config)
            return
        variant_name, var_source = get_variant_name(path, family_name)

    dir_name = _normalize_dir_name(family_name)
    new_filename = make_font_filename(family_name, variant_name, path.suffix)
    family_dir = root_dir / dir_name

    _log(
        "VERBOSE",
        f"Family '{dir_name}' ({fam_source}), variant '{variant_name}' ({var_source}) — {path.name}",
        theme,
        config,
    )

    if _is_already_organized(path, dir_name, new_filename):
        _log("SKIP", f"{path.name} — already organized", theme, config)
        return

    if config.dry_run:
        if path.parent == family_dir:
            _log("DRY", f"Would rename {path.name} → {new_filename}", theme, config)
        else:
            _log("DRY", f"Would move {path.name} → {dir_name}/{new_filename}", theme, config)
        return

    try:
        destination = move_font(path, family_dir, dry_run=False, new_name=new_filename)
        _log("FONT", f"{path.name} → {destination.parent.name}/{destination.name}", theme, config)
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


def consolidate_dirs(root_dir: Path, config: Config, theme: ThemeSpec) -> None:
    """Second-pass check: merge any family directories whose names share a prefix.

    After the first organisation pass some directories may still be split
    if the canonical grouping didn't resolve them (e.g. the canonical name
    did not appear in the original raw names set).  This pass looks at the
    actual directory names on disk and merges any that have a prefix match.
    """
    subdirs = [p for p in root_dir.iterdir() if p.is_dir()]
    if len(subdirs) < 2:
        return

    dir_name_set = {d.name for d in subdirs}
    # Build canonical map from directory names (title-cased, as on disk)
    dir_canonical = grouper.build_canonical_map(dir_name_set)

    # Directories that need to be merged into a shorter canonical name
    to_merge = {d: dir_canonical[d.name] for d in subdirs if dir_canonical[d.name] != d.name}

    if not to_merge:
        _log("VERBOSE", "Post-move check: no additional groupings found.", theme, config)
        return

    for source_dir, canonical_name in to_merge.items():
        _log(
            "VERBOSE",
            f"Post-move grouping: '{source_dir.name}' → '{canonical_name}/'",
            theme,
            config,
        )
        for file in list(source_dir.iterdir()):
            if file.is_file() and is_font_file(file):
                # Re-process with the directory name as the original family hint
                process_font(
                    file,
                    root_dir,
                    config,
                    theme,
                    canonical_family=canonical_name,
                    original_family=source_dir.name,
                )
        # Empty dirs are caught by Pass 3 (find_empty_dirs loop)


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

    # 4. Pre-move check: build canonical family map across all fonts
    #    Groups fonts that share a family name prefix (e.g. "911 Porscha" and
    #    "911 Porscha Condensed") into a single canonical family.
    raw_family_map = _build_raw_family_map(fonts)
    canonical_map = grouper.build_canonical_map(set(raw_family_map.values()))

    grouped_count = sum(1 for k, v in canonical_map.items() if k != v)
    if grouped_count:
        _log(
            "VERBOSE",
            f"Pre-move grouping: {grouped_count} variant family name(s) resolved to canonical.",
            theme,
            config,
        )

    # 5. Banner + summary panel
    display.print_banner(theme)
    display.print_summary_panel(len(fonts), len(non_fonts), config.directory, theme)

    # 6. Tree preview with interactive A/V/C menu (unless suppressed)
    if not config.no_tree:
        moves = _compute_moves(fonts, raw_family_map, canonical_map)
        tree = display.build_proposal_tree(
            config.directory, moves, non_fonts, theme, empty_dirs=pre_empty
        )
        total_items = len(moves) + len(non_fonts) + len(pre_empty)

        if not config.dry_run:
            apply = display.interactive_tree_view(
                tree, theme, total_items, interactive=config.interactive
            )
            if not apply:
                _log("VERBOSE", "Aborted by user.", theme, config)
                return
        else:
            # Dry-run: just show the tree, no prompt
            use_pager = config.interactive and total_items > display.console.height
            display.print_tree(tree, pager=use_pager)

    # 7. Execute — Pass 1: fonts (with pre-move canonical grouping applied)
    _log("VERBOSE", f"Found {len(fonts)} font(s), {len(non_fonts)} non-font(s)", theme, config)
    for path in fonts:
        raw_name = raw_family_map.get(path, "")
        canonical = canonical_map.get(raw_name, raw_name) if raw_name else None
        process_font(
            path,
            config.directory,
            config,
            theme,
            canonical_family=canonical,
            original_family=raw_name or None,
        )

    # Pass 2: non-fonts
    for path in non_fonts:
        process_non_font(path, config, theme)

    # Pass 2.5: post-move check — consolidate any dirs still split by prefix
    #           (second check the user requested; operates on directory names)
    if not config.dry_run:
        consolidate_dirs(config.directory, config, theme)

    # Pass 3: empty directories — loop handles cascading cleanup
    if not config.dry_run:
        empties = find_empty_dirs(config.directory)
        while empties:
            for d in empties:
                process_empty_dir(d, config, theme)
            empties = find_empty_dirs(config.directory)
    else:
        for d in pre_empty:
            process_empty_dir(d, config, theme)
