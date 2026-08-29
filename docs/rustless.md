# Rustless Verification Framework

## Purpose

`tools/rustless` provides deterministic Python-side repository inspection and evidence preservation. It is designed to remain useful without Rust, Cargo, or other native toolchains.

## Architecture

The package separates models, filesystem safety, repository identity, toolchain detection, inventory, fixtures, hashing/integrity, provenance, claims, static analysis, CI inspection, evidence, parallel execution, gates, reports and CLI orchestration.

## Governance

The invariant is **NO EVIDENCE -> NO VERIFIED CLAIM**. Python structural verification is never equivalent to native compiler/runtime verification. Fixture integrity is not runtime correctness; claim consistency is not experimental proof.

## Statuses

- VERIFIED: direct sufficient evidence exists and required checks pass.
- PARTIALLY_VERIFIED: some evidence passes but a verification dimension remains unavailable.
- PROVISIONAL: asserted, inferred, declarative or unreproduced evidence.
- BLOCKED: a required prerequisite is missing. The blocker must state what, why, and how to unblock it.

Aggregation uses the severity order VERIFIED < PARTIALLY_VERIFIED < PROVISIONAL < BLOCKED for required gates; optional gates do not downgrade an otherwise successful required set.

## Reports

The canonical graph is `artifacts/rustless/verification.json`; `verification.md` is rendered from that graph. The graph records repository identity, environment, toolchains, inventory, fixtures, integrity, provenance, claims, checks, evidence, gates, limitations and blockers.

## Native boundary

If a Rust repository lacks usable native tooling, Rustless reports native execution gates as BLOCKED rather than emulating them. If native tooling is present, availability is still not proof that a command succeeded unless the command is actually executed by an explicitly trusted execution feature. CI definitions are inspected but never executed automatically.

## Security

Rustless does not execute repository scripts or fixtures, follow untrusted symlinks, install dependencies, run CI, modify source, or delete files. It applies root containment and file-size limits.

## Configuration

Optional `rustless.toml` supports fixture roots, size limits, integrity manifest path, jobs, timeout and strict policy. The package otherwise operates with safe defaults.

## CLI and exit codes

Use `python -m tools.rustless verify`. Exit codes are 0/1/2/3/4 for VERIFIED/PARTIALLY_VERIFIED/PROVISIONAL/BLOCKED/tool error.

## Limitations

Rustless is an evidence-preservation and verification framework. It is not a compiler, interpreter, runtime, sanitizer, debugger, VM, or replacement for native toolchains. It cannot infer execution correctness from source shape or documentation.
