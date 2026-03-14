# Font Organizer

## Purpose

This project contains a Python script that organizes font files by **font family name**.

The script recursively scans a directory, extracts font metadata, groups fonts belonging to the same family, and moves non-font files to the system recycle bin.

The goal is to transform messy font collections into a clean deterministic structure.

Example input:

```
Fonts/
├── OpenSans-Regular.ttf
├── OpenSans-Bold.ttf
├── OpenSans-Italic.ttf
├── Roboto-Light.ttf
├── readme.txt
└── license.md
```

Example output:

```
Fonts/
├── Open Sans/
│   ├── OpenSans-Regular.ttf
│   ├── OpenSans-Bold.ttf
│   └── OpenSans-Italic.ttf
├── Roboto/
│   └── Roboto-Light.ttf
└── .trash/
    ├── readme.txt
    └── license.md
```

---

# Implementation Requirements

## Language

Python **3.10+**

The script must run on:

* Linux
* macOS
* Windows

Avoid platform-specific shell commands.
Use Python libraries instead.

---

# Required Dependencies

Preferred libraries:

| Library    | Purpose                         |
| ---------- | ------------------------------- |
| fontTools  | Extract font metadata           |
| send2trash | Move files to OS recycle bin    |
| pathlib    | Cross-platform filesystem paths |

Install:

```
pip install fonttools send2trash
```

---

# Supported Font Formats

The script must detect these extensions **case-insensitively**:

| Format                 | Extensions |
| ---------------------- | ---------- |
| OpenType               | `.otf`     |
| TrueType               | `.ttf`     |
| Web Open Font Format   | `.woff`    |
| Web Open Font Format 2 | `.woff2`   |

Extension matching must be case-insensitive.

Examples:

```
.ttf
.TTF
.otf
.OTF
```

---

# Recursive File Discovery

Font files must be discovered by scanning the filesystem.

The script **must not rely on system installed fonts**.

Use recursive traversal.

Example concept:

```
Path(directory).rglob("*")
```

All discovered files must be classified as:

* Font
* Non-font

---

# Font Metadata Extraction

Font family name must be extracted from **font metadata**, not filenames.

Preferred method:

```
from fontTools.ttLib import TTFont
```

Extract the **name table** entries for:

* Typographic Family
* Font Family
* Preferred Family

Fallback priority:

1. Typographic Family
2. Font Family
3. Filename heuristic

---

# Directory Organization

Fonts must be grouped into directories using the **family name**.

Example input:

```
OpenSans-Regular.ttf
OpenSans-Bold.ttf
OpenSans-Italic.ttf
```

Expected structure:

```
Open Sans/
 ├── OpenSans-Regular.ttf
 ├── OpenSans-Bold.ttf
 └── OpenSans-Italic.ttf
```

Rules:

* Create directory if it does not exist
* Directory name must equal the family name
* Move fonts into that directory

---

# Verbose Logging

The script must output clear logs describing actions.

Examples:

```
[FONT] OpenSans-Bold.ttf → Open Sans/
[FONT] Roboto-Light.ttf → Roboto/
[TRASH] readme.txt → recycle bin
```

Logging should include:

* file path
* detected type
* extracted family name
* destination directory

---

# Non-Font File Handling

Any file not matching the supported extensions must be moved to the recycle bin.

Use:

```
send2trash(path)
```

Behavior across platforms:

| OS      | Destination              |
| ------- | ------------------------ |
| Windows | Recycle Bin              |
| macOS   | Trash                    |
| Linux   | Trash (freedesktop spec) |

---

# Script Execution Modes

## Default Mode

```
python font_organizer.py DIRECTORY
```

Behavior:

* recursively scans directory
* groups fonts
* moves non-font files to recycle bin
* prints logs

---

## Dry Run Mode

```
python font_organizer.py DIRECTORY --dry-run
```

Behavior:

* prints actions
* **does not modify filesystem**

Example:

```
[DRY] Would move Roboto-Bold.ttf → Roboto/
[DRY] Would trash readme.txt
```

---

## Verbose Mode

```
python font_organizer.py DIRECTORY --verbose
```

Provides detailed processing logs.

---

# Edge Cases

## Duplicate Files

Example:

```
Roboto-Regular.ttf
Roboto-Regular(1).ttf
```

Behavior:

* avoid overwriting
* append suffix

Example result:

```
Roboto-Regular-1.ttf
```

---

## Missing Metadata

Some fonts may not contain valid metadata.

Fallback behavior:

* derive family name from filename

Example:

```
MyFont-Bold.ttf
```

Family becomes:

```
MyFont
```

---

## Corrupt Fonts

If metadata parsing fails:

```
[ERROR] Unable to read metadata: font.ttf
```

Handling options:

* skip file
* optionally move to recycle bin

---

## Already Organized Fonts

If a font already resides in the correct family directory:

```
[SKIP] Already organized
```

---

## Nested Font Directories

Example:

```
Fonts/OpenSans/OpenSans-Bold.ttf
```

Behavior:

* detect existing organization
* avoid creating duplicate directories

---

# Safety Requirements

The script must:

* never permanently delete files
* always use the recycle bin
* support dry-run mode
* avoid overwriting existing files
* operate safely on large directories

---

# Performance Considerations

Large font libraries may contain **thousands of files**.

Optimizations:

* process files iteratively
* avoid loading entire directory trees into memory
* minimize repeated metadata extraction
* fail fast on corrupted files

---

# Test Scenarios

The script must work correctly with:

### Case 1

Flat directory of fonts.

### Case 2

Deep nested directory tree.

### Case 3

Mixed file types (fonts + documents + images).

### Case 4

Duplicate filenames.

### Case 5

Fonts missing metadata.

### Case 6

Already organized font directories.

---

# Expected Final Structure

Example result:

```
Fonts/
├── Open Sans/
│   ├── OpenSans-Regular.ttf
│   ├── OpenSans-Bold.ttf
│   └── OpenSans-Italic.ttf
├── Roboto/
│   ├── Roboto-Light.ttf
│   └── Roboto-Bold.ttf
```

---

# Non Goals

The script should **not**:

* convert font formats
* modify font metadata
* download fonts
* validate font licensing
