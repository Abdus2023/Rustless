from .models import Gate, Status, aggregate

NATIVE = ("cargo_check", "cargo_test", "cargo_fmt", "cargo_clippy", "miri")


def _section_status(sections, name):
    value = sections.get(name, {})
    if isinstance(value, dict) and "status" in value:
        try:
            return Status(value["status"])
        except ValueError:
            return Status.BLOCKED
    return Status.VERIFIED if value is not None else Status.BLOCKED


def evaluate(toolchains, sections):
    gates = []
    for gid, name, section in (
        ("RG-001", "Repository Inventory", "inventory"),
        ("RG-002", "Fixture Integrity", "fixtures"),
        ("RG-003", "Provenance", "provenance"),
        ("RG-004", "Static Analysis", "static"),
        ("RG-005", "CI Reconciliation", "ci"),
    ):
        status = _section_status(sections, section)
        required = gid != "RG-005"
        gates.append(Gate(
            gid, name, required, status,
            reason=f"{name} result: {status.value}.",
            blocking_reasons=[f"{name} did not complete successfully."] if status == Status.BLOCKED and required else [],
            class_name="required" if required else "advisory",
        ).json())

    rust = bool(toolchains.get("rust_files"))
    native_available = bool(
        toolchains.get("cargo", {}).get("available")
        and toolchains.get("rustc", {}).get("available")
    )
    for offset, name in enumerate(NATIVE, 6):
        if not rust:
            gate = Gate(
                f"RG-{offset:03d}", name, False, Status.PARTIALLY_VERIFIED,
                reason="Native gate not applicable: no Rust marker detected; no native verification was performed.",
                class_name="advisory",
            ).json()
            gate["applicability"] = "NOT_APPLICABLE"
        else:
            reason = (
                "Native tools are available, but rustless does not execute native commands automatically; "
                "independent native execution evidence is required."
                if native_available else
                "Native prerequisite unavailable; rustless does not emulate native execution."
            )
            gate = Gate(
                f"RG-{offset:03d}", name, True, Status.BLOCKED,
                reason=reason,
                blocking_reasons=[reason],
                class_name="required",
            ).json()
            gate["applicability"] = "APPLICABLE"
        gates.append(gate)

    required_status = aggregate(Status(g["status"]) for g in gates if g["required"])
    return gates, required_status.value
