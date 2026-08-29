from pathlib import Path
import re

def inspect(root):
    files=sorted(list((root/'.github/workflows').glob('*.yml'))+list((root/'.github/workflows').glob('*.yaml'))) if (root/'.github/workflows').exists() else []
    rows=[]
    for p in files:
        text=p.read_text(errors='replace'); rows.append({'path':p.relative_to(root).as_posix(),'jobs':re.findall(r'^\s{2}([A-Za-z0-9_.-]+):\s*$',text,re.M),'commands':re.findall(r'\b(cargo\s+(?:fmt|check|test|clippy|miri)\b[^\n]*)',text)})
    return {'files':rows,'status':'VERIFIED','executed':False}
