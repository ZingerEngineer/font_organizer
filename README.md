<div align="center">
  <img src="https://res.cloudinary.com/dxdkqsgfm/image/upload/v1773550256/Font_Organizer_Logo_jhgnj6.svg" alt="Font Organizer" width="180" />
  <h1>Font Organizer</h1>
  <p>Organize font collections by family — colorful output, interactive TUI, cross-platform.</p>
</div>

---

Font Organizer recursively scans a directory, extracts family names from font metadata, groups fonts into named subdirectories, renames each file to a canonical `family_variant.ext` format, and sends non-font files and empty directories straight to the recycle bin — safely, never permanently deleting anything.

## Features

- **Smart metadata extraction** — reads the OpenType name table (Typographic Family → Font Family → filename fallback)
- **Canonical family grouping** — two-pass prefix matching groups `"911 Porscha Condensed"` under `"911 Porscha"` automatically
- **Canonical file renaming** — fonts are renamed to `family_variant.ext` (e.g. `open sans_bold italic.ttf`)
- **Title-cased directories** — family directories use title case (e.g. `Open Sans/`)
- **Safe trash** — non-font files and empty directories go to the OS recycle bin, never permanently deleted
- **Duplicate-safe** — appends `-1`, `-2` etc. on filename collisions
- **OMZ-style TUI** — ASCII banner, colored pill tags, icon-per-action log lines (`◆ ⊗ ○ ◇ ✗ ·`)
- **5 color themes** — `default`, `neon`, `pastel`, `mono`, `dracula` — or pick interactively
- **Interactive tree view** — preview proposed layout with an A / V / C menu (Apply / View again / Cancel)
- **Transient progress spinner** — disappears after scan, keeps output clean
- **Dry-run mode** — preview every action without touching the filesystem
- **Cross-platform** — Linux, macOS, Windows

---

## Installation

### Linux / macOS (Bash)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ZingerEngineer/font_organizer/main/install.sh)
```

Or clone and run locally:

```bash
git clone https://github.com/ZingerEngineer/font_organizer.git ~/.font-organizer
bash ~/.font-organizer/install.sh
```

### Windows (PowerShell)

Open PowerShell — run as **Administrator** for a system-wide install:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
Invoke-Expression (Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ZingerEngineer/font_organizer/main/install.ps1" -UseBasicParsing).Content
```

Or clone and run locally:

```powershell
git clone https://github.com/ZingerEngineer/font_organizer.git "$env:USERPROFILE\.font-organizer"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "$env:USERPROFILE\.font-organizer\install.ps1"
```

### Manual (pip)

Requires Python 3.10+:

```bash
git clone https://github.com/ZingerEngineer/font_organizer.git
cd font_organizer
pip install -e .
```

For `sudo` access on Linux/macOS, symlink the binary into a root-owned directory:

```bash
sudo ln -sf $(which font-organizer) /usr/local/bin/font-organizer
```

---

## Requirements

| Dependency  | Version | Purpose |
|-------------|---------|---------|
| Python      | 3.10+   | Runtime |
| fonttools   | ≥ 4.0.0 | OpenType name table extraction |
| send2trash  | ≥ 1.8.0 | Cross-platform recycle bin |
| rich        | ≥ 13.0.0| TUI — colors, tree, progress |
| brotli      | ≥ 1.0.9 | WOFF2 font support |

---

## Usage

```
font-organizer DIRECTORY [options]
```

### Options

| Flag | Description |
|------|-------------|
| `--dry-run` | Preview all actions without modifying the filesystem |
| `--verbose` | Print detailed processing info (family source, variant source) |
| `--theme NAME` | Color theme: `default`, `neon`, `pastel`, `mono`, `dracula`, or `pick` |
| `--no-interactive` | Disable all prompts — safe for piped / scripted use |
| `--no-tree` | Suppress the tree preview of proposed changes |

### Examples

```bash
# Organize a fonts directory (interactive — shows tree + A/V/C menu)
font-organizer ~/Fonts

# Preview without making any changes
font-organizer ~/Fonts --dry-run

# Choose a color theme interactively
font-organizer ~/Fonts --theme pick

# Use the dracula theme with verbose logs
font-organizer ~/Fonts --theme dracula --verbose

# Process system / protected directories
sudo font-organizer /usr/share/fonts          # Linux / macOS
font-organizer C:\Windows\Fonts               # Windows (PowerShell as Administrator)

# Pipe-safe (no prompts, no colors)
font-organizer ~/Fonts --no-interactive --no-tree | tee organize.log
```

---

## Interactive Flow

```
  ███████╗ ██████╗ ███╗   ██╗████████╗███████╗
  ██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔════╝
  ...

╭─── Font Organizer ────────────────────────────────╮
│  Font files found:       42                       │
│  Non-font files found:    7                       │
│  Directory: /home/user/Fonts                      │
╰───────────────────────────────────────────────────╯

Fonts/
├── Open Sans/
│   ├── open sans_regular.ttf
│   └── open sans_bold.ttf
├── Roboto/
│   └── roboto_light.ttf
└── recycle bin
    ├── readme.txt
    └── license.md

  [ A ]  Apply changes   [ V ]  View again   [ C ]  Cancel
  ❯ Choice [a]:
```

After choosing **A**:

```
◆ ❯  FONT     open sans_regular.ttf → Open Sans/
◆ ❯  FONT     open sans_bold.ttf → Open Sans/
◆ ❯  FONT     roboto_light.ttf → Roboto/
⊗ ❯  TRASH    readme.txt → recycle bin
⊗ ❯  TRASH    license.md → recycle bin
```

---

## Output Structure

Input:

```
Fonts/
├── OpenSans-Regular.ttf
├── OpenSans-Bold.ttf
├── 911Porscha-Condensed.otf
├── 911Porscha-CondensedItalic.otf
├── readme.txt
└── OldFolder/
    └── Roboto-Light.ttf
```

Output:

```
Fonts/
├── 911 Porscha/
│   ├── 911 porscha_condensed.otf
│   └── 911 porscha_condensed italic.otf
├── Open Sans/
│   ├── open sans_regular.ttf
│   └── open sans_bold.ttf
└── Roboto/
    └── roboto_light.ttf
```

`readme.txt` and `OldFolder/` are sent to the recycle bin.

---

## Color Themes

| Theme | Style |
|-------|-------|
| `default` | Teal / orange / blue pills — works on any terminal |
| `neon` | Bright green / hot pink — dark terminals |
| `pastel` | Soft 256-color — light terminals |
| `mono` | No color — accessible / screen readers |
| `dracula` | Matches the Dracula color scheme |

Use `--theme pick` for a live swatch picker before organizing.

---

## Supported Font Formats

| Format | Extensions |
|--------|------------|
| TrueType | `.ttf` `.TTF` |
| OpenType | `.otf` `.OTF` |
| WOFF | `.woff` |
| WOFF 2 | `.woff2` |

---

## License

MIT
