"""Font metadata extraction via fontTools."""

from __future__ import annotations

import re
from pathlib import Path

# Name IDs per OpenType spec
_NAME_ID_FAMILY = 1
_NAME_ID_TYPOGRAPHIC_FAMILY = 16

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


def get_family_name(path: Path) -> tuple[str, str]:
    """Return (family_name, source) where source is 'metadata' | 'filename'.

    Never raises — corrupt or exotic fonts degrade gracefully to filename fallback.
    """
    name = extract_family_name(path)
    if name:
        return name, "metadata"

    return family_name_from_filename(path), "filename"
