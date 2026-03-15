# Usage Guide

## Installation

### Option A — pipx (recommended for CLI tools)

Installs in an isolated environment and registers `font-organizer` globally:

```bash
pip install pipx
pipx install .
```

### Option B — pip editable install (for development)

```bash
pip install -e .
```

### Option C — run directly without installing

```bash
pip install -r requirements.txt
python font_organizer.py DIRECTORY
```

After installing via pipx or pip, the command is available globally:

```bash
font-organizer ~/Downloads/fonts
```

---

## Basic Syntax

```
font-organizer DIRECTORY [--dry-run] [--verbose]
```

---

## Arguments

### `DIRECTORY` (required)

The path to the folder containing fonts to organize. Scanned recursively — all subdirectories are included.

```bash
font-organizer ~/Downloads/fonts
font-organizer /mnt/storage/MyFonts
font-organizer .                      # current directory
```

---

## Flags

### `--dry-run`

Preview all actions without touching the filesystem. No files are moved or deleted.

```bash
font-organizer ~/Downloads/fonts --dry-run
```

Output:
```
[DRY] Would move OpenSans-Bold.ttf → Open Sans/
[DRY] Would move Roboto-Light.ttf → Roboto/
[DRY] Would trash readme.txt
```

Use this before a real run to verify the script will do what you expect.

---

### `--verbose`

Print detailed per-file information: the family name, where it came from (font metadata or filename heuristic), and every decision made.

```bash
font-organizer ~/Downloads/fonts --verbose
```

Output:
```
[VERBOSE] Scanning: /home/user/Downloads/fonts
[VERBOSE] Found 42 font(s), 3 non-font(s)
[VERBOSE] Family 'Open Sans' (source: metadata) — OpenSans-Bold.ttf
[FONT] OpenSans-Bold.ttf → Open Sans/
[VERBOSE] Family 'Roboto' (source: filename) — Roboto-Light.ttf
[FONT] Roboto-Light.ttf → Roboto/
[TRASH] readme.txt → recycle bin
```

---

## Combining Flags

Flags can be combined freely:

```bash
# Verbose dry run — maximum detail, zero risk
font-organizer ~/Downloads/fonts --dry-run --verbose

# Live run with verbose output
font-organizer ~/Downloads/fonts --verbose
```

---

## Processing sudo-protected files

Some directories (e.g. system font folders) are owned by root and require elevated permissions.

If the script hits a permission error it will tell you:

```
[ERROR] Permission denied: Arial.ttf — try: sudo font-organizer /usr/share/fonts
```

Run the command with `sudo` to process those files:

```bash
sudo font-organizer /usr/share/fonts
sudo font-organizer /usr/share/fonts --dry-run   # preview first
```

**Note:** When running as root, non-font files are sent to root's trash
(`/root/.local/share/Trash` on Linux). They are still recoverable.

---

## Log Tags

| Tag | Meaning |
|-----|---------|
| `[FONT]` | Font moved to its family directory |
| `[SKIP]` | Font already in the correct directory — no action taken |
| `[TRASH]` | Non-font file sent to recycle bin |
| `[DRY]` | Action that would happen — dry-run mode only |
| `[VERBOSE]` | Detailed diagnostic info — verbose mode only |
| `[ERROR]` | Something went wrong; file skipped |

---

## Output Structure

Given this input:

```
Downloads/fonts/
├── OpenSans-Regular.ttf
├── OpenSans-Bold.ttf
├── Roboto-Light.ttf
├── readme.txt
└── subfolder/
    └── Lato-Italic.ttf
```

Running:

```bash
font-organizer ~/Downloads/fonts
```

Produces:

```
Downloads/fonts/
├── Open Sans/
│   ├── OpenSans-Regular.ttf
│   └── OpenSans-Bold.ttf
├── Roboto/
│   └── Roboto-Light.ttf
└── Lato/
    └── Lato-Italic.ttf
# readme.txt → moved to OS trash
```

---

## Edge Cases

### Duplicate filenames

If two fonts with the same filename belong to the same family, the second file is renamed automatically:

```
Roboto-Regular.ttf       → Roboto/Roboto-Regular.ttf
Roboto-Regular(1).ttf    → Roboto/Roboto-Regular-1.ttf
```

### Missing metadata

If a font has no readable name table, the family name is derived from the filename:

```
MyFont-Bold.ttf  →  family: MyFont
```

### Corrupt fonts

If a font file cannot be parsed at all, it is skipped:

```
[ERROR] Unable to determine family name: broken.ttf
```

### WOFF2 support

WOFF2 metadata extraction requires the `brotli` package. Without it, WOFF2 files fall back to filename-based detection. Install with:

```bash
pip install brotli
```

---

## Safety

- Files are **never permanently deleted** — non-fonts go to the OS recycle bin
- Existing files are **never overwritten** — duplicates get a numeric suffix
- Use `--dry-run` to preview any run before committing
