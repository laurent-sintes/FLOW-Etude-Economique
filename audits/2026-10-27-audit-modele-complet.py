"""Read-only model inventory and bounded dependency probes; writes only its audit JSON.

Run from the repository with tools and tmp/yaml-stacks/deps on PYTHONPATH.
No source changes, publication, cleanup, browser checks or full test suite.
"""
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
import os
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).with_suffix('.json')
SKIP = {'.git', 'node_modules', '__pycache__', '.venv', 'deps', 'python-deps', 'pythondeps', 'dist'}
TEXT = {'.yaml', '.md', '.py', '.mjs', '.ps1', '.json'}
started = time.perf_counter()
files = {}
texts = {}
duplicates = defaultdict(list)
for directory in ('source', 'config', 'sources', 'tools', 'archives', 'audits', 'output', 'outputs', 'release', 'tmp'):
    for base, dirs, names in os.walk(ROOT/directory, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP and not (Path(base)/d).is_symlink()]
        for name in names:
            path = Path(base)/name
            rel = path.relative_to(ROOT).as_posix()
            if path.is_symlink() or path in (Path(__file__), OUT) or name.startswith('2026-10-27-audit-modele-complet'):
                continue
            size = path.stat().st_size
            item = dict(bytes=size, family=directory)
            if directory != 'tmp' and size <= 32*1024*1024:
                raw = path.read_bytes()
                item['sha256'] = hashlib.sha256(raw).hexdigest()
                duplicates[item['sha256']].append(rel)
                if path.suffix in TEXT and directory != 'release' and size < 4*1024*1024:
                    texts[rel] = raw.decode('utf-8-sig', errors='replace')
            files[rel] = item
for name in ('AGENTS.md', 'README.md', 'app/README.md'):
    path = ROOT/name
    texts[name] = path.read_text(encoding='utf-8-sig')
    files[name] = dict(bytes=path.stat().st_size, family='documentation')

# Explicit path mentions, not a claim of exhaustive reachability (dynamic paths and relative links exist).
for target, item in files.items():
    if item['family'] not in ('tmp', 'release'):
        item['literal_consumers'] = [p for p, t in texts.items() if p != target and target in t]

from model_context import model_session
from validate_stacks import read
from project_investment import prepare, project
from composable_costs import initial_ledger
from calculate_costs import validate_inputs, SLUGS
from study_snapshot import engine_revision
from jsonschema import Draft202012Validator

result = dict(scope='Model, provenance and documentation. No application review.',
              exclusions=sorted(SKIP), inventory=files,
              directory_totals={k: dict(files=sum(i['family']==k for i in files.values()),
                      bytes=sum(i['bytes'] for i in files.values() if i['family']==k))
                  for k in sorted({i['family'] for i in files.values()})},
              exact_duplicates=[dict(sha256=h, paths=p) for h,p in duplicates.items() if len(p)>1],
              limitations=['Literal references are a lower bound, not deletion authorization.',
                          'Runtime/dependency folders excluded; tmp inventoried without hashing or reference extraction.',
                          'Files over 32 MiB are inventoried but not hashed.',
                          'Probes mutate copies in memory only; they test dependencies, not economic correctness.'])
with model_session() as session:
    data = prepare()
    projection = project(deepcopy(data))
    result['calculation_documents'] = sorted(p.relative_to(ROOT).as_posix() for p in session.documents)
    result['calculation_fingerprints'] = data['empreintes']
    result['hash_only_dependencies'] = sorted(set(data['empreintes'])-set(result['calculation_documents']))
    result['current_totals'] = {o['stack']:o['totaux_eur_ht'] for o in projection['options']}
    original = {s:read(ROOT/f'source/chiffrage/chiffrage-{s}.yaml') for s in SLUGS}
    result['legacy_core_rows'] = {s:len(d['core']) for s,d in original.items()}
    _, applied_before = validate_inputs()
    result['effective_core_rows'] = {s:len(d['core']) for s,d in applied_before.items()}
    for slug, doc in original.items():
        altered = deepcopy(doc)
        for row in altered['core']:
            row['jh_frontend_avant_ia'] *= 2
            row['jh_backend_avant_ia'] = {k:v*2 for k,v in row['jh_backend_avant_ia'].items()}
        session.documents[(ROOT/f'source/chiffrage/chiffrage-{slug}.yaml').resolve()] = altered
    _, applied_after = validate_inputs()
    result['probes'] = dict(double_195_legacy_core_rows=dict(effective_inputs_identical=applied_before==applied_after))
    for slug,doc in original.items():
        session.documents[(ROOT/f'source/chiffrage/chiffrage-{slug}.yaml').resolve()] = doc
    empty = deepcopy(original['java-spring']); empty['core'] = []
    errors = list(Draft202012Validator(read(ROOT/'source/schema-chiffrage.yaml')).iter_errors(empty))
    result['probes']['remove_legacy_core'] = [dict(path=list(e.path),message=e.message) for e in errors]

    option = next(o for o in data['options'] if o['stack']=='java-spring')
    ledger = initial_ledger(option, option['composable']['reference_services'])
    changes = [(['group','perimetre','utilisateurs'],1900),
               (['group','perimetre','unites_deploiement'],8),
               (['config','classification_make','MAI-001','responsabilite'],'mco_client'),
               (['config','hebergement_build','cas_central'],'soutenu')]
    for keys,value in changes:
        altered = deepcopy(option)
        node = altered['composable']['inputs']
        for key in keys[:-1]: node=node[key]
        before=node[keys[-1]];node[keys[-1]]=value
        after=initial_ledger(altered,altered['composable']['reference_services'])
        result['probes']['/'.join(keys)] = dict(before=before,after=value,ledger_identical=after==ledger)
    result['malformed_classification_key'] = read(ROOT/'source/modele-composable.yaml')['classification_make']['MAI-008']
    altered = deepcopy(option)
    altered['composable']['inputs']['group']['perimetre']['repartition_usagers_par_unite'] = [.25,.25,.25]
    try:
        short = initial_ledger(altered,altered['composable']['reference_services'])
        result['probes']['missing_deployment_share'] = dict(rejected=False,
            amount_difference_eur=round(sum(r['amount'] for r in short)-sum(r['amount'] for r in ledger),2))
    except Exception as error:
        result['probes']['missing_deployment_share'] = dict(rejected=True,error=str(error))
    result['legacy_document_registration'] = {
        p:(p in texts['AGENTS.md']) for p in ('source/core-system-features.yaml',
            'source/schema-core-system-features.yaml','source/schema-core-system-solution.yaml',
            'source/inflation.yaml','source/schema-inflation.yaml','tools/validate_stacks.py')}

release = json.loads((ROOT/'release/current.json').read_text(encoding='utf-8'))
payload = release['payload']
result['release'] = dict(id=release['sha256'][:12],created_at=release['created_at'],
                       engine_revision_matches=engine_revision()==payload['engine_revision'],
                       documents=len(payload['documents']),
                       historical_documents=[p for p in payload['documents'] if p.startswith(('archives/','audits/'))])
frozen_projection = project(deepcopy(payload['data']))
result['release']['projection_identical_to_draft'] = projection==frozen_projection
result['release']['totals_identical_to_draft'] = result['current_totals']=={o['stack']:o['totaux_eur_ht'] for o in frozen_projection['options']}
result['release']['changed_documents'] = [p for p,d in payload['documents'].items()
    if not (ROOT/p).is_file() or hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=d['sha256']]
result['release']['horizons_checked'] = [3,5,7,10]
result['release']['horizon_amount_differences'] = []
for current,frozen in zip(projection['options'],frozen_projection['options']):
    for horizon in (3,5,7,10):
        a=round(sum(y['total'] for y in current['annees'][:horizon]),2)
        b=round(sum(y['total'] for y in frozen['annees'][:horizon]),2)
        if a!=b:result['release']['horizon_amount_differences'].append(dict(stack=current['stack'],horizon=horizon,draft=a,release=b))
result['elapsed_seconds'] = round(time.perf_counter()-started,3)
result['duplicates_summary'] = dict(groups=len(result['exact_duplicates']),
    redundant_bytes=sum(files[p]['bytes'] for g in result['exact_duplicates'] for p in g['paths'][1:]))
for path,item in files.items():
    if path.startswith(('sources/client/','sources/cartographie-','sources/recalibration-')):
        action='preserve_evidence'
    elif path in result['calculation_documents'] or path in result['calculation_fingerprints']:
        action='active_dependency_do_not_remove'
    elif path.startswith('tools/flow_') or path in ('tools/audit_flow_workbook.log','tools/build_flow_estimate.log'):
        action='retire_legacy_excel_chain_after_reference_review'
    elif path.startswith(('output/','outputs/')):
        action='select_final_deliverables_then_remove_redundant_derivatives'
    elif path.startswith('archives/'):
        action='retain_cited_evidence_then_review_historical_working_copies'
    elif path.startswith('tmp/'):
        action='separate_runtime_from_disposable_work_before_cleanup'
    else:action='review_role_no_automatic_deletion'
    item['proposed_disposition']=action
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('inventory','calculation_fingerprints','exact_duplicates','calculation_documents')},ensure_ascii=False,indent=2))
