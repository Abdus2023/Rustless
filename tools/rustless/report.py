import json
from pathlib import Path

def markdown(g):
    s=g.get('summary',{}); lines=['# Rustless Verification Report','## Executive Summary',f"FINAL STATUS: {s.get('status')}",'','## Repository Identity',json.dumps(g.get('repository',{}),indent=2),'','## Environment',json.dumps(g.get('environment',{}),indent=2),'','## Toolchains',json.dumps(g.get('toolchains',{}),indent=2),'','## Inventory',json.dumps(g.get('inventory',{}),indent=2),'','## Fixtures',json.dumps(g.get('fixtures',[]),indent=2),'','## Integrity',json.dumps(g.get('integrity',{}),indent=2),'','## Provenance',json.dumps(g.get('provenance',{}),indent=2),'','## Claims',json.dumps(g.get('claims',[]),indent=2),'','## Static Analysis',json.dumps(g.get('static',{}),indent=2),'','## CI Reconciliation',json.dumps(g.get('ci',{}),indent=2),'','## Gates',json.dumps(g.get('gates',[]),indent=2),'','## Evidence',json.dumps(g.get('evidence',[]),indent=2),'','## Limitations',json.dumps(g.get('limitations',[]),indent=2),'','## Blockers',json.dumps(g.get('blockers',[]),indent=2),'','## Final Status',f"FINAL STATUS: {s.get('status')}"]
    return '\n'.join(lines)+'\n'
def write(graph,out):
    out=Path(out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(graph,indent=2,sort_keys=True)+'\n'); out.with_suffix('.md').write_text(markdown(graph))
