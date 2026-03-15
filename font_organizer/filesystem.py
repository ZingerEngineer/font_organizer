"""Safe file operations: move, dedup, trash."""

from __future__ import annotations

import shutil
from pathlib import Path


def make_font_filename(family: str, variant: str, suffix: str) -> str:
    """Build the canonical font filename from family and variant names.

    Format: {family_lower}_{variant_lower}{suffix}
    Example: ("Open Sans", "Bold Italic", ".ttf") → "open sans_bold italic.ttf"
    """
    family_part = family.lower().strip()
    variant_part = (variant or "regular").lower().strip()
    return f"{family_part}_{variant_part}{suffix}"


def resolve_destination(
    source: Path,
    target_dir: Path,
    new_name: str | None = None,
) -> Path:
    """Return a non-colliding destination path inside target_dir.

    Uses new_name as the filename when provided, otherwise source.name.
    Appends -1, -2, etc. to the stem if the target already exists.
    This function is pure (no I/O).
    """
    base = new_name if new_name is not None else source.name
    candidate = target_dir / base
    if not candidate.exists():
        return candidate

    stem = Path(base).stem
    suffix = Path(base).suffix
    counter = 1
    while True:
        candidate = target_dir / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def ensure_directory(path: Path, dry_run: bool) -> None:
    """Create directory (and parents) if it does not exist."""
    if not dry_run:
        path.mkdir(parents=True, exist_ok=True)


def move_font(
    source: Path,
    family_dir: Path,
    dry_run: bool,
    new_name: str | None = None,
) -> Path:
    """Move source font into family_dir, optionally renaming it.

    new_name overrides the destination filename (used for canonical renaming).
    Returns the final destination path (resolved, not created in dry-run mode).
    """
    destination = resolve_destination(source, family_dir, new_name)
    if not dry_run:
        ensure_directory(family_dir, dry_run=False)
        shutil.move(str(source), str(destination))
    return destination


def trash_file(path: Path, dry_run: bool) -> None:
    """Move path to the OS recycle bin / trash.

    Catches TrashPermissionError on headless Linux and logs nothing further —
    the caller is responsible for logging before calling this function.
    """
    if dry_run:
        return
    try:
        from send2trash import send2trash  # type: ignore
        send2trash(str(path))
    except PermissionError:
        # Let PermissionError propagate unwrapped so the caller can suggest sudo
        raise
    except Exception as exc:
        raise RuntimeError(f"Could not trash {path.name}: {exc}") from exc
