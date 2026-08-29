# Rustless

Rustless is a repository-agnostic, stdlib-first Python evidence-preservation and verification framework. It can inspect Rust, Python, mixed-language, documentation, fixture, schema and CI repositories when native tooling is unavailable.

**Rustless is not a compiler, interpreter, runtime, sanitizer, debugger, VM, or replacement for native toolchains.** No source parsing or fixture inspection is treated as native execution evidence.

## CLI

`python -m tools.rustless verify --root PATH`

Commands include `inventory`, `toolchain`, `fixtures`, `integrity`, `provenance`, `claims`, `static`, `ci`, `gates`, `verify`, `report`, and `self-test`. Options include `--root`, `--config`, `--jobs`, `--json`, `--markdown`, `--output`, `--strict`, `--verbose`, `--quiet`, `--fail-on`, `--include`, and `--exclude`.

## Status contract

`VERIFIED` means direct sufficient evidence for the specific property. `PARTIALLY_VERIFIED` means only part of the requested evidence is established. `PROVISIONAL` means inferred, declarative, repository-reported or independently unreproduced. `BLOCKED` means a required prerequisite is unavailable.

Native Rust gates remain `BLOCKED` when `cargo`/`rustc` cannot actually run. Rustless never fabricates cargo, rustc, clippy, rustfmt, test or Miri output.

## Evidence and canonical graph

`artifacts/rustless/verification.json` is the canonical machine-readable graph. Markdown is rendered from that graph. Evidence IDs are deterministic and timestamps are omitted by default.

## Integrity

SHA-256 manifests use deterministic relative paths and ordering. Manifest creation refuses to overwrite an existing manifest. Verification reports `ADDED`, `REMOVED`, `MODIFIED`, and `UNCHANGED`.

## Security and determinism

Repository files are treated as untrusted. Symlinks and special files are not followed; file-size limits apply; fixtures are never executed. Results are sorted and stable. Rustless does not install packages, run CI workflows, modify source, or delete files.

## Configuration

An optional `rustless.toml` may define repository, integrity, fixtures, execution and gate policies. No configuration is required.

## Exit codes

`0 VERIFIED`, `1 PARTIALLY_VERIFIED`, `2 PROVISIONAL`, `3 BLOCKED`, `4 TOOL/USAGE ERROR`. Strict policy may be used by CI wrappers to reject non-verified outcomes.

## Limitations

Natural-language truth determination is intentionally out of scope. Static inspection cannot prove compilation, borrow checking, runtime behavior, performance, sanitizer results or Miri results. External claims remain claims unless independently supplied evidence exists.
