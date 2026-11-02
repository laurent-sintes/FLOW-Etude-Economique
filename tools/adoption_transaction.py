"""Stage validated model changes, reject stale plans, and recover interrupted file transactions."""
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
import base64, hashlib, json, os, tempfile, uuid


def digest(raw): return hashlib.sha256(raw).hexdigest()
def encode(doc): return (json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode('utf-8')
def require(ok, message):
    if not ok: raise ValueError('ERR_ADOPTION_TRANSACTION: '+message)

def target(root, name):
    rel=PurePosixPath(name)
    require(isinstance(name,str) and '\\' not in name and not rel.is_absolute() and '..' not in rel.parts, 'Invalid relative path')
    allowed=(name.startswith('source/') and rel.suffix in ('.yaml','.yml')) or name=='config/publication.yaml' or (name.startswith('audits/') and rel.suffix in ('.json','.yaml','.yml','.md')) or name=='tools/fixtures/active-adoption.json'
    require(allowed,'Path is not an adoption document: '+name)
    path=(root/name).resolve();require(path.is_relative_to(root) and path!=root,'Path escapes project')
    return path

def atomic(path, raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,temp=tempfile.mkstemp(prefix='.adoption-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as stream: stream.write(raw);stream.flush();os.fsync(stream.fileno())
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)

@contextmanager
def lock(root):
    folder=root/'tmp/core-adoptions';folder.mkdir(parents=True,exist_ok=True)
    with (folder/'apply.lock').open('a+b') as stream:
        stream.seek(0,2)
        if stream.tell()==0:stream.write(b'0');stream.flush()
        stream.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as error:raise ValueError('ERR_ADOPTION_TRANSACTION: Another adoption holds the lock') from error
        try:yield
        finally:
            stream.seek(0)
            if os.name=='nt':msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(stream.fileno(),fcntl.LOCK_UN)

def seal(plan):return digest(encode({k:v for k,v in plan.items() if k!='sha256'}))
def create_plan(root, changes, inputs, summary, validation):
    root=Path(root).resolve();require(bool(validation.get('passed')),'Candidate is not validated')
    require(bool(changes),'Empty adoption')
    entries=[]
    for name,raw in changes.items():
        path=target(root,name);old=path.read_bytes() if path.exists() else None
        require(isinstance(raw,bytes),'Document must be encoded bytes')
        if old==raw:continue
        entries.append(dict(path=name,before=None if old is None else base64.b64encode(old).decode('ascii'),before_sha256=None if old is None else digest(old),after=base64.b64encode(raw).decode('ascii'),after_sha256=digest(raw)))
    require(bool(entries),'No files changed')
    plan=dict(format=1,id=uuid.uuid4().hex,root=str(root),summary=summary,inputs=inputs,entries=entries,validation=validation)
    plan['sha256']=seal(plan)
    folder=root/'tmp/core-adoptions'/plan['id'];folder.mkdir(parents=True)
    atomic(folder/'plan.json',encode(plan));return folder/'plan.json'

def load_plan(path):
    path=Path(path).resolve();plan=json.loads(path.read_text(encoding='utf-8'))
    require(plan.get('format')==1 and plan.get('sha256')==seal(plan),'Plan changed since validation')
    root=Path(plan['root']).resolve();require(path.is_relative_to(root/'tmp/core-adoptions'),'Plan is outside its project')
    names=set()
    for e in plan['entries']:
        target(root,e['path']);require(e['path'] not in names,'Duplicate target');names.add(e['path'])
        for key in ('before','after'):
            raw=None if e[key] is None else base64.b64decode(e[key],validate=True)
            require((None if raw is None else digest(raw))==e[key+'_sha256'],'Plan content mismatch')
    return plan,root

def verify_inputs(plan,root,after=False):
    expected=dict(plan['inputs'])
    expected.update({e['path']:e['after_sha256'] if after else e['before_sha256'] for e in plan['entries']})
    for name,sha in expected.items():
        p=(root/name).resolve();require(p.is_relative_to(root),'Input escapes project')
        actual=digest(p.read_bytes()) if p.is_file() else None
        require(actual==sha,'Stale input: '+name)

def _rollback(plan,root):
    # Check all targets first. Never overwrite another writer's contents.
    for e in plan['entries']:
        p=target(root,e['path']);current=digest(p.read_bytes()) if p.is_file() else None
        require(current in (e['before_sha256'],e['after_sha256']),'Recovery found foreign contents: '+e['path'])
    for e in reversed(plan['entries']):
        p=target(root,e['path'])
        if e['before'] is None:
            if p.exists():p.unlink()
        else:atomic(p,base64.b64decode(e['before']))

def apply(path,after_write=None):
    plan,root=load_plan(path);pending=root/'tmp/core-adoptions/pending.json';journal=Path(path).parent/'journal.json'
    with lock(root):
        require(not pending.exists(),'An interrupted adoption must be recovered first')
        verify_inputs(plan,root)
        record=dict(id=plan['id'],plan=str(Path(path).resolve()),plan_sha256=plan['sha256'],status='applying')
        atomic(journal,encode(record));atomic(pending,encode(record))
        try:
            for e in plan['entries']:
                # Refuse a concurrent edit immediately before each replacement.
                p=target(root,e['path']);current=digest(p.read_bytes()) if p.is_file() else None
                require(current==e['before_sha256'],'Concurrent target change: '+e['path'])
                atomic(p,base64.b64decode(e['after']))
                if after_write:after_write(e['path'])
            verify_inputs(plan,root,after=True)
            record['status']='committed';atomic(journal,encode(record));pending.unlink()
        except BaseException:
            _rollback(plan,root);record['status']='rolled_back';atomic(journal,encode(record));pending.unlink();raise
    return dict(status='committed',id=plan['id'],summary=plan['summary'],files=len(plan['entries']))

def recover(root):
    root=Path(root).resolve();pending=root/'tmp/core-adoptions/pending.json'
    with lock(root):
        require(pending.exists(),'No interrupted adoption')
        record=json.loads(pending.read_text(encoding='utf-8'));plan,bound=load_plan(record['plan'])
        require(root==bound and record['plan_sha256']==plan['sha256'],'Recovery plan does not match project')
        journal=Path(record['plan']).parent/'journal.json';state=json.loads(journal.read_text(encoding='utf-8'))
        if state['status']=='committed':verify_inputs(plan,root,after=True)
        else:_rollback(plan,root);state['status']='rolled_back';atomic(journal,encode(state))
        pending.unlink();return dict(status=state['status'],id=plan['id'])
