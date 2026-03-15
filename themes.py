"""Color theme definitions for Font Organizer.

Pure data module — no Rich objects are instantiated here.
All values are Rich markup style strings consumed by display.py.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeSpec:
    # Log tag styles
    tag_font: str
    tag_trash: str
    tag_skip: str
    tag_dry: str
    tag_error: str
    tag_verbose: str
    # Tree node styles
    tree_root: str
    tree_family: str
    tree_file: str
    tree_trash: str
    tree_skipped: str
    # UI chrome
    panel_border: str
    progress_bar: str
    spinner: str


THEMES: dict[str, ThemeSpec] = {
    "default": ThemeSpec(
        tag_font="bold cyan",
        tag_trash="bold yellow",
        tag_skip="dim white",
        tag_dry="bold blue",
        tag_error="bold red",
        tag_verbose="dim cyan",
        tree_root="bold white",
        tree_family="bold cyan",
        tree_file="white",
        tree_trash="yellow",
        tree_skipped="dim white",
        panel_border="cyan",
        progress_bar="cyan",
        spinner="dots",
    ),
    "neon": ThemeSpec(
        tag_font="bold bright_green",
        tag_trash="bold bright_magenta",
        tag_skip="dim green",
        tag_dry="bold bright_cyan",
        tag_error="bold bright_red",
        tag_verbose="dim bright_green",
        tree_root="bold bright_white",
        tree_family="bold bright_green",
        tree_file="bright_green",
        tree_trash="bright_magenta",
        tree_skipped="dim bright_green",
        panel_border="bright_green",
        progress_bar="bright_green",
        spinner="aesthetic",
    ),
    "pastel": ThemeSpec(
        tag_font="bold color(114)",
        tag_trash="bold color(222)",
        tag_skip="dim color(252)",
        tag_dry="bold color(111)",
        tag_error="bold color(210)",
        tag_verbose="dim color(151)",
        tree_root="bold color(255)",
        tree_family="color(183)",
        tree_file="color(252)",
        tree_trash="color(222)",
        tree_skipped="dim color(252)",
        panel_border="color(183)",
        progress_bar="color(114)",
        spinner="point",
    ),
    "mono": ThemeSpec(
        tag_font="bold",
        tag_trash="bold",
        tag_skip="dim",
        tag_dry="bold",
        tag_error="bold reverse",
        tag_verbose="dim",
        tree_root="bold",
        tree_family="bold",
        tree_file="",
        tree_trash="italic",
        tree_skipped="dim",
        panel_border="white",
        progress_bar="white",
        spinner="line",
    ),
    "dracula": ThemeSpec(
        tag_font="bold color(84)",
        tag_trash="bold color(212)",
        tag_skip="dim color(61)",
        tag_dry="bold color(141)",
        tag_error="bold color(203)",
        tag_verbose="dim color(117)",
        tree_root="bold color(255)",
        tree_family="bold color(141)",
        tree_file="color(255)",
        tree_trash="color(212)",
        tree_skipped="dim color(61)",
        panel_border="color(141)",
        progress_bar="color(84)",
        spinner="dots2",
    ),
}

THEME_NAMES: tuple[str, ...] = tuple(THEMES.keys())


def get_theme(name: str) -> ThemeSpec:
    """Return ThemeSpec by name. Raises ValueError with list of valid names if unknown."""
    if name not in THEMES:
        raise ValueError(
            f"Unknown theme '{name}'. Valid choices: {', '.join(THEME_NAMES)}"
        )
    return THEMES[name]


def theme_preview_text(name: str, spec: ThemeSpec) -> str:
    """Return a rich markup string showing the theme name styled in its own colors.

    Example (for 'neon'):
        [bold bright_green]neon[/]  [bold bright_green]Family[/]  [bright_green]file.ttf[/]  [bright_magenta]trash[/]  [bold bright_red]error[/]
    """
    parts = [
        f"[{spec.tree_family}]{name:<10}[/]",
        f"[{spec.tree_family}]Family[/]",
        f"[{spec.tree_file}]file.ttf[/]",
        f"[{spec.tree_trash}]trash[/]",
        f"[{spec.tag_error}]error[/]",
    ]
    return "  ".join(parts)
