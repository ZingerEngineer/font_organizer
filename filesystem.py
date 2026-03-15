"""Safe file operations: move, dedup, trash."""

from __future__ import annotations

import shutil
from pathlib import Path


def resolve_destination(source: Path, target_dir: Path) -> Path:
    """Return a non-colliding destination path inside target_dir.

    If target_dir/source.name already exists, appends -1, -2, etc. to the stem.
    This function is pure (no I/O).
    """
    candidate = target_dir / source.name
    if not candidate.exists():
        return candidate

    stem = source.stem
    suffix = source.suffix
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


def move_font(source: Path, family_dir: Path, dry_run: bool) -> Path:
    """Move source font into family_dir, avoiding overwrites.

    Returns the final destination path (resolved, not created in dry-run mode).
    """
    destination = resolve_destination(source, family_dir)
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
