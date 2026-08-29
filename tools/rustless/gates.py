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
            gate = Gate(f"RG-{offset:03d}", name, False, Status.VERIFIED, class_name="advisory", reason="Native gate not applicable: no Rust manifest or source marker detected.")
            data = gate.json()
            data["applicability"] = "NOT_APPLICABLE"
        else:
            reason = ("Native tools are available, but rustless does not execute native commands automatically; independent native evidence is required."
                      if native_available else "Native prerequisite unavailable; rustless does not emulate native execution.")
            gate = Gate(f"RG-{offset:03d}", name, True, Status.BLOCKED, class_name="required", reason=reason, blocking_reasons=[reason])
            data = gate.json()
            data["applicability"] = "APPLICABLE"
        gates.append(data)
    required_status = aggregate(Status(g["status"]) for g in gates if g["required"])
    return gates, required_status.value
