from __future__ import annotations

import multiprocessing as mp
import queue
import time
from typing import Callable


def _worker(task, out_queue):
    try:
        out_queue.put((True, task(), ""))
    except BaseException as exc:
        out_queue.put((False, None, f"{type(exc).__name__}: {exc}"))


def _run_one(task: Callable[[], object], timeout_seconds: float):
    # fork preserves the existing callable-based API on POSIX while giving us a
    # real process boundary. spawn is used where fork is unavailable.
    methods = mp.get_all_start_methods()
    method = "fork" if "fork" in methods else "spawn"
    ctx = mp.get_context(method)
    out_queue = ctx.Queue(maxsize=1)
    process = ctx.Process(target=_worker, args=(task, out_queue), daemon=True)
    process.start()
    deadline = time.monotonic() + max(0.001, timeout_seconds)
    try:
        while time.monotonic() < deadline:
            remaining = max(0.001, deadline - time.monotonic())
            try:
                ok, result, error = out_queue.get(timeout=min(0.05, remaining))
                process.join(timeout=0.1)
                return {"ok": ok, "result": result} if ok else {"ok": False, "error": error}
            except queue.Empty:
                if not process.is_alive():
                    break
        if process.is_alive():
            process.terminate()
            process.join(timeout=1.0)
            if process.is_alive() and hasattr(process, "kill"):
                process.kill()
                process.join(timeout=1.0)
        return {"ok": False, "error": "TimeoutError: task exceeded timeout"}
    finally:
        try:
            out_queue.close()
            out_queue.join_thread()
        except (OSError, ValueError):
            pass


def run(tasks, jobs=8, timeout_seconds=120):
    """Run independent callables with bounded process isolation.

    ``jobs`` bounds concurrently running processes. Each task has a hard
    timeout: a timed-out child is terminated and joined before its result is
    returned. Results are ordered by task name, independent of completion order.
    """
    names = sorted(tasks)
    limit = max(1, min(int(jobs), 8, len(names) or 1))
    pending = iter(names)
    active = {}
    out = {}

    while active or len(out) < len(names):
        while len(active) < limit:
            try:
                name = next(pending)
            except StopIteration:
                break
            process_result = _start_async(tasks[name], timeout_seconds)
            active[name] = process_result

        finished = []
        for name, state in list(active.items()):
            result = _poll(state)
            if result is not None:
                out[name] = result
                finished.append(name)
        for name in finished:
            active.pop(name, None)
        if active:
            time.sleep(0.01)

    return {name: out[name] for name in names}


def _start_async(task, timeout_seconds):
    methods = mp.get_all_start_methods()
    method = "fork" if "fork" in methods else "spawn"
    ctx = mp.get_context(method)
    q = ctx.Queue(maxsize=1)
    p = ctx.Process(target=_worker, args=(task, q), daemon=True)
    p.start()
    return {"process": p, "queue": q, "deadline": time.monotonic() + max(0.001, timeout_seconds)}


def _poll(state):
    p = state["process"]
    q = state["queue"]
    try:
        ok, result, error = q.get_nowait()
        p.join(timeout=0.1)
        q.close()
        q.join_thread()
        return {"ok": ok, "result": result} if ok else {"ok": False, "error": error}
    except queue.Empty:
        pass

    if time.monotonic() >= state["deadline"]:
        if p.is_alive():
            p.terminate()
            p.join(timeout=1.0)
            if p.is_alive() and hasattr(p, "kill"):
                p.kill()
                p.join(timeout=1.0)
        try:
            q.close()
            q.join_thread()
        except (OSError, ValueError):
            pass
        return {"ok": False, "error": "TimeoutError: task exceeded timeout"}

    if not p.is_alive():
        try:
            ok, result, error = q.get_nowait()
            return {"ok": ok, "result": result} if ok else {"ok": False, "error": error}
        except queue.Empty:
            return {"ok": False, "error": "Worker exited without a result"}
    return None
