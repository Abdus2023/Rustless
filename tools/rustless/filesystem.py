from pathlib import Path
import os

DEFAULT_EXCLUDES = (".git", "__pycache__")


def discover_root(start=None):
    p = Path(start or Path.cwd()).resolve()
    markers = (".git", "pyproject.toml", "Cargo.toml", "package.json", "Makefile", "README.md", "README.rst", "README.txt")
    for q in (p, *p.parents):
        if any((q / x).exists() for x in markers):
            return q
    return p


def safe_relative(root, path):
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (ValueError, OSError):
        return None


def _matches(rel, patterns):
    p = Path(rel)
    return any(p.match(x) or rel == x or rel.startswith(x.rstrip("/") + "/") for x in patterns)


def iter_files(root, include=(), exclude=(), max_size=104857600):
    root = Path(root).resolve()
    excludes = tuple(DEFAULT_EXCLUDES) + tuple(exclude)
    for base, dirs, files in os.walk(root, topdown=True, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not (Path(base) / d).is_symlink() and not _matches(safe_relative(root, Path(base) / d) or d, excludes))
        for name in sorted(files):
            p = Path(base) / name
            if p.is_symlink() or not p.is_file():
                continue
            rel = safe_relative(root, p)
            if rel is None or _matches(rel, excludes):
                continue
            if include and not _matches(rel, include):
                continue
            try:
                if p.stat().st_size <= max_size:
                    yield p, rel
            except OSError:
                continue
