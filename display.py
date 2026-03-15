"""All Rich-based rendering: tree, log lines, progress, panels, picker, confirmation."""

from __future__ import annotations

import os
import sys
from collections import defaultdict
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.tree import Tree

from themes import ThemeSpec, THEMES, THEME_NAMES, theme_preview_text


# ---------------------------------------------------------------------------
# Console singleton
# ---------------------------------------------------------------------------

def make_console(force_terminal: bool = False) -> Console:
    """Return a Console with highlight=False to suppress auto-highlighting of paths."""
    return Console(highlight=False, force_terminal=force_terminal)


console: Console = make_console()


# ---------------------------------------------------------------------------
# TTY detection
# ---------------------------------------------------------------------------

def is_interactive() -> bool:
    """Return True when stdout is a real TTY and color-disabling env vars are absent."""
    if not sys.stdout.isatty():
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    if "NO_COLOR" in os.environ:
        return False
    return True


# ---------------------------------------------------------------------------
# Log line rendering
# ---------------------------------------------------------------------------

_TAG_STYLE_MAP: dict[str, str] = {
    "FONT":    "tag_font",
    "TRASH":   "tag_trash",
    "SKIP":    "tag_skip",
    "DRY":     "tag_dry",
    "ERROR":   "tag_error",
    "VERBOSE": "tag_verbose",
}


def render_log_line(tag: str, message: str, theme: ThemeSpec) -> None:
    """Print one styled log line with a background-colored pill tag.

    Format: [ TAG     ] message
    The tag is padded to a fixed width and wrapped in background-color markup.
    Unknown tags fall back to tag_verbose style.
    """
    attr = _TAG_STYLE_MAP.get(tag, "tag_verbose")
    style = getattr(theme, attr, "")
    # Pill: space + tag padded to 7 chars + space (9 chars total)
    pill_text = f" {tag:<7} "
    if style:
        tag_str = f"[{style}]{pill_text}[/]"
    else:
        tag_str = pill_text
    console.print(f"{tag_str} {message}")


# ---------------------------------------------------------------------------
# Progress spinner
# ---------------------------------------------------------------------------

@contextmanager
def scan_progress(label: str, theme: ThemeSpec) -> Generator[Progress, None, None]:
    """Yield a transient Rich Progress instance for scanning operations.

    The spinner and bar disappear after the context exits (transient=True).
    """
    progress = Progress(
        SpinnerColumn(theme.spinner),
        TextColumn(f"[{theme.progress_bar}]{label}[/]"),
        BarColumn(bar_width=None, style=theme.progress_bar),
        TaskProgressColumn(),
        transient=True,
        console=console,
    )
    with progress:
        yield progress


# ---------------------------------------------------------------------------
# Tree preview
# ---------------------------------------------------------------------------

def build_proposal_tree(
    root_dir: Path,
    moves: list[tuple[Path, str, str]],
    trashes: list[Path],
    theme: ThemeSpec,
    empty_dirs: list[Path] | None = None,
) -> Tree:
    """Build a Rich Tree showing the proposed directory layout.

    Args:
        root_dir:   The target root directory.
        moves:      List of (source_path, dir_name, new_filename) triples.
        trashes:    List of non-font file paths to be sent to the recycle bin.
        theme:      Active ThemeSpec for styling.
        empty_dirs: Pre-existing empty directories that will be trashed.

    Returns a Tree ready to print. Does not touch the filesystem.
    """
    root_style = theme.tree_root if theme.tree_root else "bold"
    root_label = f"[{root_style}]{root_dir.name}/[/]" if root_style else f"{root_dir.name}/"
    tree = Tree(root_label)

    # Group by (normalized) family dir name
    # Value: list of (source, new_filename, already_organized)
    by_family: dict[str, list[tuple[Path, str, bool]]] = defaultdict(list)

    for source, dir_name, new_filename in moves:
        already = source.parent.name == dir_name and source.name == new_filename
        by_family[dir_name].append((source, new_filename, already))

    for dir_name in sorted(by_family.keys()):
        family_style = theme.tree_family if theme.tree_family else "bold"
        family_label = (
            f"[{family_style}]{dir_name}/[/]"
            if family_style
            else f"{dir_name}/"
        )
        branch = tree.add(family_label)

        entries = sorted(by_family[dir_name], key=lambda x: x[1])
        for source, new_filename, already in entries:
            file_style = theme.tree_skipped if already else (theme.tree_file if theme.tree_file else "")
            prefix = "[SKIP] " if already else ""
            label = f"{prefix}{new_filename}"
            if file_style:
                branch.add(f"[{file_style}]{label}[/]")
            else:
                branch.add(label)

    # Trash section — non-font files + pre-existing empty dirs
    has_trash = trashes or empty_dirs
    if has_trash:
        trash_style = theme.tree_trash if theme.tree_trash else "italic"
        trash_label = (
            f"[{trash_style}]recycle bin[/]"
            if trash_style
            else "recycle bin"
        )
        trash_branch = tree.add(trash_label)

        for path in sorted(trashes, key=lambda p: p.name):
            if trash_style:
                trash_branch.add(f"[{trash_style}]{path.name}[/]")
            else:
                trash_branch.add(path.name)

        for d in sorted(empty_dirs or [], key=lambda p: p.name):
            label = f"{d.name}/  [dim](empty dir)[/dim]"
            if trash_style:
                trash_branch.add(f"[{trash_style}]{label}")
            else:
                trash_branch.add(label)

    return tree


def print_tree(tree: Tree, pager: bool = False) -> None:
    """Render a Rich Tree to the console, optionally inside a scrollable pager."""
    if pager:
        with console.pager(styles=True):
            console.print(tree)
    else:
        console.print(tree)


# ---------------------------------------------------------------------------
# Panels
# ---------------------------------------------------------------------------

def print_summary_panel(
    fonts_count: int,
    non_fonts_count: int,
    root_dir: Path,
    theme: ThemeSpec,
) -> None:
    """Print a summary panel showing scan results."""
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="right", style="dim")
    table.add_column()
    table.add_row("Font files found:", str(fonts_count))
    table.add_row("Non-font files found:", str(non_fonts_count))
    table.add_row("Directory:", str(root_dir))

    console.print(
        Panel(table, title="Font Organizer", border_style=theme.panel_border)
    )


def print_panel(content: str, title: str, theme: ThemeSpec) -> None:
    """Print a generic Rich Panel."""
    console.print(Panel(content, title=title, border_style=theme.panel_border))


# ---------------------------------------------------------------------------
# Interactive confirmation
# ---------------------------------------------------------------------------

def confirm_proceed(theme: ThemeSpec) -> bool:
    """Ask the user whether to apply changes. Returns True if confirmed."""
    console.print()
    return Confirm.ask(
        f"[{theme.panel_border}]Apply these changes?[/]",
        default=False,
        console=console,
    )


# ---------------------------------------------------------------------------
# Theme picker
# ---------------------------------------------------------------------------

def run_theme_picker(current: str) -> str:
    """Display an interactive theme selection menu and return the chosen theme name.

    Falls back to `current` if not interactive (should be guarded by caller).
    """
    lines: list[str] = []
    for i, name in enumerate(THEME_NAMES, start=1):
        spec = THEMES[name]
        swatch = theme_preview_text(name, spec)
        lines.append(f"  [{i}]  {swatch}")

    body = "\n".join(lines)
    console.print(
        Panel(body, title="Choose a theme", border_style=THEMES["default"].panel_border)
    )

    choices = [str(i) for i in range(1, len(THEME_NAMES) + 1)]
    choice = Prompt.ask(
        "Enter number",
        choices=choices,
        default="1",
        console=console,
    )

    chosen_name = THEME_NAMES[int(choice) - 1]
    return chosen_name
