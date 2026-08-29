from pathlib import Path
import tomllib
DEFAULT={'execution':{'jobs':min(8,os.cpu_count() or 1),'timeout_seconds':120},'fixtures':{'roots':[],'max_file_size':104857600},'integrity':{'manifest':'artifacts/rustless/integrity.json'},'gates':{'strict':False}}
import os

def load_config(root:Path,path=None):
    cfg=dict(DEFAULT)
    p=Path(path) if path else root/'rustless.toml'
    if p.exists():
        with p.open('rb') as f: raw=tomllib.load(f)
        for k,v in raw.items():
            if isinstance(v,dict): cfg[k]={**cfg.get(k,{}),**v}
            else: cfg[k]=v
    return cfg
