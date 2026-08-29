import json
import tempfile
import time
import unittest
from pathlib import Path

from tools.rustless.filesystem import discover_root, safe_relative
from tools.rustless.hashing import sha256_file
from tools.rustless.integrity import create, verify
from tools.rustless.fixtures import discover
from tools.rustless.repository import identity
from tools.rustless.toolchain import detect
from tools.rustless.gates import evaluate
from tools.rustless.executor import run
from tools.rustless.models import Status, aggregate
from tools.rustless.evidence import EvidenceStore
from tools.rustless.report import markdown

class RustlessTests(unittest.TestCase):
    def test_status_contract(self):
        self.assertEqual(aggregate([Status.VERIFIED]), Status.VERIFIED)
        self.assertEqual(aggregate([Status.VERIFIED, Status.PARTIALLY_VERIFIED]), Status.PARTIALLY_VERIFIED)
        self.assertEqual(aggregate([Status.VERIFIED, Status.PROVISIONAL]), Status.PROVISIONAL)
        self.assertEqual(aggregate([Status.VERIFIED, Status.BLOCKED]), Status.BLOCKED)

    def test_integrity_and_changes(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); (r/'fixtures').mkdir(); (r/'fixtures/a.json').write_text('{"a":1}')
            create(r,Path('manifest.json'))
            self.assertTrue(all(x[0]=='UNCHANGED' for x in verify(r,Path('manifest.json'))))
            (r/'fixtures/a.json').write_text('{"a":2}')
            self.assertIn(('MODIFIED','fixtures/a.json'),verify(r,Path('manifest.json')))
            (r/'new.txt').write_text('new')
            self.assertIn(('ADDED','new.txt'),verify(r,Path('manifest.json')))
            (r/'new.txt').unlink()
            (r/'fixtures/a.json').unlink()
            self.assertIn(('REMOVED','fixtures/a.json'),verify(r,Path('manifest.json')))

    def test_fixture_discovery_and_hash(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); (r/'fixtures').mkdir(); p=r/'fixtures/a.txt'; p.write_text('x')
            rows=discover(r); self.assertEqual(rows[0]['sha256'],sha256_file(p)); self.assertEqual(rows[0]['binary'],False)

    def test_security_and_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); outside=r.parent/'outside'; outside.write_text('x')
            self.assertIsNone(safe_relative(r,outside))
            (r/'fixtures').mkdir(); link=r/'fixtures'/'outside'; link.symlink_to(outside)
            self.assertEqual(discover(r),[])

    def test_empty_and_missing_rust(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); tc=detect(r); gates,status=evaluate(tc,{})
            self.assertEqual(status,'VERIFIED'); self.assertIn('native_rust_execution',tc)

    def test_rust_native_gate_blocked_without_tools(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); (r/'Cargo.toml').write_text('[package]\nname="x"\nversion="0.1.0"\n')
            tc=detect(r)
            if not (tc['cargo']['available'] and tc['rustc']['available']):
                gates,status=evaluate(tc,{})
                self.assertEqual(status,'BLOCKED'); self.assertTrue(any(g['name']=='cargo_test' and g['status']=='BLOCKED' for g in gates))

    def test_executor_determinism_and_isolation(self):
        def bad(): raise ValueError('boom')
        out=run({'b':lambda:2,'a':lambda:1,'bad':bad},2)
        self.assertEqual(list(out),['a','b','bad']); self.assertTrue(out['a']['ok']); self.assertFalse(out['bad']['ok'])

    def test_executor_timeout(self):
        out=run({'slow':lambda: time.sleep(0.05)},1,timeout_seconds=0.001)
        self.assertFalse(out['slow']['ok']); self.assertIn('TimeoutError',out['slow']['error'])

    def test_root_and_identity(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); (r/'pyproject.toml').write_text(''); self.assertEqual(discover_root(r),r); self.assertEqual(identity(r)['root'],str(r))

    def test_evidence_stability_and_report(self):
        a=EvidenceStore(); b=EvidenceStore()
        self.assertEqual(a.add('sha256','a',Status.VERIFIED,'hash'), b.add('sha256','a',Status.VERIFIED,'hash'))
        g={'summary':{'status':'VERIFIED'},'repository':{},'environment':{},'toolchains':{},'inventory':{},'fixtures':[],'integrity':{},'provenance':{},'claims':[],'static':{},'ci':{},'gates':[],'evidence':a.json(),'limitations':[],'blockers':[]}
        self.assertIn('# Rustless Verification Report',markdown(json.loads(json.dumps(g,sort_keys=True))))

if __name__=='__main__': unittest.main()
