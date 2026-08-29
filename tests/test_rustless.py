import json,tempfile,unittest
from pathlib import Path
from tools.rustless.filesystem import discover_root,safe_relative
from tools.rustless.hashing import sha256_file
from tools.rustless.integrity import create,verify
from tools.rustless.fixtures import discover
from tools.rustless.repository import identity
from tools.rustless.toolchain import detect
from tools.rustless.gates import evaluate
from tools.rustless.executor import run

class RustlessTests(unittest.TestCase):
    def test_integrity_and_changes(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); (r/'fixtures').mkdir(); (r/'fixtures/a.json').write_text('{"a":1}')
            create(r,Path('manifest.json')); self.assertTrue(all(x[0]=='UNCHANGED' for x in verify(r,Path('manifest.json'))))
            (r/'fixtures/a.json').write_text('{"a":2}'); self.assertIn(('MODIFIED','fixtures/a.json'),verify(r,Path('manifest.json')))
    def test_fixture_discovery_and_hash(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); (r/'fixtures').mkdir(); p=r/'fixtures/a.txt'; p.write_text('x'); rows=discover(r); self.assertEqual(rows[0]['sha256'],sha256_file(p))
    def test_security(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); outside=r.parent/'outside'; outside.write_text('x'); self.assertIsNone(safe_relative(r,outside))
    def test_empty_and_missing_rust(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); tc=detect(r); gates,status=evaluate(tc,{}); self.assertEqual(status,'VERIFIED'); self.assertFalse(tc['cargo']['available'])
    def test_executor_determinism_and_isolation(self):
        out=run({'b':lambda:2,'a':lambda:1},2); self.assertEqual(list(out),['a','b']); self.assertFalse(out['a']['ok'] is False)
    def test_root_and_identity(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); (r/'pyproject.toml').write_text(''); self.assertEqual(discover_root(r),r); self.assertEqual(identity(r)['root'],str(r))

if __name__=='__main__': unittest.main()
