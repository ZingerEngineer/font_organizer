# Plan: Font Organizer — Initial Script Implementation

## Context

The project has documentation (README.md, CLAUDE.md) but no implementation yet. The user wants the full Font Organizer script created with two additional constraints: modular coding (no file > 500 lines), and all markdown docs go in a `docs/` directory. CLAUDE.md must be updated to reflect both rules.

---

## Step 0 — Update CLAUDE.md

Add to `.claude/CLAUDE.md`:

```markdown
# Code Style Rules
- Modular coding: no single file may exceed 500 lines of code
- All markdown documentation, plans, and explanations created within this project go inside the `docs/` directory at the project root
```

---

## Module Structure

```
fonts_organizer/
├── font_organizer.py     # Entry point — CLI wiring only (~40 lines)
├── cli.py                # Argument parsing + Config dataclass (~60 lines)
├── scanner.py            # File discovery and classification (~80 lines)
├── metadata.py           # Font metadata extraction via fontTools (~120 lines)
├── filesystem.py         # Safe file operations (move, trash, dedup) (~130 lines)
└── organizer.py          # Orchestration — wires all modules together (~180 lines)
```

All well under 500 lines per file.

---

## Dependency Graph (no circular imports)

```
font_organizer → cli, organizer
organizer      → scanner, metadata, filesystem, cli
filesystem     → send2trash, shutil, pathlib
metadata       → fontTools, pathlib
scanner        → pathlib
cli            → argparse, pathlib, dataclasses
```

---

## Module Details

### `cli.py`
- `Config` frozen dataclass: `directory: Path`, `dry_run: bool`, `verbose: bool`
- `parse_args(argv=None) -> Config` — validates directory exists before returning

### `scanner.py`
- `FONT_EXTENSIONS: frozenset[str]` = `{".ttf", ".otf", ".woff", ".woff2"}`
- `is_font_file(path: Path) -> bool` — checks `path.suffix.lower()`
- `scan_directory(directory: Path) -> Iterator[Path]` — `rglob("*")`, files only
- `partition_files(directory: Path) -> tuple[list[Path], list[Path]]` — returns `(fonts, non_fonts)`

### `metadata.py`
- `extract_family_name(path: Path) -> str | None` — reads TTFont name table (ID 16 → ID 1), wrapped in broad `except Exception`
- `family_name_from_filename(path: Path) -> str` — strips weight/style suffixes via regex, splits on `-`/`_`
- `get_family_name(path: Path) -> tuple[str, str]` — public interface; returns `(name, source)` where source is `"metadata" | "filename" | "error"`. Never raises.

### `filesystem.py`
- `resolve_destination(source: Path, target_dir: Path) -> Path` — pure function, appends `-1`, `-2`, etc. to stem if target exists
- `ensure_directory(path: Path, dry_run: bool) -> None` — `path.mkdir(parents=True, exist_ok=True)`
- `move_font(source: Path, family_dir: Path, dry_run: bool) -> Path` — calls ensure_directory → resolve_destination → `shutil.move`; returns final destination
- `trash_file(path: Path, dry_run: bool) -> None` — wraps `send2trash.send2trash(str(path))`, catches `TrashPermissionError`

### `organizer.py`
- `log(tag: str, message: str, config: Config) -> None` — formats `[TAG] message`, suppresses VERBOSE when `config.verbose=False`
- `is_already_organized(path: Path, family_name: str) -> bool` — `path.parent.name == family_name`
- `process_font(path: Path, root_dir: Path, config: Config) -> None` — full font pipeline: extract name → check if organized → move → log
- `process_non_font(path: Path, config: Config) -> None` — trash → log
- `run(config: Config) -> None` — calls `partition_files`, then `process_font` for all fonts, then `process_non_font` for all non-fonts

### `font_organizer.py`
```python
from cli import parse_args
from organizer import run

def main():
    config = parse_args()
    run(config)

if __name__ == "__main__":
    main()
```

---

## Key Design Decisions

- **No classes** — state flows through the `Config` frozen dataclass; all functions are stateless
- **`dry_run` as explicit parameter** — every mutating function takes it; no global state
- **`shutil.move` over `Path.rename`** — handles cross-device moves correctly on all platforms
- **`get_family_name` never raises** — corrupt/exotic fonts degrade gracefully to filename fallback
- **Two-pass iteration** — fonts processed first, then non-fonts trashed; avoids edge case where a font and a non-font coexist in the same subdir

---

## Log Format

| Situation | Output |
|-----------|--------|
| Font moved | `[FONT] OpenSans-Bold.ttf → Open Sans/` |
| Font dry-run | `[DRY] Would move OpenSans-Bold.ttf → Open Sans/` |
| Trashed | `[TRASH] readme.txt → recycle bin` |
| Trash dry-run | `[DRY] Would trash readme.txt` |
| Already organized | `[SKIP] OpenSans-Bold.ttf — already in Open Sans/` |
| Error | `[ERROR] Unable to read metadata: font.ttf` |
| Verbose detail | `[VERBOSE] Family source: filename heuristic` |

---

## Implementation Order

1. `cli.py` — defines `Config`, no external deps
2. `scanner.py` — pure pathlib, no external deps
3. `metadata.py` — fontTools integration (highest risk)
4. `filesystem.py` — all mutations, dry-run safety
5. `organizer.py` — wires everything together
6. `font_organizer.py` — entry point, ~10 lines

---

## Files Created/Modified

| Action | Path |
|--------|------|
| Modified | `.claude/CLAUDE.md` — added modular coding + docs/ rules |
| Created | `font_organizer.py` |
| Created | `cli.py` |
| Created | `scanner.py` |
| Created | `metadata.py` |
| Created | `filesystem.py` |
| Created | `organizer.py` |
| Created | `docs/plans/implementation-plan.md` (this file) |
