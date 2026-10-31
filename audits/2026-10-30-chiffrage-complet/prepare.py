"""Prepare opportunity-estimate iterations from pinned native code; no effort calculated here."""
from pathlib import Path
from collections import defaultdict
import json,hashlib,importlib.util,re,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
PREV=ROOT/'audits/2026-10-30-familles-restantes';COMMON=ROOT/'audits/2026-10-30-mecanismes-partages-04'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=importlib.util.spec_from_file_location('common_counter',COMMON/'prepare.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 plan=read(PREV/'plan.json');spec4=read(COMMON/'specification.json');meas4=read(COMMON/'measurements.json')
 baseline=read(COMMON/'baseline.json')
 save(OUT/'baseline.json',dict(protected=baseline['protected'],units=baseline['units'],prior_common_sha256=sha(COMMON/'results.json'),prior_campaign_sha256=sha(PREV/'bilan.yaml')))
 save(OUT/'campaign.json',dict(scope='Core System Java/Spring, 88 capacités ; propositions, pas adoption automatique',stop_rule=dict(coverage=88,all_functions_costed_or_consumed=True,single_funding=True,same_native_counter=True,unrounded_total_change_limit_pct=5,material_family_change_limit_pct=10,two_different_reviews_required=True,no_unfunded_material_scope=True,not_probability=True),stages=[dict(iteration=5,purpose='Mesure harmonisée et compléments locaux complets'),dict(iteration=6,purpose='Revue des interactions et des composants de calcul partagés'),dict(iteration=7,purpose='Revue des garanties, du comptage fonctionnel et du financement'),dict(iteration=8,purpose='Audit indépendant et sensibilité ; poursuite si changement matériel')],authority='source/fondamentaux.yaml#estimation_model',global_schedule='Ne pas additionner les délais locaux ; calendrier de programme distinct.',no_changed_retained_decisions=True))
 repos=spec4['repos'];cache={};sources=[];families=[];exclusion=r'tax|vat|valuation|accounting|analytic|margin|wap|print|pdf|csv|migration|send.*mail'
 def get(repo,path):
  k=repo,path
  if k not in cache:cache[k]=m.load_file(repo,path,dict(repos=repos))
  return cache[k]
 # Explicit service work remains smaller than an execution system. Borrow schemas for full-family work except what the common registry already provides.
 schema_excludes={
 'orders':{'Order','OrderLine','OrderChange','OrderLink'},
 'goods-orders':{'GoodsServiceRequirement','GoodsServiceCommitment','GoodsServiceResult'},
 'workflow':{'ActivityDefinition','ProcessDefinition','ProcessInstance'},
 'human-work':{'HumanTask','WorkAssignment','WorkDeadline'},
 'supervision':{'ProcessIntervention','ProcessException','CaseEvent','CaseReadCut'},
 }
 extra_schemas={
 'orders':[('ConsignmentTerms','owner,holder,goods,authorizedQuantity,returnConditions,agreementVersion'),('ReturnResolution','orderLine,reason,disposition,creditOrReplacement,repairRef,remaining')],
 'workflow':[('ContextualComposition','caseRef,catalogVersion,contextCut,selectedActivities,constraints,decision'),('ReactiveDispatch','caseRef,eventRef,ruleVersion,actionRef,idempotencyKey,outcome')],
 'supervision':[('OperationalCaseView','caseRef,orderRefs,taskRefs,serviceRefs,knownAt,effectiveAt,remaining,causes')],
 'goods-orders':[],
 }
 rationale={
 'eligibility':'Restrictions à portée, dates, motif et explication ; les identités et droits sont consommés de Master Data.',
 'policies':'Politiques versionnées, validation et explication ; les recommandations de seuils sont financées dans optimisation.',
 'disposition':'Décisions de devenir et comparaison de valeur, pas exécution de contrôle ou réparation chez un prestataire.',
 'orders':'Variantes de consignation et résolution des retours, rapprochement ; cycle et filiation consommés de la part commune.',
 'master-plan':'Contributions et plans nets/scénarios/application ; les calculateurs spécialisés sont consommés sans reconstruction.',
 'plan-preparation':'Qualification et consommation de prévision, rapprochement demande/apports ; publication distincte du plan net.',
 'backlog':'Priorités, choix d’affectation et libération ; pas seconde réservation physique Stock.',
 'optimization':'Modèles d’objectifs et contraintes de cinq décisions, orchestration des calculateurs et justification ; noyaux de solveurs réutilisés.',
 'promising':'Promesses ATP/CTP et valorisation d’options ; lectures Stock et calendriers/capacité fournis ailleurs.',
 'service-planning':'Offres de capacité de service, sélection et plans de transport ; calendriers et solveurs disponibles consommés.',
 'coordination':'Dépendances métier, adaptation des engagements et libération des services ; ni moteur de workflow ni mouvements Stock reconstruits.',
 'assurance':'Faits opérationnels, variantes de rapprochement et vues ; reconnaissance commune consommée.',
 'goods-orders':'Douze contrats typés et leurs contrôles, pas douze moteurs ni WMS ni ateliers de production.',
 'transport-orders':'Instruction de déplacement et réservation autonome de capacité ; contrat commun de prestation consommé.',
 'customs':'Dossier de prestation douanière, contrôle des pièces et résultat ; pas moteur réglementaire ni connecteurs pays.',
 'financial-services':'Demandes et reconnaissance de facture/avoir/paiement/remboursement ; pas tenue comptable ni moteur fiscal ni passerelles bancaires.',
 'workflow':'Composition contextuelle, liaison aux contrats et adaptation réactive Flowable ; moteur BPMN/CMMN et minuteurs disponibles.',
 'human-work':'Résultat/formulaire contextualisé et critères métier d’affectation ; affectation native et échéances communes consommées.',
 'supervision':'Vue croisée explicable, limites de projection et rapprochement ; journal deux dates et interventions consommés.',
 'intelligence':'Reconstruction déterministe des traces, variantes/temps et indicateurs Supply ; pas nouveau studio BI ni apprentissage automatique.'
 }
 # Source kernels already provided by the stack or funded in Stock/Ownership may be analogues but are never new base construction.
 def provided(repo,path):
  return (repo in ('frappe','platform') or 'StockMove' in path or 'StockLocationLine' in path or path.endswith('stock_quant.py') or path.endswith('/shipment.py') or path.endswith('/stock.py') or 'workflow' in path.lower() or 'ir_cron' in path or 'trigger.py' in path or 'queue_' in path or 'modelsql.py' in path or 'mail_' in path or 'res.py'==Path(path).name)
 for f in plan['families']:
  slug=f['slug'];i2=read(PREV/slug/'entrees-2.json');i3=read(PREV/slug/'entrees-3.json')
  schemas=[x for x in i2['schemas'] if x['name'] not in schema_excludes.get(slug,set())]
  for name,fields in extra_schemas.get(slug,[]):schemas.append(dict(name=name,fields=fields.split(','),hypothesis='Structure de référence, pas spécification détaillée.'))
  bindings=[]
  for src in i3['source_measures']:
   file=get(src['repo'],src['path']);pattern=f['method_pattern']
   if slug=='intelligence':exclude=''
   else:exclude=exclusion
   atoms,methods=m.select(file,pattern,exclude)
   bindings.append(dict(repo=file['repo'],product=file['product'],path=file['path'],root_path=file['root_path'],sha256=file['sha256'],pattern=pattern,excluded_pattern=exclude,provided_kernel=provided(file['repo'],file['path']),atoms=atoms,methods=methods))
  # Original workflow references were purchasing cycles, not the real BPM application.
  if slug=='workflow':
   bindings=[]
   for b in meas4['bindings']:
    if b['mechanism']!='process-runtime' or b['kind']!='program':continue
    file=get(b['repo'],b['path']);a,mm=m.select(file,b['method_pattern'],spec4['exclusion_pattern'])
    bindings.append(dict(repo=file['repo'],product=file['product'],path=file['path'],root_path=file['root_path'],sha256=file['sha256'],pattern=b['method_pattern'],excluded_pattern=spec4['exclusion_pattern'],provided_kernel=True,atoms=a,methods=mm))
  if slug=='supervision':
   # Full ORM audit infrastructure is supplied. Only the projection/query is a new local behaviour.
   bindings=[]
   for src in read(PREV/'intelligence'/'entrees-3.json')['source_measures']:
    file=get(src['repo'],src['path']);a,mm=m.select(file,'query|select|group|report|count|aggregate|compute|analysis','')
    bindings.append(dict(repo=file['repo'],product=file['product'],path=file['path'],root_path=file['root_path'],sha256=file['sha256'],pattern='query|select|group|report|count|aggregate|compute|analysis',excluded_pattern='',provided_kernel=True,atoms=a,methods=mm))
  if slug=='customs':
   bindings=[]
   for repo,path in [('frappe','frappe/core/doctype/file/file.py'),('odoo','odoo/addons/base/models/ir_attachment.py'),('tryton','trytond/trytond/ir/attachment.py'),('axelor','axelor-quality/src/main/java/com/axelor/apps/quality/service/RequiredDocumentVersionServiceImpl.java'),('axelor','axelor-quality/src/main/java/com/axelor/apps/quality/service/RequiredDocumentStatusServiceImpl.java')]:
    file=get(repo,path);a,mm=m.select(file,'valid|check|document|version|status|attach|file|access|read|write|create|save|download','thumbnail|image|preview|encrypt|decrypt|base64')
    bindings.append(dict(repo=file['repo'],product=file['product'],path=file['path'],root_path=file['root_path'],sha256=file['sha256'],pattern='document and access validation',excluded_pattern='binary rendering and encryption',provided_kernel=True,atoms=a,methods=mm))
  if slug=='goods-orders':
   # Typed service descriptors are not twelve copies of the stock execution code.
   schemas=[dict(x,fields=x['fields']+['specificConditions','expectedProof']) for x in schemas if x['name'].startswith('service-order-')]
  entry=dict(id=f['id'],slug=slug,name=f['name'],capabilities=f['capabilities'],functions=[dict(capability=v['id'],native_name=v['source']['name'],functions=v['functions']) for v in f['native_capabilities']],scope=rationale[slug],schemas=schemas,extension_fraction=i2['new_complement_fraction'],extension_fraction_origin='Hypothèse itération 2 conservée ; aucun ajustement pour rapprocher les JH.',bindings=bindings,common_consumption=[x['mechanism'] for x in read(COMMON/'funding.json')['claims'] if x['family']==slug and 'mechanism' in x],local_module_id=slug+'-specific',quantity=1)
  if slug=='goods-orders':entry.update(quantity=12,extension_fraction=.25,quantity_reason='Douze validations/contrats spécialisés ; chaque validation estimée à un quart du composant de contrôle natif, cycle commun exclu.')
  if slug=='workflow':entry.update(quantity=2,quantity_reason='Deux nouvelles adaptations : composition contextuelle et déclenchement réactif métier ; moteurs disponibles.')
  families.append(entry)
 sources=[{k:v for k,v in x.items() if k not in ('atoms','methods','text')} for x in cache.values()]
 save(OUT/'source-catalog.json',dict(sources=sources,repos=repos,same_counter=spec4['metrics_ref'],native_code_unmodified=True))
 save(OUT/'iteration-05/inputs.json',dict(families=families,common_results_ref=(COMMON/'results.json').relative_to(ROOT).as_posix(),common_measurements_ref=(COMMON/'measurements.json').relative_to(ROOT).as_posix(),cocomo=i2['cocomo'],counter_ref=spec4['metrics_ref'],not_a_second_metamodel=True))
 save(OUT/'iteration-05/freeze.json',dict(inputs_sha256=sha(OUT/'iteration-05/inputs.json'),catalog_sha256=sha(OUT/'source-catalog.json'),before_effort=True))
 print(json.dumps(dict(families=len(families),capabilities=sum(len(x['capabilities']) for x in families),files=len(sources),functions=sum(len(v['functions']) for x in families for v in x['functions']),java_selection=[dict(family=f['slug'],methods=sum(len(b['methods']) for b in f['bindings'] if b['product']=='axelor'),units=sum(len(b['atoms']) for b in f['bindings'] if b['product']=='axelor')) for f in families]),ensure_ascii=False))
if __name__=='__main__':main()
