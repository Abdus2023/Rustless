from pathlib import Path

CATS = (
    "cargo test passes",
    "cargo check passes",
    "cargo clippy passes",
    "miri passes",
    "runtime safety proven",
    "benchmark",
    "implementation complete",
)


def _classification(claim: str) -> str:
    low = claim.lower()
    if any(x in low for x in ("cargo test", "cargo check", "cargo clippy", "miri")):
        return "REPOSITORY_REPORTED"
    if "benchmark" in low or "runtime safety" in low or "implementation complete" in low:
        return "REPOSITORY_REPORTED"
    return "DECLARATIVE"


def reconcile(root, toolchains):
    rows = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.is_symlink() or p.suffix.lower() not in (
            ".md", ".rst", ".txt", ".json", ".toml", ".yaml", ".yml"
        ):
            continue
        try:
            text = p.read_text(errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            low = line.lower()
            for category in CATS:
                if category in low:
                    rows.append({
                        "file": p.relative_to(root).as_posix(),
                        "claim": line.strip(),
                        "classification": _classification(line.strip()),
                        "status": "PROVISIONAL",
                        "required_evidence": [category],
                    })
                    break
    return sorted(rows, key=lambda x: (x["file"], x["claim"]))
