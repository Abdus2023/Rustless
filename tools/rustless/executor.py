from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

def run(tasks, jobs=8, timeout_seconds=120):
    names = sorted(tasks)
    limit = max(1, min(int(jobs), 8, len(names) or 1))
    out = {}
    with ThreadPoolExecutor(max_workers=limit) as ex:
        futures = {name: ex.submit(tasks[name]) for name in names}
        for name in names:
            f = futures[name]
            try:
                out[name] = {'ok': True, 'result': f.result(timeout=max(0.001, timeout_seconds))}
            except TimeoutError:
                f.cancel(); out[name] = {'ok': False, 'error': 'TimeoutError: task exceeded timeout'}
            except Exception as exc:
                out[name] = {'ok': False, 'error': f'{type(exc).__name__}: {exc}'}
    return out
