import json
import re
from pathlib import Path
try:
    import yaml
except ImportError:
    yaml = None
import tomllib

def inspect(root):
    findings = []
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.is_symlink():
            continue
        rel = p.relative_to(root).as_posix(); suffix = p.suffix.lower()
        if suffix == '.json':
            try: json.loads(p.read_text(encoding='utf-8')); status='VERIFIED'; msg='valid JSON'
            except Exception as exc: status='BLOCKED'; msg=f'invalid JSON: {exc}'
            findings.append({'path':rel,'check':'json','status':status,'message':msg})
        elif suffix == '.toml':
            try: tomllib.loads(p.read_text(encoding='utf-8')); status='VERIFIED'; msg='valid TOML'
            except Exception as exc: status='BLOCKED'; msg=f'invalid TOML: {exc}'
            findings.append({'path':rel,'check':'toml','status':status,'message':msg})
        elif suffix in ('.yaml','.yml'):
            if yaml is None:
                findings.append({'path':rel,'check':'yaml','status':'PROVISIONAL','message':'YAML parser unavailable; file not executed or interpreted'})
            else:
                try: yaml.safe_load(p.read_text(encoding='utf-8')); status='VERIFIED'; msg='valid YAML'
                except Exception as exc: status='BLOCKED'; msg=f'invalid YAML: {exc}'
                findings.append({'path':rel,'check':'yaml','status':status,'message':msg})
    rust = any((root/x).exists() for x in ('Cargo.toml','rust-toolchain','rust-toolchain.toml'))
    bad = any(x['status']=='BLOCKED' for x in findings)
    return {'status':'BLOCKED' if bad else 'VERIFIED','mode':'STATIC_ONLY','rust_static':rust,'findings':findings,'native_claims_forbidden':['compile_success','runtime_success','borrow_checker_success','miri_success','clippy_success']}
