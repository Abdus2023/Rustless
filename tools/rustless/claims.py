from pathlib import Path
import re
CATS=('cargo test passes','cargo check passes','miri passes','runtime safety proven','benchmark','implementation complete')
def reconcile(root,toolchains):
    rows=[]
    for p in root.rglob('*'):
        if not p.is_file() or p.is_symlink() or p.suffix.lower() not in ('.md','.rst','.txt','.json','.toml','.yaml','.yml'): continue
        text=p.read_text(errors='replace')
        for line in text.splitlines():
            low=line.lower()
            for c in CATS:
                if c in low:
                    native=('cargo' in c or 'miri' in c) and not (toolchains.get('cargo',{}).get('available') and toolchains.get('rustc',{}).get('available'))
                    rows.append({'file':p.relative_to(root).as_posix(),'claim':line.strip(),'classification':'BLOCKED' if native else 'PROVISIONAL','status':'BLOCKED' if native else 'PROVISIONAL'})
                    break
    return sorted(rows,key=lambda x:(x['file'],x['claim']))
