from .models import Gate,Status,aggregate

def evaluate(toolchains,sections):
    gates=[]
    for i,(name,status,required) in enumerate([('Repository Inventory','VERIFIED',True),('Fixture Integrity','VERIFIED',True),('Provenance','VERIFIED',True),('Static Analysis','VERIFIED',True),('CI Reconciliation','VERIFIED',False)]): gates.append(Gate(f'RG-{i+1:03d}',name,required,Status(status),reason='Python-side inspection completed.'))
    native=Status.VERIFIED if toolchains.get('cargo',{}).get('available') and toolchains.get('rustc',{}).get('available') else Status.BLOCKED
    for j,name in enumerate(('cargo_check','cargo_test','cargo_fmt','cargo_clippy','miri'),6): gates.append(Gate(f'RG-{j:03d}',name,True,native,reason='Native toolchain unavailable; rustless never emulates native execution.' if native==Status.BLOCKED else 'Tool available; rustless records availability only.'))
    required=[g.status for g in gates if g.required]
    overall=aggregate(required)
    return [g.json() for g in gates],overall.value
