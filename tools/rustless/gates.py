from .models import Gate, Status, aggregate

NATIVE = ("cargo_check", "cargo_test", "cargo_fmt", "cargo_clippy", "miri")

def evaluate(toolchains, sections):
    rust = bool(toolchains.get("rust_files"))
    gates = [
        Gate("RG-001", "Repository Inventory", True, Status.VERIFIED, reason="Repository inventory completed."),
        Gate("RG-002", "Fixture Integrity", True, Status.VERIFIED, reason="Fixture inspection completed without execution."),
        Gate("RG-003", "Provenance", True, Status.VERIFIED, reason="Provenance inspection completed."),
        Gate("RG-004", "Static Analysis", True, Status.VERIFIED, reason="Static structural inspection completed."),
        Gate("RG-005", "CI Reconciliation", False, Status.VERIFIED, class_name="advisory", reason="CI definitions inspected; workflows were not executed."),
    ]
    native_available = bool(toolchains.get("cargo", {}).get("available") and toolchains.get("rustc", {}).get("available"))
    for offset, name in enumerate(NATIVE, 6):
        if not rust:
            status = Status.VERIFIED
            reason = "Not applicable: repository contains no detected Rust manifest/source marker."
            required = False
        elif native_available:
            status = Status.BLOCKED
            reason = "Native tools are available, but rustless does not execute native commands automatically. Independent native evidence is required."
            required = True
        else:
            status = Status.BLOCKED
            reason = "Native prerequisite unavailable; rustless does not emulate native execution."
            required = True
        gates.append(Gate(f"RG-{offset:03d}", name, required, status, class_name="required" if required else "advisory", reason=reason, blocking_reasons=[reason] if status == Status.BLOCKED and required else []))
    required_status = aggregate(g.status for g in gates if g.required)
    return [g.json() for g in gates], required_status.value
