import shutil,subprocess
TOOLS=('rustc','cargo','rustup','python','python3','git','node','npm','go','java')
def detect(root):
    out={}
    for name in TOOLS:
        p=shutil.which(name); ver=None
        if p:
            try:
                r=subprocess.run([name,'--version'],capture_output=True,text=True,timeout=5); ver=(r.stdout or r.stderr).splitlines()[0] if r.returncode==0 else None
            except Exception: pass
        out[name]={'available':bool(p),'path':p,'version':ver}
    rustfiles=[x for x in ('rust-toolchain','rust-toolchain.toml','Cargo.toml','Cargo.lock') if (root/x).exists()]
    cargo=out['cargo']['available']; rustc=out['rustc']['available']
    out['native_rust_execution']='VERIFIED' if cargo and rustc else 'BLOCKED'
    out['rust_files']=rustfiles
    return out
