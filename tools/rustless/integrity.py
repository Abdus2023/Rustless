import json
from pathlib import Path
from .filesystem import iter_files
from .hashing import sha256_file

def manifest(root,include=(),exclude=(),max_file_size=104857600):
    rows=[]
    for p,rel in iter_files(root,include,exclude,max_file_size): rows.append({'path':rel,'size':p.stat().st_size,'sha256':sha256_file(p)})
    return {'format':'rustless-integrity-v1','root':'.','algorithm':'sha256','files':sorted(rows,key=lambda x:x['path'])}
def create(root,path,include=(),exclude=()):
    p=root/path
    if p.exists(): raise FileExistsError(f'manifest exists: {p}')
    data=manifest(root,include,exclude); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n'); return data
def verify(root,path):
    m=json.loads((root/path).read_text()); expected={x['path']:x for x in m.get('files',[])}; actual={r:{'path':r,'size':p.stat().st_size,'sha256':sha256_file(p)} for p,r in iter_files(root)}
    changes=[]
    for r in sorted(set(expected)|set(actual)):
        if r not in expected: changes.append(('ADDED',r))
        elif r not in actual: changes.append(('REMOVED',r))
        elif expected[r]['size']!=actual[r]['size'] or expected[r]['sha256']!=actual[r]['sha256']: changes.append(('MODIFIED',r))
        else: changes.append(('UNCHANGED',r))
    return changes
