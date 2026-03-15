"""Font metadata extraction via fontTools."""

from __future__ import annotations

import re
from pathlib import Path

# Name IDs per OpenType spec
_NAME_ID_FAMILY = 1
_NAME_ID_SUBFAMILY = 2
_NAME_ID_TYPOGRAPHIC_FAMILY = 16
_NAME_ID_TYPOGRAPHIC_SUBFAMILY = 17

# Split "BoldItalic" → "Bold Italic", "ExtraLight" → "Extra Light"
_CAMEL_SPLIT = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")

# Weight/style suffixes to strip when deriving family from filename
_WEIGHT_STYLE_PATTERN = re.compile(
    r"[-_]?"
    r"("
    r"thin|extralight|extra.?light|ultralight|ultra.?light"
    r"|light|regular|medium|semibold|semi.?bold|demibold|demi.?bold"
    r"|bold|extrabold|extra.?bold|ultrabold|ultra.?bold"
    r"|black|heavy"
    r"|italic|oblique|slanted"
    r"|condensed|expanded|narrow|wide"
    r"|roman|normal"
    r")$",
    re.IGNORECASE,
)


def extract_family_name(path: Path) -> str | None:
    """Read the OpenType name table and return the font family name, or None on failure."""
    try:
        from fontTools.ttLib import TTFont  # type: ignore

        font = TTFont(str(path), fontNumber=0)
        name_table = font["name"]

        # Priority: Typographic Family (16) → Font Family (1)
        for name_id in (_NAME_ID_TYPOGRAPHIC_FAMILY, _NAME_ID_FAMILY):
            record = name_table.getBestFamilyName() if name_id == _NAME_ID_FAMILY else None
            if name_id == _NAME_ID_TYPOGRAPHIC_FAMILY:
                record = name_table.getDebugName(name_id)
            if record:
                return record.strip()

        # Fallback to Font Family via getBestFamilyName
        best = name_table.getBestFamilyName()
        if best:
            return best.strip()

        return None
    except Exception:
        return None


def family_name_from_filename(path: Path) -> str:
    """Derive a family name from a font filename by stripping weight/style suffixes."""
    stem = path.stem

    # Split on first hyphen or underscore — take the prefix as family
    for sep in ("-", "_"):
        if sep in stem:
            stem = stem.split(sep)[0]
            break

    # Strip trailing weight/style keywords
    stem = _WEIGHT_STYLE_PATTERN.sub("", stem).strip()

    return stem if stem else path.stem


def extract_variant_name(path: Path) -> str | None:
    """Read the OpenType name table and return the font subfamily/variant, or None."""
    try:
        from fontTools.ttLib import TTFont  # type: ignore

        font = TTFont(str(path), fontNumber=0)
        name_table = font["name"]

        # Priority: Typographic Subfamily (17) → Subfamily (2)
        for name_id in (_NAME_ID_TYPOGRAPHIC_SUBFAMILY, _NAME_ID_SUBFAMILY):
            record = name_table.getDebugName(name_id)
            if record:
                return record.strip()
        return None
    except Exception:
        return None


def variant_from_filename(path: Path) -> str:
    """Derive a variant/subfamily name from a font filename.

    Splits on the first separator and takes the remaining parts.
    CamelCase parts are split into words: "BoldItalic" → "Bold Italic".
    Returns "Regular" if no variant can be found.
    """
    stem = path.stem
    parts: list[str] = []

    for sep in ("-", "_"):
        if sep in stem:
            parts = stem.split(sep)[1:]
            break

    if not parts:
        return "Regular"

    # CamelCase-split each part and flatten
    words: list[str] = []
    for part in parts:
        words.extend(_CAMEL_SPLIT.split(part))

    return " ".join(w for w in words if w)


def get_variant_name(path: Path, family_name: str) -> tuple[str, str]:
    """Return (variant_name, source) where source is 'metadata' | 'filename'.

    Never raises. Falls back to filename heuristic if metadata is unavailable.
    """
    name = extract_variant_name(path)
    if name:
        return name, "metadata"
    return variant_from_filename(path), "filename"


def get_family_name(path: Path) -> tuple[str, str]:
    """Return (family_name, source) where source is 'metadata' | 'filename'.

    Never raises — corrupt or exotic fonts degrade gracefully to filename fallback.
    """
    name = extract_family_name(path)
    if name:
        return name, "metadata"

    return family_name_from_filename(path), "filename"
