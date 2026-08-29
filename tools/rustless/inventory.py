from collections import Counter
from pathlib import Path
from .filesystem import iter_files

def inventory(root):
    files=list(iter_files(root)); ext=Counter(p.suffix.lower().lstrip('.') or '[no-extension]' for p,_ in files)
    markers=['.git','pyproject.toml','Cargo.toml','package.json','Makefile','README.md','rust-toolchain','rust-toolchain.toml']
    ci=[]; tests=[]; fixtures=[]; docs=[]; schemas=[]; generated=[]; locks=[]
    for p,rel in files:
        l=rel.lower()
        if '.github/workflows/' in l or Path(rel).name in ('Jenkinsfile','.gitlab-ci.yml','azure-pipelines.yml'): ci.append(rel)
        if any(x in Path(rel).parts for x in ('test','tests')): tests.append(rel)
        if any(x in Path(rel).parts for x in ('fixture','fixtures','testdata','golden','goldens','snapshots','samples','corpus','corpora','vectors','expected','reference')): fixtures.append(rel)
        if p.suffix.lower() in ('.md','.rst','.txt'): docs.append(rel)
        if p.suffix.lower() in ('.json','.schema'): schemas.append(rel)
        if any(x in l for x in ('generated','gen/')): generated.append(rel)
        if p.name in ('Cargo.lock','package-lock.json','poetry.lock','Pipfile.lock'): locks.append(rel)
    return {'files':len(files),'directories':len({str(p.parent.relative_to(root)) for p,_ in files}),'extensions':dict(sorted(ext.items())),'markers':[m for m in markers if (root/m).exists()],'ci_files':ci,'test_files':tests,'fixture_files':fixtures,'documentation_files':docs,'schema_candidates':schemas,'generated_candidates':generated,'lockfiles':locks}
