from tools.rustless.gates import evaluate
from tools.rustless.claims import reconcile


def test_non_rust_native_gates_are_not_native_successes(tmp_path):
    gates, _ = evaluate({}, {})
    native = [g for g in gates if g["id"] >= "RG-006"]
    assert native
    assert all(g["status"] != "VERIFIED" for g in native)
    assert all(g.get("applicability") == "NOT_APPLICABLE" for g in native)


def test_rust_without_native_tools_blocks_native_gates(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "Cargo.toml").write_text("[package]\nname='x'\nversion='0.1.0'\n")
    gates, _ = evaluate({"rust_files": ["Cargo.toml"], "cargo": {"available": False}, "rustc": {"available": False}}, {})
    native = [g for g in gates if g["id"] >= "RG-006"]
    assert all(g["status"] == "BLOCKED" for g in native)


def test_claims_do_not_become_evidence_backed_from_tool_presence(tmp_path):
    (tmp_path / "README.md").write_text("cargo test passes\n")
    rows = reconcile(tmp_path, {"cargo": {"available": True}, "rustc": {"available": True}})
    assert rows
    assert rows[0]["status"] == "PROVISIONAL"
    assert rows[0]["classification"] != "EVIDENCE_BACKED"
