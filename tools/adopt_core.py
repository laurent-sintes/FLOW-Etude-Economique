"""One entry point for preparing, validating and applying adopted Core estimates."""
from pathlib import Path
from copy import deepcopy
from collections import Counter
import argparse,json,os,shutil,subprocess,sys,uuid,time
from adoption_transaction import create_plan,apply,recover,encode,digest,require
from validate_stacks import ROOT,read
from model_context import model_session
from core_adoption_reference import build_reference,raw_json,POINTER
from model_revision import next_revision
from core_product_estimate import apportioned
from estimation_calculation import formula,rounded
from estimation_preparation import prepare
from estimation_inputs import load_proofs,digest as scope_digest

SOURCES=('source/estimations-core-retenues.yaml','source/calculs-estimation-core.yaml','source/fonctions-produit-core.yaml','source/proposition-produit-core.yaml','source/evaluation-charges-brutes.yaml','source/version-modele.yaml','config/publication.yaml')

def yaml_bytes(doc):
    import yaml
    return yaml.safe_dump(doc,allow_unicode=True,sort_keys=False,width=110).encode('utf-8')

def describe(study):
    units=next(o['core_units'] for o in study.economic['options'] if o['stack']=='java-spring')
    return dict(total_jh=sum(u['total_jh'] for u in units),cost_eur_ht=sum(u['cost_eur_ht'] for u in units),units={u['id']:dict(jh=u['total_jh'],roles={r['id']:r['jh'] for r in u['roles']},rates={r['id']:r['rate_eur_jh'] for r in u['roles']},method=u['method']) for u in units})

def template(study):
    allocations={a['unit_id']:a for a in read(ROOT/'source/fonctions-produit-core.yaml')['allocations']};rows=[]
    for u in next(o['core_units'] for o in study.economic['options'] if o['stack']=='java-spring'):
        work=u['trace'].get('work_package_adoption',{}).get('work')
        if work:rows.append(dict(id=u['id'],label=u['label'],work=deepcopy(work),purpose_totals={x['purpose_id']:sum(x['jh_by_role'].values()) for x in allocations[u['id']]['shares']},purpose_basis=allocations[u['id']]['basis']))
    return dict(format=1,method='work_packages',date=study.model_revision['date'],units=rows)

def validate_proposal(doc,study,registry,documents):
    require(isinstance(doc,dict) and set(doc)=={'format','method','date','units'} and doc['format']==1 and doc['method']=='work_packages','Expected a work_packages proposal')
    next_revision(read(ROOT/'source/version-modele.yaml'),doc['date'])
    units={u['id']:u for u in next(o['core_units'] for o in study.economic['options'] if o['stack']=='java-spring')}
    allocations={a['unit_id']:a for a in read(ROOT/'source/fonctions-produit-core.yaml')['allocations']}
    known=set()
    for c in registry['calculations']:
        if c['recipe']=='work_package_adoption_v1':known.update(documents[c['inputs']['revision_proposal']]['scenario_ids'])
    require(bool(doc['units']) and len({u['id'] for u in doc['units']})==len(doc['units']),'Duplicate or empty proposed units')
    ids=set()
    for r in doc['units']:
        require(set(r)<= {'id','label','work','purpose_totals','purpose_basis'} and r['id'] in units,'Unknown proposed unit')
        require(bool(r.get('work')),'Empty work packages')
        owned={m['id'] for m in units[r['id']]['funding'] if m['funding_mode']=='funded'}
        for w in r['work']:
            require(set(w)=={'id','label','jh','scope','reuse','scenario_refs','funding_ref','effort_status'},'Unexpected work-package fields')
            require(w['id'] not in ids and type(w['jh']) is int and w['jh']>0,'Duplicate or invalid work-package effort');ids.add(w['id'])
            require(w['funding_ref'] in owned and w['effort_status']=='engineering_assumption_not_observed','Invalid funding or evidence status')
            require(w['scope'] and w['reuse'] and w['label'] and w['scenario_refs'] and set(w['scenario_refs'])<=known,'Missing boundary or unknown scenario')
        totals=r.get('purpose_totals')
        if totals is None:
            old={s['purpose_id']:sum(s['jh_by_role'].values()) for s in allocations[r['id']]['shares']};positive=[k for k,v in old.items() if v>0]
            require(len(positive)==1,'Mixed purpose requires explicit purpose_totals')
            totals={k:sum(w['jh'] for w in r['work']) if k==positive[0] else 0 for k in old};r['purpose_totals']=totals
        require(set(totals)=={'core-domain','support'} and all(type(v) is int and v>=0 for v in totals.values()) and sum(totals.values())==sum(w['jh'] for w in r['work']),'Purpose totals do not reconcile')
        require(bool(r.get('purpose_basis',allocations[r['id']]['basis'])),'Purpose allocation needs a basis')
    return units,allocations,known

def project(doc,study,registry,documents,note):
    require(isinstance(note,str) and bool(note.strip()),'Decision note required')
    doc=deepcopy(doc);valued,allocations,known=validate_proposal(doc,study,registry,documents)
    source={p:read(ROOT/p) for p in SOURCES};units=source[SOURCES[0]]['units'];selected={r['id']:r for r in doc['units']}
    unchanged=all(r['work']==valued[r['id']]['trace'].get('work_package_adoption',{}).get('work') and r['purpose_totals']=={s['purpose_id']:sum(s['jh_by_role'].values()) for s in allocations[r['id']]['shares']} for r in doc['units'])
    if unchanged:return None,dict(status='no_change',**describe(study))
    signature=digest(encode(dict(proposal=doc,registry=digest((ROOT/SOURCES[1]).read_bytes()))))[:16]
    folder='audits/'+doc['date']+'-adoption-core-'+signature
    require(not (ROOT/folder).exists(),'Immutable adoption directory already exists')
    new={}
    basis=dict(id='work-package-adoption-basis',registry=deepcopy(registry),units=deepcopy(units),input_hashes={p:v['sha256'] for p,v in registry['proofs'].items()})
    scope=dict(id='adopted-work-packages',status='adopted',date=doc['date'],units=doc['units'],scenario_ids=sorted(known))
    new[folder+'/basis.json']=encode(basis);new[folder+'/scope.json']=encode(scope)
    current_ref=source['source/proposition-produit-core.yaml']['adoption']['revision'];decision=deepcopy(read(ROOT/current_ref['path']))
    before=describe(study);after_jh=sum(sum(w['jh'] for w in selected[u['id']]['work']) if u['id'] in selected else u['total_jh'] for u in units)
    decision.update(id='core-adoption-'+signature,date=doc['date'],status='adopted',decision_status='adopted',user_decision=note,adopted_jh=before['total_jh'],proposal_jh=after_jh,delta_jh=after_jh-before['total_jh'],delta_pct=100*(after_jh/before['total_jh']-1),previous_cost_eur_ht=before['cost_eur_ht'],scope_change='Remplacement intégral des lots détaillés validés, avec conservation des financements et du référentiel natif.',inputs_sha256={p:digest(raw) for p,raw in new.items()})
    cost=0
    for u in units:
        old=valued[u['id']]
        if u['id'] not in selected:cost+=old['cost_eur_ht'];continue
        r=selected[u['id']];days=sum(w['jh'] for w in r['work']);roles=apportioned(days,{x['id']:x['jh'] for x in u['roles']})
        u.update(total_jh=days,method='Estimation détaillée par livrable',decision_date=doc['date'],role_assumption='Proportions antérieures conservées pour la valorisation des livrables validés.')
        for x in u['roles']:x['jh']=roles[x['id']]
        cost+=round(sum(roles[x['id']]*x['rate_eur_jh'] for x in old['roles'])+days*old['tooling_eur_jh'],2)
        c=next(c for c in registry['calculations'] if c['unit_id']==u['id']);p=prepare(documents,c,registry,formula,use_cache=True);cc=p['cocomo'];E=formula('cocomo_exponent',B=cc['B'],SF_sum=cc['SF_sum']);F=formula('schedule_exponent',D=cc['D'],E=E,B=cc['B']);months=formula('cocomo_schedule',C=cc['C'],JH=days,effort_phase_factor=cc['effort_phase_factor'],day_hours=cc['day_hours'],month_hours=cc['month_hours'],SCED=cc['SCED'],F=F,schedule_phase_factor=cc['schedule_phase_factor'])
        u['months']=rounded(months,p['allocation'].get('schedule_rounding_months',1));u['schedule']['unrounded_months']=months
        c['recipe']='work_package_adoption_v1';c['inputs']=dict(revision_basis=folder+'/basis.json',revision_proposal=folder+'/scope.json',revision_hypotheses=folder+'/decision.json')
        c['scope']['decision_scope_sha256']=scope_digest({k:u[k] for k in ('capabilities','includes','excludes')+(('professional_functions',) if 'professional_functions' in u else ())})
        a=next(a for a in source['source/fonctions-produit-core.yaml']['allocations'] if a['unit_id']==u['id']);support=apportioned(r['purpose_totals']['support'],roles)
        for share in a['shares']:share['jh_by_role']={k:support[k] if share['purpose_id']=='support' else v-support[k] for k,v in roles.items()}
        a['basis']=r.get('purpose_basis',a['basis']);a['evidence_refs'].append(folder+'/decision.json')
    decision['construction_cost_eur_ht']=round(cost,2)
    for row in decision['units']:
        row['adopted_jh']=valued[row['id']]['total_jh'];row['proposal_jh']=next(u['total_jh'] for u in units if u['id']==row['id']);row['delta_jh']=row['proposal_jh']-row['adopted_jh']
    for s in decision['sensitivity']:
        s['total_jh']=sum(rounded(formula('cosmic_effort',CFP=valued[u['id']]['trace']['CFP'],hours_per_CFP=s['value'],factor=1,day_hours=7),10) if u['method']=='COSMIC × ISBSG' else u['total_jh'] for u in units)
    new[folder+'/decision.json']=encode(decision);ref=dict(path=folder+'/decision.json',sha256=digest(new[folder+'/decision.json']))
    for u in units:
        if u['id'] in selected:u['provenance'].update(**ref,explanation='Adoption transactionnelle des livrables validés. Comparaisons antérieures conservées.')
    for name,raw in list(new.items()):
        value=json.loads(raw);dependencies=value.get('input_hashes',value.get('inputs_sha256',{}));registry['proofs'][name]=dict(sha256=digest(raw),kind='calculation_evidence',dependencies=[dict(path=p,sha256=h) for p,h in dependencies.items()])
    source[SOURCES[1]]=registry;source['source/proposition-produit-core.yaml']['adoption']['revision']=ref;source['source/evaluation-charges-brutes.yaml']['proposal']=dict(**ref,status='adopted')
    for id,r in selected.items():
        total=sum(w['jh'] for w in r['work']);analysis=source['source/evaluation-charges-brutes.yaml']['unit_analyses'][id];analysis['finding']=f"**{total} JH retenus pour {len(r['work'])} livrables détaillés.**"
    source['source/version-modele.yaml']=next_revision(source['source/version-modele.yaml'],doc['date'])
    text='# Adoption des estimations Core\n\nDécision : '+note+'\n\nEstimation retenue : '+str(after_jh)+' JH, '+str(round(cost,2))+' € HT. Les lots remplacent leurs anciens montants. Les autres lots, tarifs et calendriers sont conservés.\n'
    new[folder+'/audit.md']=text.encode('utf-8')
    source['config/publication.yaml']['documents'].extend(new)
    new.update({p:yaml_bytes(d) for p,d in source.items()})
    return new,dict(status='prepared',total_jh=after_jh,cost_eur_ht=round(cost,2),delta_jh=decision['delta_jh'],delta_cost_eur_ht=round(cost-before['cost_eur_ht'],2),decision=ref,proof_directory=folder,changed_units=list(selected),calendar='unchanged')


def project_contracts(doc,study,registry,documents,note):
    """Validate a declarative package using any already implemented calculation recipe."""
    from adoption_transaction import target
    require(set(doc)=={'format','method','date','decision_ref','documents'} and doc['format']==1 and doc['method']=='prepared_contracts','Invalid prepared-contract package')
    require(note and isinstance(doc['documents'],dict),'Decision note and documents required')
    require('source/version-modele.yaml' not in doc['documents'],'The revision is managed by the adoption command')
    changes={}
    for name,value in doc['documents'].items():
        target(ROOT.resolve(),name)
        if name.startswith('source/'):
            require(name in set(SOURCES)|{'source/statut-evaluation.yaml','source/methode-evaluation-core.yaml','source/complements-budgetaires.yaml','source/comparaison-solutions.yaml'},'Prepared package cannot change calibration, schemas or the native reference')
        raw=value.encode('utf-8') if name.endswith('.md') and isinstance(value,str) else encode(value) if name.endswith('.json') else yaml_bytes(value)
        if name in registry['proofs']:require(digest(raw)==registry['proofs'][name]['sha256'],'Historical calculation proof cannot be replaced')
        changes[name]=raw
    require(doc['decision_ref'] in changes,'Decision proof missing from package')
    decision=json.loads(changes[doc['decision_ref']]);before=describe(study)
    require(decision['status']==decision['decision_status']=='adopted' and decision['user_decision']==note and decision['date']==doc['date'],'Decision does not match the recorded validation')
    require(decision['adopted_jh']==before['total_jh'] and decision.get('previous_cost_eur_ht')==before['cost_eur_ht'],'Prepared package has a stale baseline')
    require('source/estimations-core-retenues.yaml' in doc['documents'],'Retained decisions missing')
    units=doc['documents']['source/estimations-core-retenues.yaml']['units'];old={u['id']:u for u in read(ROOT/'source/estimations-core-retenues.yaml')['units']}
    require(len(units)==len(old) and {u['id'] for u in units}==set(old),'Prepared package changes native unit identities')
    for u in units:require(u['capabilities']==old[u['id']]['capabilities'],'Prepared package changes the native scope')
    require(sum(u['total_jh'] for u in units)==decision['proposal_jh'],'Prepared package effort does not reconcile')
    for name,raw in changes.items():
        if (ROOT/name).is_file() and name.startswith('audits/'):require((ROOT/name).read_bytes()==raw,'Existing audit evidence is immutable')
    ref=dict(path=doc['decision_ref'],sha256=digest(changes[doc['decision_ref']]))
    for name in ('source/proposition-produit-core.yaml','source/evaluation-charges-brutes.yaml'):
        value=doc['documents'].get(name,read(ROOT/name))
        if name.endswith('proposition-produit-core.yaml'):value['adoption']['revision']=ref
        else:value['proposal']=dict(**ref,status='adopted')
        changes[name]=yaml_bytes(value)
    publication=doc['documents'].get('config/publication.yaml',read(ROOT/'config/publication.yaml'))
    for name in changes:
        if name not in publication['documents']:publication['documents'].append(name)
    changes['config/publication.yaml']=yaml_bytes(publication)
    changes['source/version-modele.yaml']=yaml_bytes(next_revision(read(ROOT/'source/version-modele.yaml'),doc['date']))
    return changes,dict(status='prepared',total_jh=decision['proposal_jh'],cost_eur_ht=decision['construction_cost_eur_ht'],delta_jh=decision['proposal_jh']-before['total_jh'],delta_cost_eur_ht=decision['construction_cost_eur_ht']-before['cost_eur_ht'],decision=dict(path=doc['decision_ref'],sha256=digest(changes[doc['decision_ref']])),proof_directory=Path(doc['decision_ref']).parent.as_posix(),changed_units=[u['id'] for u in units if u!=old[u['id']]],calendar='unchanged')


def refresh_reading(changes):
    """Keep summary prose free of duplicated active amounts or counts."""
    units=__import__('yaml').safe_load(changes['source/estimations-core-retenues.yaml'])['units']
    status=read(ROOT/'source/statut-evaluation.yaml')
    status['core']['producer']='Méthodes retenues par lot : '+', '.join(dict.fromkeys(u['method'] for u in units))
    status['core']['summary']='**Les estimations retenues sont intégrées au chiffrage.** Les hypothèses restent à confronter aux réalisations.'
    status['core']['text']='Les lots et leurs livrables sont décrits dans les charges brutes. Leurs mécanismes partagés sont financés une fois. Les règles et interfaces propres au Groupe relèvent de l’intégration. Le calendrier global et les garanties restent à confirmer.'
    changes['source/statut-evaluation.yaml']=yaml_bytes(status)
    for name,key in [('source/proposition-produit-core.yaml','reading'),('source/evaluation-charges-brutes.yaml','labels')]:
        doc=__import__('yaml').safe_load(changes[name])
        if key=='reading':doc[key]['grouping_note']='Le total additionne les décisions retenues après contrôle des financements. Les méthodes sont précisées par lot. Aucun volume de code intégré n’est déduit.'
        else:doc[key]['comparison_note']='Les méthodes retenues sont précisées par lot. Les références OSS et COSMIC des lots détaillés gardent leur périmètre antérieur. Ces montants ne s’additionnent pas.'
        changes[name]=yaml_bytes(doc)
    method=read(ROOT/'source/methode-evaluation-core.yaml')
    method['principle']['text']='**Cartographie des capacités → fonctions à réaliser → références et comptages → JH retenus.** Les calculs COCOMO II et COSMIC × ISBSG restent séparés. Les lots détaillés par livrable sont retenus par somme de leurs charges validées, avec déduction des mécanismes déjà financés.'
    changes['source/methode-evaluation-core.yaml']=yaml_bytes(method)


def materialize(stage,files,changes):
    stage=stage.resolve();require(stage.is_relative_to((ROOT/'tmp').resolve()),'Unsafe stage')
    for name in files:
        src=(ROOT/name).resolve();require(src.is_relative_to(ROOT.resolve()),'Staging source escapes project')
        if src.is_file():
            dst=stage/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    for p in (ROOT/'tools').glob('*.py'):
        dst=stage/'tools'/p.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
    for name,raw in changes.items():
        dst=stage/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw)


def prepare_adoption(proposal,note):
    from study_app import Study
    from estimation_inputs import _frozen_calculation_proofs
    started=time.perf_counter();timings={}
    with model_session() as snapshot:
        study=Study();timings['load']=time.perf_counter()-started
        registry=read(ROOT/SOURCES[1]);documents=_frozen_calculation_proofs(registry)
        changes,summary=(project_contracts if proposal.get('method')=='prepared_contracts' else project)(proposal,study,registry,documents,note)
        if changes is None:return dict(status='no_change',summary=summary,timings=timings)
        refresh_reading(changes)
        timings['projection']=time.perf_counter()-started-timings['load']
        inputs={p.relative_to(ROOT).as_posix():h for p,h in snapshot.digests.items()}
        files=set(study.files)|set(inputs)
        files.update(p.relative_to(ROOT).as_posix() for p in ROOT.iterdir() if p.is_file())
        for name in files:
            if (ROOT/name).is_file():inputs[name]=digest((ROOT/name).read_bytes())
        inputs[POINTER]=digest((ROOT/POINTER).read_bytes()) if (ROOT/POINTER).exists() else None
        before=deepcopy(study.baseline);before_record=dict(parameters=deepcopy(study.parameters),baseline=before)
    scratch=ROOT/'tmp/core-adoptions'/('candidate-'+uuid.uuid4().hex);stage=scratch/'workspace';stage.mkdir(parents=True)
    phase=time.perf_counter();materialize(stage,files,changes);out=scratch/'validated.json';before_path=scratch/'before.json';before_path.write_bytes(encode(before_record));timings['staging']=time.perf_counter()-phase
    env=dict(os.environ);env['PYTHONPATH']=os.pathsep.join([str(stage/'tools'),str(ROOT/'tmp/model-deps')]);env['PYTHONIOENCODING']='utf-8'
    phase=time.perf_counter();proc=subprocess.run([sys.executable,'-m','tools.adopt_core','_validate','--output',str(out),'--decision',summary['decision']['path'],'--before',str(before_path)],cwd=stage,env=env,capture_output=True,text=True,encoding='utf-8')
    timings['validation']=time.perf_counter()-phase
    require(proc.returncode==0,'Candidate validation failed: '+proc.stderr[-5000:])
    validated=json.loads(out.read_text(encoding='utf-8'));require(validated['summary']['total_jh']==summary['total_jh'] and abs(validated['summary']['cost_eur_ht']-summary['cost_eur_ht'])<.005,'Projection and engine differ')
    parameters=deepcopy(validated['baseline']['parameters']);parameters['options']['java-spring']['build']=before_record['parameters']['options']['java-spring']['build']
    require(parameters==before_record['parameters'],'Adoption changes parameters other than construction')
    previous_units=describe(study)['units']
    require({k:v['rates'] for k,v in validated['summary']['units'].items()}=={k:v['rates'] for k,v in previous_units.items()},'Adoption changes project rates')
    old={o['stack']:o for o in before['options']}
    for o in validated['baseline']['options']:
        if o['stack']!='java-spring':require(o==old[o['stack']],'Another option changed')
        else:
            for h,b in zip(o['horizons'],old[o['stack']]['horizons']):require(abs(h['totals']['total']-b['totals']['total']-summary['delta_cost_eur_ht']*h['build_progress'])<.01,'Budget delta does not reconcile')
    refname=summary['proof_directory']+'/test-reference.json';raw=raw_json(validated['reference']);changes[refname]=raw;changes[POINTER]=raw_json(dict(format=1,path=refname,sha256=digest(raw)))
    for name,sha in inputs.items():require((digest((ROOT/name).read_bytes()) if (ROOT/name).is_file() else None)==sha,'Sources changed during preparation: '+name)
    validation=dict(passed=True,options=5,horizons=20,workspace=str(stage),summary=validated['summary'])
    plan=create_plan(ROOT,changes,inputs,summary,validation)
    timings['total']=time.perf_counter()-started
    return dict(status='prepared',plan=str(plan),summary=summary,timings=timings)


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('template');p.add_argument('--output',type=Path,required=True)
    for name in ('prepare','run'):
        p=sub.add_parser(name);p.add_argument('--proposal',type=Path,required=True);p.add_argument('--decision-note',required=True)
        if name=='run':p.add_argument('--refresh',action='store_true',help='Build one local delivery after successful adoption')
    p=sub.add_parser('apply');p.add_argument('--plan',type=Path,required=True)
    sub.add_parser('recover')
    p=sub.add_parser('_validate');p.add_argument('--output',type=Path,required=True);p.add_argument('--decision',required=True);p.add_argument('--before',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='template':
        from study_app import Study
        require(not args.output.exists(),'Proposal file already exists');args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(encode(template(Study())));result=dict(status='template',path=str(args.output))
    elif args.command=='_validate':
        from study_app import Study
        s=Study();require(s.simulate(s.parameters)==s.baseline,'Baseline simulation differs')
        for o in s.baseline['options']:
            for h in o['horizons']:require(abs(sum(h['cost_natures'].values())-h['totals']['total'])<.01,'Unreconciled horizon')
        result=dict(summary=describe(s),baseline=s.baseline,reference=build_reference(s,args.decision,digest((ROOT/args.decision).read_bytes()),ROOT,before=read(args.before)));args.output.write_bytes(encode(result));return
    elif args.command in ('prepare','run'):
        result=prepare_adoption(read(args.proposal),args.decision_note)
        if args.command=='run' and result['status']=='prepared':result=apply(result['plan'])
        if args.command=='run' and args.refresh:
            from prepare_static_app import prepare as refresh
            try:result['delivery']=refresh()
            except Exception as error:
                result.update(status='committed_delivery_failed' if result['status']=='committed' else 'delivery_failed',delivery_error=str(error))
                print(json.dumps(result,ensure_ascii=False,indent=2));return 1
    elif args.command=='apply':result=apply(args.plan)
    else:result=recover(ROOT)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':sys.exit(main())
