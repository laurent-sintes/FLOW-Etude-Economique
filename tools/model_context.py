"""One isolated source snapshot per build, never a process-wide mutable cache."""
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from functools import wraps
import hashlib

CURRENT = ContextVar('flow_model_snapshot', default=None)

class SourceSnapshot:
    def __init__(self):
        self.documents = {}
        self.digests = {}
        self.memo = {}

    def read(self, path, loader):
        path = path.resolve()
        if path not in self.documents:
            raw = path.read_bytes()
            self.documents[path] = loader(raw.decode('utf-8-sig'))
            self.digests[path] = hashlib.sha256(raw).hexdigest()
        return deepcopy(self.documents[path])

    def verify(self):
        for path, digest in self.digests.items():
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError(f'Source changed during model loading: {path}')

@contextmanager
def model_session():
    existing = CURRENT.get()
    if existing is not None:
        yield existing
        return
    snapshot = SourceSnapshot()
    token = CURRENT.set(snapshot)
    try:
        yield snapshot
        snapshot.verify()
    finally:
        CURRENT.reset(token)

def scoped_model(fn):
    @wraps(fn)
    def run(*args, **kwargs):
        with model_session():
            return fn(*args, **kwargs)
    return run

def model_memo(fn):
    """Cache only default/identifier calls. Explicit test inputs always validate."""
    @wraps(fn)
    def run(*args, **kwargs):
        session = CURRENT.get()
        if session is None or kwargs or any(not isinstance(a, (str, type(None))) for a in args):
            return fn(*args, **kwargs)
        key = (fn.__module__, fn.__name__, args)
        if key not in session.memo:
            session.memo[key] = fn(*args, **kwargs)
        return deepcopy(session.memo[key])
    return run
