from pathlib import Path
from .filesystem import iter_files
from .hashing import sha256_file
PATTERNS=('fixture','fixtures','testdata','golden','goldens','snapshots','samples','examples','corpus','corpora','vectors','expected','reference')
def discover(root,configured=(),max_file_size=104857600):
    rows=[]
    for p,rel in iter_files(root,max_size=max_file_size):
        parts={x.lower() for x in Path(rel).parts}
        if configured and not any(rel.startswith(str(x).rstrip('/')+'/') or rel==str(x) for x in configured): continue
        if configured or parts.intersection(PATTERNS):
            binary=True
            try: data=p.read_bytes(); binary=b'\0' in data[:8192]; parseable=True
            except OSError: data=b''; parseable=False
            rows.append({'path':rel,'type':p.suffix.lower().lstrip('.') or 'file','size':p.stat().st_size,'sha256':sha256_file(p),'modified':None,'binary':binary,'parseable':parseable})
    return sorted(rows,key=lambda x:x['path'])
