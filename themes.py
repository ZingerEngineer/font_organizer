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
        # Tags: background pill style (foreground on background)
        tag_font="bold white on dark_cyan",
        tag_trash="bold black on gold1",
        tag_skip="white on grey46",
        tag_dry="bold white on dodger_blue3",
        tag_error="bold white on red3",
        tag_verbose="white on grey30",
        # Tree
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
        tag_font="bold black on bright_green",
        tag_trash="bold black on bright_magenta",
        tag_skip="bold white on grey27",
        tag_dry="bold black on bright_cyan",
        tag_error="bold white on bright_red",
        tag_verbose="white on grey19",
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
        tag_font="bold white on color(65)",
        tag_trash="bold white on color(130)",
        tag_skip="white on color(239)",
        tag_dry="bold white on color(67)",
        tag_error="bold white on color(131)",
        tag_verbose="white on color(235)",
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
        tag_font="bold reverse",
        tag_trash="bold reverse",
        tag_skip="dim reverse",
        tag_dry="bold underline",
        tag_error="bold reverse",
        tag_verbose="dim reverse",
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
        tag_font="bold black on color(84)",
        tag_trash="bold black on color(212)",
        tag_skip="white on color(240)",
        tag_dry="bold black on color(141)",
        tag_error="bold white on color(203)",
        tag_verbose="dim white on color(238)",
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
    """Return a rich markup string showing the theme name with pill-style tag swatches."""
    pills = [
        f"[{spec.tag_font}] FONT [/]",
        f"[{spec.tag_trash}] TRASH [/]",
        f"[{spec.tag_error}] ERROR [/]",
        f"[{spec.tag_skip}] SKIP [/]",
    ]
    name_part = f"[{spec.tree_family}]{name:<10}[/]"
    return name_part + "  " + " ".join(pills)
