# Plan: Interactive TUI and Visual Output for Font Organizer

## Context

The script previously output plain `[TAG] message` lines with no color, no tree structure, and no interactivity. This change adds: styled/colored output via `rich`, a tree view of the proposed directory layout before executing, five built-in color themes, an interactive theme picker, a scan progress spinner, and a confirmation gate before applying changes.

---

## New Modules

### `themes.py`

Pure data module. Defines `ThemeSpec` (frozen dataclass) and 5 built-in themes:

| Name | Character |
|------|-----------|
| `default` | Neutral cyan/yellow, any terminal |
| `neon` | Bright green/magenta, dark terminals |
| `pastel` | Soft 256-color, light terminals |
| `mono` | No color, accessible |
| `dracula` | Matches Dracula color scheme |

Public API: `get_theme(name)`, `theme_preview_text(name, spec)`, `THEME_NAMES`, `THEMES`.

### `display.py`

All Rich rendering. Module-level `console` singleton. Functions:

- `is_interactive()` — TTY + NO_COLOR check
- `render_log_line(tag, message, theme)` — styled tag + message
- `scan_progress(label, theme)` — transient spinner context manager
- `build_proposal_tree(root_dir, moves, trashes, theme) -> Tree`
- `print_tree(tree)`
- `print_summary_panel(fonts_count, non_fonts_count, root_dir, theme)`
- `confirm_proceed(theme) -> bool`
- `run_theme_picker(current) -> str`

---

## Modified Files

### `cli.py`

Three new `Config` fields: `theme: str`, `interactive: bool`, `no_tree: bool`.
Three new flags: `--theme NAME`, `--no-interactive`, `--no-tree`.
`interactive` computed as `not --no-interactive AND is_interactive()`.

### `organizer.py`

- `log()` replaced by `_log(tag, message, theme, config)` shim
- `_compute_moves(fonts)` added for tree preview (pure, no I/O)
- `run()` restructured: theme resolution → scan spinner → summary panel → tree preview → confirm → execute
- `process_font()` and `process_non_font()` gain `theme: ThemeSpec` parameter

### `pyproject.toml` / `requirements.txt`

Added `rich>=13.0.0`. Registered `themes` and `display` in `py-modules`.

---

## Usage

```bash
font-organizer /path/to/fonts                          # default theme, interactive
font-organizer /path/to/fonts --theme pick             # interactive theme picker
font-organizer /path/to/fonts --theme neon --dry-run   # neon theme, preview only
font-organizer /path/to/fonts --no-interactive --no-tree  # scripting mode
```
