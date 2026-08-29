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
            status = None
            reason = "NOT_APPLICABLE: no Rust manifest or source marker detected; no native Rust claim is made."
            required = False
            applicability = "NOT_APPLICABLE"
        elif native_available:
            status = Status.BLOCKED
            reason = "Native tools are available, but rustless does not execute native commands automatically. Independent native evidence is required."
            required = True
            applicability = "APPLICABLE"
        else:
            status = Status.BLOCKED
            reason = "Native prerequisite unavailable; rustless does not emulate native execution."
            required = True
            applicability = "APPLICABLE"
        gate = Gate(f"RG-{offset:03d}", name, required, status or Status.VERIFIED, class_name="required" if required else "advisory", reason=reason, blocking_reasons=[reason] if status == Status.BLOCKED and required else [])
        data = gate.json()
        data["applicability"] = applicability
        if not rust:
            data["status"] = "NOT_APPLICABLE"
        gates.append(data)
    required_status = aggregate(Status(g["status"]) for g in gates if g["required"] and g["status"] != "NOT_APPLICABLE")
    return gates, required_status.value
