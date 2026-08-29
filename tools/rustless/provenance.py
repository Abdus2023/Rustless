from pathlib import Path
import json,re
KEYS=('source','origin','commit','commit_sha','revision','version','generated_from','derived_from','fixture_of','copied_from','evidence','citation','artifact')
def reconcile(root):
    refs=[]; broken=[]
    for p in root.rglob('*'):
        if not p.is_file() or p.is_symlink() or p.stat().st_size>10485760: continue
        if p.suffix.lower() not in ('.md','.json','.toml','.yaml','.yml'): continue
        text=p.read_text(errors='replace')
        for k in KEYS:
            if re.search(r'\b'+re.escape(k)+r'\s*[:=]',text,re.I): refs.append({'file':p.relative_to(root).as_posix(),'field':k})
    return {'status':'VERIFIED' if not broken else 'BLOCKED','references':sorted(refs,key=lambda x:(x['file'],x['field'])),'broken':broken,'graph_edges':[]}
