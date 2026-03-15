"""Font family grouping via substring/prefix matching.

Solves the problem where a font collection stores variants as separate
family names in metadata:
    "911 Porscha"
    "911 Porscha Condensed"
    "911 Porscha Condensed Italic"
    "911 Porscha Italic"

All of these share the prefix "911 Porscha" and should be organized into
a single family directory.

Two passes are supported:
  1. Pre-move:  build_canonical_map() over all extracted family names.
  2. Post-move: build_canonical_map() over all directory names after the
                first organization pass (catches any that slipped through).
"""

from __future__ import annotations


def is_prefix_match(prefix: str, full: str) -> bool:
    """Return True when prefix is a word-boundary prefix of full (case-insensitive).

    "911 Porscha" matches "911 Porscha Condensed"  → True
    "Arial"       matches "Arial Black"            → True
    "Aria"        matches "Arial"                  → False  (not a full word boundary)
    """
    p = prefix.strip().lower()
    f = full.strip().lower()
    if p == f:
        return False  # Identical names are not "prefixes" of each other
    if not f.startswith(p):
        return False
    remainder = f[len(p):]
    return remainder.startswith(" ")  # Word boundary: next char must be a space


def build_canonical_map(names: set[str]) -> dict[str, str]:
    """Map every name to its shortest prefix-matching canonical name.

    Names sorted by length (shortest first). A name becomes canonical if
    no shorter name is a word-boundary prefix of it. Longer names that
    have a prefix match are remapped to the shortest matching prefix.

    Example:
        {"911 Porscha", "911 Porscha Condensed", "911 Porscha Condensed Italic"}
        →
        {
            "911 Porscha":                "911 Porscha",
            "911 Porscha Condensed":      "911 Porscha",
            "911 Porscha Condensed Italic":"911 Porscha",
        }
    """
    sorted_names = sorted(names, key=lambda n: (len(n), n.lower()))
    canonical: dict[str, str] = {}

    for name in sorted_names:
        best = name
        for candidate in sorted_names:
            if candidate == name:
                break  # Only compare against shorter names (already processed)
            resolved = canonical.get(candidate, candidate)
            if is_prefix_match(resolved, name):
                best = resolved
                break
        canonical[name] = best

    return canonical


def derive_variant(
    original_family: str,
    canonical_family: str,
    metadata_variant: str,
) -> str:
    """Derive the variant name when a font is grouped under a canonical family.

    The part of original_family that extends beyond canonical_family becomes
    the variant prefix. The metadata variant is appended if it adds new info.

    Examples:
        ("911 Porscha Condensed",        "911 Porscha", "Regular") → "Condensed"
        ("911 Porscha Condensed Italic", "911 Porscha", "Regular") → "Condensed Italic"
        ("911 Porscha Bold",             "911 Porscha", "Bold")    → "Bold"
        ("911 Porscha",                  "911 Porscha", "Regular") → "Regular"
        ("911 Porscha",                  "911 Porscha", "Bold")    → "Bold"
    """
    canon_lower = canonical_family.strip().lower()
    orig_lower = original_family.strip().lower()

    # Extract the extra words from the original family name
    family_suffix = orig_lower[len(canon_lower):].strip()  # e.g. "condensed italic"

    meta = metadata_variant.strip().lower()

    if not family_suffix:
        # Same family — use metadata variant unchanged
        return metadata_variant or "Regular"

    # family_suffix IS the variant descriptor
    # Only append metadata variant if it adds new words not already in suffix
    if meta and meta not in ("regular",) and meta not in family_suffix:
        combined = f"{family_suffix} {meta}"
    else:
        combined = family_suffix

    return combined.title()
