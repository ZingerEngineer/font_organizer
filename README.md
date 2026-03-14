# Font Organizer

A Python script that organizes font files by font family name. It recursively scans a directory, extracts font metadata, groups fonts into family subdirectories, and moves non-font files to the system recycle bin.

## Features

- Detects font files by extension (`.ttf`, `.otf`, `.woff`, `.woff2`) — case-insensitive
- Extracts family names from font metadata using `fontTools`
- Falls back to filename heuristics when metadata is missing
- Moves non-font files to the OS recycle bin (never permanently deletes)
- Handles duplicates safely by appending a suffix
- Supports dry-run mode to preview changes without touching the filesystem

## Requirements

- Python 3.10+

## Installation

```bash
pip install fonttools send2trash
```

## Usage

### Default

Scan and organize fonts in a directory:

```bash
python font_organizer.py DIRECTORY
```

### Dry Run

Preview what would happen without making any changes:

```bash
python font_organizer.py DIRECTORY --dry-run
```

### Verbose

Print detailed logs during processing:

```bash
python font_organizer.py DIRECTORY --verbose
```

## Example

Input:

```
Fonts/
├── OpenSans-Regular.ttf
├── OpenSans-Bold.ttf
├── Roboto-Light.ttf
└── readme.txt
```

Output:

```
Fonts/
├── Open Sans/
│   ├── OpenSans-Regular.ttf
│   └── OpenSans-Bold.ttf
├── Roboto/
│   └── Roboto-Light.ttf
└── .trash/
    └── readme.txt
```

## Supported Formats

| Format  | Extensions       |
|---------|-----------------|
| TrueType | `.ttf`, `.TTF` |
| OpenType | `.otf`, `.OTF` |
| WOFF     | `.woff`        |
| WOFF2    | `.woff2`       |
