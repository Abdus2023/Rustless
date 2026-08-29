import argparse, json, sys
from pathlib import Path
from .filesystem import discover_root
from .config import load_config
from .repository import identity
from .toolchain import detect
from .inventory import inventory
from .fixtures import discover
from .integrity import create, verify as verify_integrity, manifest
from .provenance import reconcile
from .claims import reconcile as reconcile_claims
from .static import inspect as static_inspect
from .ci import inspect as ci_inspect
from .gates import evaluate
from .evidence import EvidenceStore
from .executor import run
from .report import write
from .models import EXIT_CODES, Status


def graph(root, cfg, jobs=8, include=(), exclude=()):
    tc, inv, fix = detect(root), inventory(root), discover(root, cfg.get('fixtures', {}).get('roots', ()), cfg.get('fixtures', {}).get('max_file_size', 104857600))
    tasks = {
        'provenance': lambda: reconcile(root),
        'claims': lambda: reconcile_claims(root, tc),
        'static': lambda: static_inspect(root),
        'ci': lambda: ci_inspect(root),
    }
    parts = run(tasks, jobs=jobs)
    prov = parts['provenance']['result'] if parts['provenance']['ok'] else {'status':'BLOCKED','error':parts['provenance']['error']}
    claims = parts['claims']['result'] if parts['claims']['ok'] else []
    static = parts['static']['result'] if parts['static']['ok'] else {'status':'BLOCKED','error':parts['static']['error']}
    ci = parts['ci']['result'] if parts['ci']['ok'] else {'status':'BLOCKED','error':parts['ci']['error']}
    integrity = manifest(root, include, exclude + ('artifacts/rustless/verification.json', 'artifacts/rustless/verification.md'))
    store = EvidenceStore()
    ev_inv = store.add('inventory', '.', Status.VERIFIED, 'filesystem inventory')
    ev_fix = store.add('fixture_inventory', 'fixtures', Status.VERIFIED, 'safe filesystem discovery', {'count': len(fix)})
    ev_int = store.add('sha256_manifest', '.', Status.VERIFIED, 'sha256', {'file_count': len(integrity['files'])})
    ev_prov = store.add('provenance', '.', Status(prov.get('status','PROVISIONAL')), 'provenance inspection')
    gates, overall = evaluate(tc, {'inventory':inv,'fixtures':fix,'provenance':prov,'static':static,'ci':ci})
    evidence = store.json()
    for g in gates:
        if g['id']=='RG-001': g['evidence']=[ev_inv]
        elif g['id']=='RG-002': g['evidence']=[ev_fix]
        elif g['id']=='RG-003': g['evidence']=[ev_prov]
        elif g['id']=='RG-004': g['evidence']=[ev_int]
    blockers = [g['reason'] for g in gates if g['status']=='BLOCKED' and g['required']]
    return {'schema':'rustless-verification-v1','repository':identity(root),'environment':{'python':sys.version.split()[0]},'toolchains':tc,'inventory':inv,'fixtures':fix,'integrity':integrity,'provenance':prov,'claims':claims,'static':static,'ci':ci,'checks':parts,'evidence':evidence,'gates':gates,'limitations':['Static inspection, fixture integrity, and claim reconciliation are not native execution evidence.','CI definitions are inspected but never executed by rustless.'],'blockers':sorted(set(blockers)),'summary':{'status':overall,'required_gate_count':sum(g['required'] for g in gates),'blocked_required_gate_count':len(blockers)}}


def main(argv=None):
    ap=argparse.ArgumentParser(prog='python -m tools.rustless')
    ap.add_argument('command', nargs='?', default='verify'); ap.add_argument('subcommand', nargs='?')
    ap.add_argument('--root'); ap.add_argument('--config'); ap.add_argument('--jobs', type=int); ap.add_argument('--output', default='artifacts/rustless/verification.json')
    ap.add_argument('--json', action='store_true'); ap.add_argument('--markdown', action='store_true'); ap.add_argument('--strict', action='store_true'); ap.add_argument('--verbose', action='store_true'); ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--fail-on', choices=[s.value for s in Status]); ap.add_argument('--include', action='append', default=[]); ap.add_argument('--exclude', action='append', default=[])
    args=ap.parse_args(argv); root=Path(args.root).resolve() if args.root else discover_root(); cfg=load_config(root,args.config); jobs=args.jobs or cfg.get('execution',{}).get('jobs',8)
    if args.command=='self-test':
        import unittest; return unittest.main(module=None, argv=['unittest','discover','-s','tests','-p','test_rustless.py'], exit=False).result.wasSuccessful() is False
    if args.command=='integrity' and args.subcommand=='create': create(root,Path(cfg['integrity']['manifest']),args.include,args.exclude); print('INTEGRITY MANIFEST: CREATED'); return 0
    if args.command=='integrity' and args.subcommand=='verify':
        changes=verify_integrity(root,Path(cfg['integrity']['manifest'])); print(json.dumps(changes,indent=2)); return 0 if not any(x[0] in ('ADDED','REMOVED','MODIFIED') for x in changes) else 3
    g=graph(root,cfg,jobs,args.include,args.exclude)
    if args.command in ('inventory','toolchain','fixtures','provenance','claims','static','ci'):
        key={'inventory':'inventory','toolchain':'toolchains','fixtures':'fixtures','provenance':'provenance','claims':'claims','static':'static','ci':'ci'}[args.command]; print(json.dumps(g[key],indent=2,ensure_ascii=False)); return 0
    if args.command in ('verify','report','gates'):
        write(g,args.output); print(json.dumps(g,indent=2,ensure_ascii=False) if args.json else f"FINAL STATUS: {g['summary']['status']}"); status=Status(g['summary']['status'])
        if args.fail_on and {Status.VERIFIED:0,Status.PARTIALLY_VERIFIED:1,Status.PROVISIONAL:2,Status.BLOCKED:3}[status] >= {Status.VERIFIED:0,Status.PARTIALLY_VERIFIED:1,Status.PROVISIONAL:2,Status.BLOCKED:3}[Status(args.fail_on)]: return 1 if args.strict else EXIT_CODES[status]
        return EXIT_CODES[status]
    ap.error('unknown command')

if __name__=='__main__': main()
