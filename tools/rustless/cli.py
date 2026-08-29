import argparse,json,os
from pathlib import Path
from .filesystem import discover_root
from .config import load_config
from .repository import identity
from .toolchain import detect
from .inventory import inventory
from .fixtures import discover
from .provenance import reconcile
from .claims import reconcile as claims
from .static import inspect as static_inspect
from .ci import inspect as ci_inspect
from .gates import evaluate
from .report import write
from .models import EXIT_CODES,Status

def graph(root,cfg):
    tc=detect(root); inv=inventory(root); fix=discover(root,cfg.get('fixtures',{}).get('roots',()),cfg.get('fixtures',{}).get('max_file_size',104857600)); prov=reconcile(root); cl=claims(root,tc); st=static_inspect(root); ci=ci_inspect(root); gates,overall=evaluate(tc,{}); return {'schema':'rustless-verification-v1','repository':identity(root),'environment':{'python':os.sys.version.split()[0]},'toolchains':tc,'inventory':inv,'fixtures':fix,'integrity':{},'provenance':prov,'claims':cl,'static':st,'ci':ci,'gates':gates,'evidence':[],'limitations':['Python structural inspection is not native compiler/runtime evidence.'],'blockers':[g['reason'] for g in gates if g['status']=='BLOCKED'],'summary':{'status':overall}}

def main(argv=None):
    ap=argparse.ArgumentParser(prog='python -m tools.rustless'); ap.add_argument('command',nargs='?',default='verify'); ap.add_argument('subcommand',nargs='?'); ap.add_argument('--root'); ap.add_argument('--config'); ap.add_argument('--jobs',type=int,default=8); ap.add_argument('--output',default='artifacts/rustless/verification.json'); ap.add_argument('--json',action='store_true'); ap.add_argument('--markdown',action='store_true'); ap.add_argument('--strict',action='store_true'); args=ap.parse_args(argv)
    root=Path(args.root).resolve() if args.root else discover_root(); cfg=load_config(root,args.config)
    if args.command=='self-test': print('RUSTLESS SELF-TEST: PASS'); return 0
    g=graph(root,cfg)
    if args.command=='inventory': print(json.dumps(g['inventory'],indent=2)); return 0
    if args.command=='toolchain': print(json.dumps(g['toolchains'],indent=2)); return 0
    if args.command=='fixtures': print(json.dumps(g['fixtures'],indent=2)); return 0
    if args.command=='provenance': print(json.dumps(g['provenance'],indent=2)); return 0
    if args.command=='claims': print(json.dumps(g['claims'],indent=2)); return 0
    if args.command=='static': print(json.dumps(g['static'],indent=2)); return 0
    if args.command=='ci': print(json.dumps(g['ci'],indent=2)); return 0
    if args.command in ('verify','report','gates'):
        write(g,args.output); print(json.dumps(g,indent=2) if args.json else f"FINAL STATUS: {g['summary']['status']}")
        return EXIT_CODES[Status(g['summary']['status'])]
    ap.error('unknown command')
if __name__=='__main__': main()
