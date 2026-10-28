"""Compact canonical transport and one current, autonomous release."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile

FORMAT = 1
ENGINE_FILES = ('project_investment.py','composable_costs.py','calculate_costs.py','study_app.py','market_oss.py',
                'model_inputs.py','business_calibration.py','buy_qualification.py','model_context.py','validate_stacks.py','content_model.py','core_method.py','architecture_model.py','fundamentals_model.py','framework_vision.py','framework_parameters.py','application_framework.py','economic_reading.py','evaluation_status.py','analyze_cost_references.py','core_qualification.py','market_instruction.py','market_reading.py','study_snapshot.py')
def digest(raw): return hashlib.sha256(raw).hexdigest()
def encode(value): return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')
def engine_revision():
    folder=Path(__file__).resolve().parent
    return digest(b''.join((folder/name).read_bytes() for name in ENGINE_FILES))

def pack_content(content):
    result=deepcopy(content)
    nodes={}
    for row in result['business_map']['rows']:
        for key in ('capacite','hierarchie','variantes'):
            items=[row[key]] if key=='capacite' else row[key]
            for node in items:
                if node['id'] in nodes and nodes[node['id']]!=node:
                    raise ValueError('Conflicting business node: '+node['id'])
                nodes[node['id']]=node
            row[key]=items[0]['id'] if key=='capacite' else [n['id'] for n in items]
    result['business_map']['nodes']=nodes
    result['complexity'].pop('rows')
    result['transport_format']=FORMAT
    return result

def unpack_content(content):
    result=deepcopy(content)
    if result.pop('transport_format',None)!=FORMAT: raise ValueError('Unsupported content format')
    nodes=result['business_map'].pop('nodes')
    for row in result['business_map']['rows']:
        row['capacite']=nodes[row['capacite']]
        row['hierarchie']=[nodes[i] for i in row['hierarchie']]
        row['variantes']=[nodes[i] for i in row['variantes']]
    result['complexity']['rows']=result['business_map']['rows']
    return result

def candidate(study):
    from validate_stacks import ROOT
    for path,expected in study.source_digests.items():
        if digest(Path(path).read_bytes())!=expected:
            raise ValueError('Draft changed since loading: '+path)
    documents={}
    for path in sorted(study.files):
        file=ROOT/path
        if not file.is_file(): continue
        raw=file.read_bytes()
        documents[path]=dict(sha256=digest(raw))
        if file.suffix in ('.yaml','.md','.py'):
            documents[path]['text']=raw.decode('utf-8-sig')
    payload=deepcopy(dict(data=study.data,economic=study.economic,ui=study.ui,architecture=study.architecture,fundamentals=study.fundamentals,
                 content=pack_content(study.content),baseline=study.baseline,
                 parameters=study.parameters,version=study.version,
                 simulation_contract=study.simulation_contract(),engine_revision=engine_revision(),documents=documents))
    return dict(format=FORMAT,created_at=datetime.now(timezone.utc).isoformat(),
                sha256=digest(encode(payload)),payload=payload)

def publish(bundle, path):
    """Single-file atomic replacement; failure leaves the previous release intact."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    validate_bundle(bundle)
    fd,temporary=tempfile.mkstemp(prefix='.candidate-',suffix='.json',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as stream:
            stream.write(encode(bundle));stream.flush();os.fsync(stream.fileno())
        os.replace(temporary,path)
    finally:
        if os.path.exists(temporary):os.unlink(temporary)

def validate_bundle(bundle):
    if bundle.get('format')!=FORMAT or digest(encode(bundle['payload']))!=bundle['sha256']:
        raise ValueError('Invalid release snapshot')
    return bundle

def load(path):
    return validate_bundle(json.loads(Path(path).read_text(encoding='utf-8')))
