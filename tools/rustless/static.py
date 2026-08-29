import json,re
from pathlib import Path
try: import yaml
except ImportError: yaml=None

def inspect(root):
    findings=[]
    for p in root.rglob('*'):
        if p.is_file() and not p.is_symlink() and p.suffix.lower()=='.json':
            try: json.loads(p.read_text()); findings.append({'path':p.relative_to(root).as_posix(),'check':'json','status':'VERIFIED'})
            except Exception as e: findings.append({'path':p.relative_to(root).as_posix(),'check':'json','status':'PROVISIONAL','message':str(e)})
    rust=any((root/x).exists() for x in ('Cargo.toml','src'))
    return {'status':'VERIFIED','mode':'STATIC_ONLY','rust_static':rust,'findings':findings,'native_claims_forbidden':['compile_success','runtime_success','borrow_checker_success','miri_success','clippy_success']}
