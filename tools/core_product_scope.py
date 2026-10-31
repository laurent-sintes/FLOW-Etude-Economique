"""Product purpose is independent of capability hierarchy and project roles; never invent missing effort."""
from copy import deepcopy
from collections import Counter
import hashlib,math
from jsonschema import Draft202012Validator
from validate_stacks import ROOT,read
from model_context import scoped_model,model_memo
from estimation_calculation import formula
from estimation_inputs import registry
from capability_catalog import analysis
from core_product_estimate import build_product_proposal,dependencies as proposal_dependencies

SOURCE='source/fonctions-produit-core.yaml'
SCHEMA='source/schema-fonctions-produit-core.yaml'
ERROR='ERR_CORE_PRODUCT_SCOPE:'
PURPOSES=('business-runtime','it-complement')
def require(value,message):
 if not value:raise ValueError(ERROR+message)
def dependencies():
 doc=read(ROOT/SOURCE)
 return {SOURCE,SCHEMA,doc['evidence']['path'],'tools/core_product_scope.py'}|proposal_dependencies()

@scoped_model
@model_memo
def load_scope():
 doc=read(ROOT/SOURCE);Draft202012Validator(read(ROOT/SCHEMA)).validate(doc)
 ref=doc['evidence'];path=(ROOT/ref['path']).resolve();require(path.is_relative_to(ROOT.resolve()),'evidence path')
 require(hashlib.sha256(path.read_bytes()).hexdigest()==ref['sha256'],'evidence changed')
 evidence=read(path);proofs=evidence['evidence'];known={m['id']:m for m in registry()['mechanisms']};caps={r['id'] for r in analysis()['blocs']}
 require({p['id'] for p in doc['purposes']}==set(PURPOSES),'purpose identities')
 ids=[f['id'] for f in doc['functions']];require(len(ids)==len(set(ids)),'duplicate product function')
 for f in doc['functions']:
  for key in ('capability_refs','depends_on','existing_funding_refs','evidence_refs'):require(len(f[key])==len(set(f[key])),'duplicate '+key)
  require(set(f['capability_refs'])<=caps,'native capability reference')
  require(set(f['depends_on'])<=set(ids) and f['id'] not in f['depends_on'],'function dependency')
  require(set(f['existing_funding_refs'])<=set(known),'funding reference')
  require(set(f['evidence_refs'])<=set(proofs),'code proof reference')
  require(f['additional_jh'] is None,'unadopted additional effort must stay unknown')
  # IT functions never invent native business capabilities.
  if f['purpose']=='it-complement':require(not f['capability_refs'],'IT function is not a native capability')
 result=deepcopy(doc)
 for f in result['functions']:
  f['market_evidence']=[{k:deepcopy(proofs[id][k]) for k in ('product','repository','commit','path','url','start_line','end_line','observation') if k in proofs[id]} for id in f['evidence_refs']]
  f['existing_funding']=[dict(id=id,label=known[id]['label'],owner=known[id]['funding_owner']) for id in f['existing_funding_refs']]
 result['evidence_summary']=dict(function_families=len(ids),themes_with_code=sum(bool(f['evidence_refs']) for f in doc['functions']),unique_source_files=len(proofs),prior_measured_files=sum(p['in_previous_measurements'] for p in proofs.values()),newly_inspected_files=sum(not p['in_previous_measurements'] for p in proofs.values()),by_product=dict(Counter(p['product'] for p in proofs.values())))
 return result

def partition(units,allocations):
 """Partition already adopted effort by explicit role amounts; unknown allocation is not zero scope."""
 index={u['id']:u for u in units};require(len(index)==len(units),'duplicate retained unit')
 ids=[a['unit_id'] for a in allocations];require(len(ids)==len(set(ids)),'duplicate allocation')
 require(set(ids)<=set(index),'allocation references unknown retained unit')
 totals={p:dict(known_jh=0.,known_eur_ht=0.) for p in PURPOSES};allocated=set();details=[]
 for a in allocations:
  require(bool(a['evidence_refs']) and bool(a.get('basis','')),'allocation requires evidence and basis')
  unit=index[a['unit_id']];roles={r['id']:r for r in unit['roles']};shares=a['shares']
  require(len(shares)==2 and {s['purpose_id'] for s in shares}==set(PURPOSES),'two purpose shares required')
  for share in shares:
   require(set(share['jh_by_role'])<=set(roles),'unknown role')
   for v in share['jh_by_role'].values():require(type(v) in (int,float) and math.isfinite(v) and v>=0,'invalid role effort')
  for id,r in roles.items():require(math.isclose(sum(s['jh_by_role'].get(id,0) for s in shares),r['jh'],abs_tol=1e-9),'role effort conservation')
  for share in shares:
   jh=sum(share['jh_by_role'].values());labour=sum(formula('role_price',JH=v,rate=roles[id]['rate_eur_jh']) for id,v in share['jh_by_role'].items());cost=round(labour+jh*unit['tooling_eur_jh'],2)
   target=totals[share['purpose_id']];target['known_jh']+=jh;target['known_eur_ht']+=cost
  allocated.add(unit['id']);details.append(deepcopy(a))
 adopted_jh=sum(u['total_jh'] for u in units);adopted_cost=round(sum(u['cost_eur_ht'] for u in units),2)
 unallocated_jh=formula('purpose_unallocated_jh',total=adopted_jh,business=totals[PURPOSES[0]]['known_jh'],it=totals[PURPOSES[1]]['known_jh'])
 unallocated_cost=round(formula('purpose_unallocated_cost',total=adopted_cost,business=totals[PURPOSES[0]]['known_eur_ht'],it=totals[PURPOSES[1]]['known_eur_ht']),2)
 expected_jh=sum(u['total_jh'] for id,u in index.items() if id not in allocated);expected_cost=round(sum(u['cost_eur_ht'] for id,u in index.items() if id not in allocated),2)
 require(math.isclose(unallocated_jh,expected_jh,abs_tol=1e-9) and abs(unallocated_cost-expected_cost)<0.005,'partition conservation')
 complete=bool(units) and len(allocated)==len(units)
 for value in totals.values():value.update(jh=value['known_jh'] if complete else None,eur_ht=round(value['known_eur_ht'],2) if complete else None)
 return dict(adopted_jh=adopted_jh,adopted_eur_ht=adopted_cost,purposes=totals,unallocated_jh=unallocated_jh,unallocated_eur_ht=unallocated_cost,partition_complete=complete,additional_required_jh=None,total_complete_product_jh=None,unit_count=len(units),allocated_units=len(allocated),allocations=details,status='partition_complete' if complete else 'partition_pending' if units else 'no_estimate')

def build_core_product_scope(economic):
 doc=load_scope();result=dict(reading=deepcopy(doc['reading']),purposes=deepcopy(doc['purposes']),functions=deepcopy(doc['functions']),evidence_summary=deepcopy(doc['evidence_summary']),options=[],source_ref=SOURCE)
 all_units={u['id'] for o in economic['options'] for u in o.get('core_units',[])};require({a['unit_id'] for a in doc['allocations']}<=all_units,'unknown adopted allocation')
 for o in economic['options']:
  if o['strategie']!='make':continue
  units=o['core_units'];ids={u['id'] for u in units};allocations=[a for a in doc['allocations'] if a['unit_id'] in ids];result['options'].append(dict(stack=o['stack'],name=o['nom'] if 'nom' in o else o['stack'],**partition(units,allocations)))
 result['proposal']=build_product_proposal(economic)
 require(result['proposal']['scope_functions']==len(result['functions']),'professional function coverage mismatch')
 return result
