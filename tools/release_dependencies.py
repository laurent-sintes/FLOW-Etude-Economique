"""Initial-release sequencing hypotheses, independent of calendar and valuation."""
from copy import deepcopy
from pathlib import PurePosixPath
from jsonschema import Draft202012Validator
from validate_stacks import ROOT,read

SOURCE='source/dependances-release.yaml'
SCHEMA='source/schema-dependances-release.yaml'

def dependencies():
    doc=read(ROOT/SOURCE)
    return {SOURCE,SCHEMA,'tools/release_dependencies.py',*[p for c in doc['constraints'] for p in c['evidence_refs']]}

def require(condition,message):
    if not condition:raise ValueError('ERR_RELEASE_DEPENDENCY: '+message)

def project(document,organisation):
    doc=deepcopy(document)
    require(doc['phase_ref']=='acquisition','Only initial construction is covered')
    teams={t['id']:t for t in organisation['teams']}
    releases={r['id']:r for r in doc['releases']}
    require(len(releases)==len(doc['releases']),'Duplicate release')
    team_refs=[r['team_ref'] for r in releases.values()]
    expected={t['id'] for t in teams.values() if t['type']!='enabling'}
    require(len(team_refs)==len(set(team_refs)) and set(team_refs)==expected,'Initial product team coverage')
    require(set(doc['excluded_team_refs'])==set(teams)-expected,'Excluded team coverage')
    rows=next(p['rows'] for p in organisation['charge_dossier']['phases'] if p['id']=='acquisition')
    types={t['id']:t for t in organisation['team_types']}
    for release in releases.values():
        team=teams[release['team_ref']]
        contributions=[dict(work_unit_ref=row['id'],label=row['label'],jh=c['jh'],share_pct=c['share_pct'])
                       for row in rows if row['kind']=='core_build' for c in row['contributions'] if c['team_ref']==team['id'] and c['jh'] is not None]
        require(bool(contributions),'Release without funded construction')
        release.update(label=team['label'],type=team['type'],color=types[team['type']]['color'],jh=sum(c['jh'] for c in contributions),work_contributions=contributions)
    require(abs(sum(r['jh'] for r in releases.values())-sum(r['jh'] for r in rows if r['kind']=='core_build'))<1e-7,'Build contributions must reconcile')
    ids=set();keys=set();complete_graph={id:[] for id in releases}
    for c in doc['constraints']:
        source,target=c['provider_release_ref'],c['consumer_release_ref']
        require(c['id'] not in ids,'Duplicate constraint identity');ids.add(c['id'])
        require(source in releases and target in releases,'Unknown release reference')
        require(source!=target,'Self dependency')
        require(c['gate'] in ('start','production'),'Unknown dependency gate')
        require(type(c['threshold_pct']) is int and 0<c['threshold_pct']<=100,'Invalid threshold')
        require(c['assessment']=='sequencing_assumption','Unsubstantiated progress measurement')
        key=(source,target,c['gate']);require(key not in keys,'Duplicate dependency');keys.add(key)
        require(all(isinstance(c[k],str) and c[k].strip() for k in ('prerequisite','work_scope','justification')),'Missing concrete condition')
        require(bool(c['evidence_refs']),'Missing evidence')
        for path in c['evidence_refs']:
            p=PurePosixPath(path)
            require(not p.is_absolute() and '..' not in p.parts and p.parts[0] in ('source','sources','audits'),'Unsafe evidence path')
        c.update(provider_team_ref=releases[source]['team_ref'],consumer_team_ref=releases[target]['team_ref'],provider_label=releases[source]['label'],consumer_label=releases[target]['label'])
        if c['gate']=='production' and c['threshold_pct']==100:complete_graph[source].append(target)
    visiting=set();visited=set()
    def visit(node):
        require(node not in visiting,'Complete-release production cycle')
        if node in visited:return
        visiting.add(node)
        for target in complete_graph[node]:visit(target)
        visiting.remove(node);visited.add(node)
    for node in complete_graph:visit(node)
    return doc

def build_dependencies(organisation):
    doc=read(ROOT/SOURCE)
    Draft202012Validator(read(ROOT/SCHEMA)).validate(doc)
    result=project(doc,organisation)
    require(all((ROOT/p).is_file() for c in doc['constraints'] for p in c['evidence_refs']),'Missing evidence file')
    return result
