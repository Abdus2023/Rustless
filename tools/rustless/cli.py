import argparse,json,os,subprocess,sys
from pathlib import Path
from .filesystem import discover_root
from .config import load_config
from .repository import identity
from .toolchain import detect
from .inventory import inventory
from .fixtures import discover
from .integrity import create,verify
from .provenance import reconcile
from .claims import reconcile as claims
from .static import inspect as static_inspect
from .ci import inspect as ci_inspect
from .gates import evaluate
from .report import write
from .models import EXIT_CODES,Status

def graph(root,cfg):
    tc=detect(root); inv=inventory(root); fix=discover(root,cfg.get('fixtures',{}).get('roots',()),cfg.get('fixtures',{}).get('max_file_size',104857600)); prov=reconcile(root); cl=claims(root,tc); st=static_inspect(root); ci=ci_inspect(root); gates,overall=evaluate(tc,{})
    return {'schema':'rustless-verification-v1','repository':identity(root),'environment':{'python':sys.version.split()[0]},'toolchains':tc,'inventory':inv,'fixtures':fix,'integrity':{},'provenance':prov,'claims':cl,'static':st,'ci':ci,'gates':gates,'evidence':[],'limitations':['Python structural inspection is not native compiler/runtime evidence.'],'blockers':[g['reason'] for g in gates if g['status']=='BLOCKED'],'summary':{'status':overall}}

def main(argv=None):
    ap=argparse.ArgumentParser(prog='python -m tools.rustless'); ap.add_argument('command',nargs='?',default='verify'); ap.add_argument('subcommand',nargs='?'); ap.add_argument('--root'); ap.add_argument('--config'); ap.add_argument('--jobs',type=int,default=8); ap.add_argument('--output',default='artifacts/rustless/verification.json'); ap.add_argument('--json',action='store_true'); ap.add_argument('--markdown',action='store_true'); ap.add_argument('--strict',action='store_true'); ap.add_argument('--verbose',action='store_true'); ap.add_argument('--quiet',action='store_true'); ap.add_argument('--fail-on',choices=[s.value for s in Status]); ap.add_argument('--include',action='append',default=[]); ap.add_argument('--exclude',action='append',default=[]); args=ap.parse_args(argv)
    root=Path(args.root).resolve() if args.root else discover_root(); cfg=load_config(root,args.config)
    if args.command=='self-test': return subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_rustless.py'],cwd=root).returncode
    if args.command=='integrity' and args.subcommand=='create': create(root,Path(cfg['integrity']['manifest']),args.include,args.exclude); print('INTEGRITY MANIFEST: CREATED'); return 0
    if args.command=='integrity' and args.subcommand=='verify':
        changes=verify(root,Path(cfg['integrity']['manifest'])); print(json.dumps(changes,indent=2)); return 0 if not [x for x in changes if x[0] in ('ADDED','REMOVED','MODIFIED')] else 3
    g=graph(root,cfg)
    if args.command in ('inventory','toolchain','fixtures','provenance','claims','static','ci'):
        key={'inventory':'inventory','toolchain':'toolchains','fixtures':'fixtures','provenance':'provenance','claims':'claims','static':'static','ci':'ci'}[args.command]; print(json.dumps(g[key],indent=2)); return 0
    if args.command in ('verify','report','gates'):
        write(g,args.output); print(json.dumps(g,indent=2) if args.json else f"FINAL STATUS: {g['summary']['status']}"); return EXIT_CODES[Status(g['summary']['status'])]
    ap.error('unknown command')
if __name__=='__main__': main()
