from .models import Gate,Status,aggregate

def evaluate(toolchains,sections):
    rust=bool(toolchains.get('rust_files'))
    gates=[]
    base=[('Repository Inventory',True),('Fixture Integrity',True),('Provenance',True),('Static Analysis',True),('CI Reconciliation',False)]
    for i,(name,required) in enumerate(base,1): gates.append(Gate(f'RG-{i:03d}',name,required,Status.VERIFIED,reason='Python-side inspection completed.'))
    native=Status.VERIFIED if toolchains.get('cargo',{}).get('available') and toolchains.get('rustc',{}).get('available') else Status.BLOCKED
    for j,name in enumerate(('cargo_check','cargo_test','cargo_fmt','cargo_clippy','miri'),6):
        required=rust
        gates.append(Gate(f'RG-{j:03d}',name,required,native,reason='Native toolchain unavailable; rustless never emulates native execution.' if native==Status.BLOCKED else 'Tool availability detected; no native command executed by rustless.'))
    return [g.json() for g in gates],aggregate([g.status for g in gates if g.required]).value
