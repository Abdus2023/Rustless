import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.rustless.claims import reconcile
from tools.rustless.gates import evaluate
from tools.rustless.models import Status, aggregate
from tools.rustless.toolchain import detect


class AcceptanceAdversarialTests(unittest.TestCase):
    def test_fake_native_claim_is_provisional_when_tools_are_absent(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "README.md").write_text(
                "cargo test passes\ncargo clippy passes\nMiri passes\nbenchmark: 780K msg/s\n",
                encoding="utf-8",
            )
            (root / "Cargo.toml").write_text(
                '[package]\nname="fake"\nversion="0.1.0"\n', encoding="utf-8"
            )
            with patch("tools.rustless.toolchain.shutil.which", return_value=None):
                tc = detect(root)
            self.assertEqual(tc["native_rust_execution"], "BLOCKED")
            claims = reconcile(root, tc)
            self.assertTrue(claims)
            self.assertTrue(all(c["status"] == "PROVISIONAL" for c in claims))
            self.assertTrue(all(c["classification"] == "REPOSITORY_REPORTED" for c in claims))
            gates, overall = evaluate(tc, {})
            self.assertEqual(overall, "BLOCKED")
            native = [g for g in gates if g["name"] == "cargo_test"]
            self.assertEqual(native[0]["status"], "BLOCKED")

    def test_non_rust_repository_marks_native_gates_not_applicable(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "README.md").write_text("documentation only\n", encoding="utf-8")
            tc = detect(root)
            gates, overall = evaluate(tc, {})
            self.assertEqual(overall, "VERIFIED")
            for gate in gates:
                if gate["name"] in {"cargo_check", "cargo_test", "cargo_fmt", "cargo_clippy", "miri"}:
                    self.assertEqual(gate["status"], "VERIFIED")
                    self.assertEqual(gate["applicability"], "NOT_APPLICABLE")

    def test_status_contract_has_exactly_four_values(self):
        self.assertEqual({s.value for s in Status}, {
            "VERIFIED", "PARTIALLY_VERIFIED", "PROVISIONAL", "BLOCKED"
        })
        self.assertEqual(aggregate([Status.VERIFIED, Status.BLOCKED]), Status.BLOCKED)
        self.assertEqual(aggregate([Status.VERIFIED, Status.PROVISIONAL]), Status.PROVISIONAL)

    def test_unicode_and_space_paths_are_read_without_execution(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = root / "tests" / "fixtures"
            p.mkdir(parents=True)
            (p / "أسلم وجهه.json").write_text('{"ok": true}', encoding="utf-8")
            (p / "space name.txt").write_text("fixture", encoding="utf-8")
            # The assertion is deliberately limited to filesystem readability;
            # fixture contents are never executed.
            self.assertTrue((p / "أسلم وجهه.json").read_text(encoding="utf-8"))
            self.assertEqual(json.loads((p / "أسلم وجهه.json").read_text(encoding="utf-8"))["ok"], True)


if __name__ == "__main__":
    unittest.main()
