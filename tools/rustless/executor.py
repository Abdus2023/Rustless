from concurrent.futures import ThreadPoolExecutor,as_completed

def run(tasks,jobs=8):
    out={}
    with ThreadPoolExecutor(max_workers=max(1,min(jobs,8))) as ex:
        fs={ex.submit(fn):name for name,fn in tasks.items()}
        for f in as_completed(fs):
            n=fs[f]
            try: out[n]={'ok':True,'result':f.result()}
            except Exception as e: out[n]={'ok':False,'error':f'{type(e).__name__}: {e}'}
    return {k:out[k] for k in sorted(out)}
