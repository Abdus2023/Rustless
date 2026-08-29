import shutil, subprocess
TOOLS = ('rustc','cargo','rustup','python','python3','git','node','npm','go','java')

def _version(name):
    try:
        r = subprocess.run([name, '--version'], capture_output=True, text=True, timeout=5, check=False)
        return (r.stdout or r.stderr).splitlines()[0] if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None

def detect(root):
    out = {name: {'available': bool(shutil.which(name)), 'path': shutil.which(name), 'version': None} for name in TOOLS}
    for name in TOOLS:
        if out[name]['available']:
            out[name]['version'] = _version(name)
    rustfiles = [x for x in ('rust-toolchain','rust-toolchain.toml','Cargo.toml','Cargo.lock') if (root/x).exists()]
    rust = bool(rustfiles)
    out['rust_files'] = rustfiles
    out['required_native_tools'] = {'rustc': out['rustc']['available'], 'cargo': out['cargo']['available']} if rust else {}
    out['native_rust_execution'] = 'BLOCKED' if rust and not (out['rustc']['available'] and out['cargo']['available']) else ('UNEXECUTED' if rust else 'NOT_APPLICABLE')
    out['execution_policy'] = 'rustless does not execute native toolchains automatically'
    return out
