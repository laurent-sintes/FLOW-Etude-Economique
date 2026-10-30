from pathlib import Path
import sys,json,hashlib,time
from collections import Counter
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
import yaml
from validate_stacks import ROOT
from retained_core import validate
from model_context import model_session
out=Path(__file__).resolve().parent
def key(text):return hashlib.sha256(text.replace('\r\n','\n').encode()).hexdigest()
paths={}
for folder in ('source','sources','audits'):
    for p in (ROOT/folder).rglob('*'):
        if p.suffix in ('.json','.yaml','.yml') and p.is_file():
            try:paths[key(p.read_text(encoding='utf-8-sig'))]=p.relative_to(ROOT).as_posix()
            except (UnicodeError,OSError):pass
reports={};original=yaml.load;values={}
for mode in ('standalone','one_snapshot'):
    counts=Counter()
    def load(text,*args,**kwargs):
        counts[paths.get(key(text),'unknown')]+=1
        return original(text,*args,**kwargs)
    start=time.perf_counter()
    with patch('yaml.load',side_effect=load):
        if mode=='one_snapshot':
            with model_session():values[mode]=validate()
        else:values[mode]=validate()
    reports[mode]=dict(seconds=time.perf_counter()-start,parse_calls=sum(counts.values()),counts=dict(counts.most_common()))
assert values['standalone']==values['one_snapshot']
reports['identical_results']=True
(out/'validation-parses.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in reports.items() if k=='identical_results' or k in ()}))
for mode in ('standalone','one_snapshot'):print(mode,reports[mode]['parse_calls'],list(reports[mode]['counts'].items())[:6])
