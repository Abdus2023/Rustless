from pathlib import Path
import os,tomllib
DEFAULT={'execution':{'jobs':min(8,os.cpu_count() or 1),'timeout_seconds':120},'fixtures':{'roots':[],'max_file_size':104857600},'integrity':{'manifest':'artifacts/rustless/integrity.json'},'gates':{'strict':False}}

def load_config(root:Path,path=None):
    cfg={k:(dict(v) if isinstance(v,dict) else v) for k,v in DEFAULT.items()}
    p=Path(path) if path else root/'rustless.toml'
    if p.exists():
        with p.open('rb') as f: raw=tomllib.load(f)
        for k,v in raw.items():
            if isinstance(v,dict): cfg[k]={**cfg.get(k,{}),**v}
            else: cfg[k]=v
    return cfg
