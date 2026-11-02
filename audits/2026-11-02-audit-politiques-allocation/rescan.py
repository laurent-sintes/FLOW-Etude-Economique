"""Rescan frozen OSS sources and re-estimate policy governance without adopting a budget."""
from pathlib import Path
import ast,base64,gzip,hashlib,importlib.util,json,os,re,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'tmp/model-deps'))
from validate_stacks import read
from estimation_calculation import calculate,formula,rounded
from retained_core import referenced_value
from core_product_estimate import apportioned

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
protected={str(p.relative_to(ROOT)):sha(p) for base in ('source','config') for p in (ROOT/base).glob('*.yaml')}
prof=load('audits/2026-10-30-audit-fonctions-transverses/proposal-inputs.json')
repos={k:prof['measurements']['repos'][k] for k in ('erpnext','odoo','tryton','axelor','studio')}
# Search all available code in these pinned local checkouts, with explicit exclusions.
pattern=re.compile(r'allocat|reserv|priorit|polic|quota|rule|condition|incompat|conflict',re.I)
scan={};skip={'.git','node_modules','dist','build','locale','locales','translations','tests','test','__pycache__','i18n','static','documentation','docs'}
if '--replay' in sys.argv:
    scan=json.loads((OUT/'results.json').read_text(encoding='utf-8'))['scan']
else:
    for repo,meta in repos.items():
        root=ROOT/meta['root'];examined=0;matched=[]
        for folder,dirs,files in os.walk(root):
            dirs[:]=[d for d in dirs if d not in skip]
            for name in files:
                p=Path(folder)/name
                if p.suffix not in ('.py','.java','.js','.xml','.json') or p.stat().st_size>2_000_000:continue
                text=p.read_text(encoding='utf-8-sig',errors='replace');examined+=1
                if pattern.search(p.name) or pattern.search(text):matched.append(str(p.relative_to(root)).replace('\\','/'))
        scan[repo]=dict(files_examined=examined,matching_files=matched,matching_count=len(matched),root=meta['root'],commit=meta['commit'],excluded_directories=sorted(skip))
s=importlib.util.spec_from_file_location('counter',ROOT/'audits/2026-10-30-master-data-natif/measure.py');counter=importlib.util.module_from_spec(s);s.loader.exec_module(counter)
files={
 'erpnext':['erpnext/accounts/doctype/pricing_rule/pricing_rule.py','erpnext/accounts/doctype/pricing_rule/utils.py','erpnext/accounts/doctype/pricing_rule/pricing_rule.js','erpnext/accounts/doctype/pricing_rule/pricing_rule.json','erpnext/accounts/doctype/promotional_scheme/promotional_scheme.py'],
 'odoo':['addons/product/models/product_pricelist.py','addons/product/models/product_pricelist_item.py'],
 'tryton':['modules/product_price_list/price_list.py','modules/account_statement_rule/account.py'],
 'axelor':['axelor-base/src/main/java/com/axelor/apps/base/service/pricing/PricingComputer.java','axelor-base/src/main/java/com/axelor/apps/base/service/pricing/PricingServiceImpl.java','axelor-base/src/main/java/com/axelor/apps/base/service/pricing/PricingGenericServiceImpl.java','axelor-base/src/main/resources/domains/PricingRule.xml','axelor-base/src/main/resources/views/PricingRule.xml']}
measures=[];archive={}
for repo,paths in files.items():
 for rel in paths:
    p=ROOT/repos[repo]['root']/rel;key=repo+'/'+rel;raw=p.read_bytes();archive[key]=base64.b64encode(raw).decode()
    m=counter.measure(p);measures.append(dict(repo=repo,path=rel,commit=repos[repo]['commit'],sha256=sha(p),**m))
# Detailed functions replace the three generic policy processes, not the other two families.
# A group moves once per type and process. Brand/channel values do not multiply CFP.
processes=[]
def process(id,label,E,R,W,X,reason):
 processes.append(dict(id=id,label=label,E=E.split(),R=R.split(),W=W.split(),X=X.split(),scope_reason=reason))
process('strategy','Définir et réviser une stratégie','StrategyCommand','BusinessReferences Strategy Rights','Strategy Audit','Outcome','Commande métier propre à la stratégie, hors stockage générique de versions fourni par Master Data.')
process('scope','Configurer les bénéficiaires et périmètres','ScopeCommand','BusinessReferences ScopeHierarchy Rights','ScopeHierarchy Audit','Outcome Diagnostic','Hiérarchies marque, canal et usage. Pas une création des référentiels maîtres.')
process('protection','Configurer protections quotas et plafonds','ProtectionCommand','ScopeHierarchy Strategy Units Rights','ProtectionRules Audit','Outcome','Définitions de droits collectifs. Les compteurs de consommation et réservations restent dans Stock.')
process('priority','Configurer priorités et marges de réarbitrage','PriorityCommand','Strategy ScopeHierarchy Rights','PriorityRules Audit','Outcome Diagnostic','Définition des règles. Le calcul d’affectation reste dans le lot décisions.')
process('exceptions','Configurer les dérogations autorisées','ExceptionCommand','Strategy Rights Authorities','ExceptionRules Audit','Outcome','Catalogue de dérogations métier. Le moteur de tâches et d’approbation est consommé.')
process('validate','Contrôler les paramètres et leurs combinaisons','ValidationRequest','Strategy ScopeHierarchy ProtectionRules PriorityRules ExceptionRules','ValidationReport','Diagnostic','Contrôle de types, périodes, unités et combinaisons autorisées, distinct de l’enregistrement des brouillons.')
process('conflicts','Détecter les incompatibilités entre politiques','ConflictCheckRequest','PolicySet ScopeHierarchy ProtectionRules PriorityRules ExceptionRules','ConflictReport','ConflictReport Counterexample','Analyse croisée des priorités, chevauchements et protections sous un langage de règles borné. Pas preuve formelle de tout programme arbitraire.')
process('commitments','Contrôler la compatibilité avec les engagements','ImpactRequest','CandidatePolicy ActivePolicy StockCommitments Assignments Rights','ImpactReport','ImpactReport Rejections','Interrogation des moteurs existants et interprétation métier de l’impact. Pas second moteur Stock ni second solveur.')
process('tests','Exécuter un jeu de tests de politique','TestRunRequest','PolicyVersion TestCases ExpectedOutcomes Rights','TestRun TestResults','TestResults','Jeux de cas de règles. Réutilisation des calculs de plan, promesse et réservation, sans refaire leur simulation.')
process('activate','Planifier et autoriser une activation','ActivationCommand','PolicyVersion ValidationReport ConflictReport ImpactReport Rights','PolicyActivation Audit','Outcome','Remplace le processus initial d’activation. Master Data conserve les versions et Process Management les approbations.')
process('resolve','Résoudre les règles applicables à un contexte','PolicyQuery','ActivePolicy ScopeHierarchy ProtectionRules PriorityRules ExceptionRules','PolicyResolution','ApplicableRules','Service de résolution pour les consommateurs. Il ne choisit pas l’affectation ni ne réserve la ressource.')
process('explain','Expliquer une règle appliquée ou écartée','ExplanationQuery','PolicyResolution PolicyVersion Audit','PolicyExplanation','Explanation','Remplace l’explication générique initiale avec raisons des choix et conflits.')
process('withdraw','Suspendre ou retirer une politique','WithdrawalCommand','PolicyActivation StockCommitments Assignments Rights','PolicyActivation Audit','Outcome','Contrôle métier du retrait. La sauvegarde et le retour technique de version restent fournis.')
basepath='audits/2026-10-30-chiffrage-complet/iteration-07/cosmic-controls.json';old=load(basepath)
kept=[p for p in old['processes'] if 'BC-008' not in p['capabilities']]
old_policy=[p for p in old['processes'] if 'BC-008' in p['capabilities']]
kept_cfp=sum(len(p['movements']) for p in kept);removed=sum(len(p['movements']) for p in old_policy)
new_cfp=sum(len(p[k]) for p in processes for k in ('E','R','W','X'))
assert (kept_cfp,removed)==(47,17)
for p in processes:
 for k in ('E','R','W','X'):assert len(p[k])==len(set(p[k]))
 assert p['E'] and (p['W'] or p['X'])
u=next(u for u in read(ROOT/'source/estimations-core-retenues.yaml')['units'] if u['id']=='supply-controls-java-spring')
r=calculate(u['calculation']);assert r['total_jh']==50
benchmark={k:old[k] for k in ('hours_per_CFP','factor','day_hours')}
raw=formula('cosmic_effort',CFP=kept_cfp+new_cfp,**benchmark);candidate=rounded(raw,10)
roles=apportioned(candidate,{x['id']:x['jh'] for x in u['roles']})
role_rows=[dict(id=x['id'],label=x['label'],jh=roles[x['id']],rate=referenced_value(x['rate_ref'])) for x in u['roles']]
# Use the same canonical tooling owner as the active economic engine.
from retained_core import value_units
tooling=read(ROOT/'source/calibration-couts.yaml')['couts_communs']['outillage_realisation_eur_par_jh']
valued=next(x for x in value_units('java-spring',[],tooling) if x['id']==u['id'])
cost=round(sum(x['jh']*x['rate'] for x in role_rows)+candidate*tooling,2)
# These deliberately generous whole-component sizes still lack full FLOW functional matching.
# They are diagnostic transpositions, not alternative complete product budgets.
c=load('audits/2026-11-01-arbitrage-references-oss/results.json')['units']
c=next(x['cocomo'] for x in c if x['id']==u['id']);E=formula('cocomo_exponent',B=c['B'],SF_sum=c['SF_sum'])
diagnostics=[]
for repo in files:
 bank=sum(m['program_units']+m['declarative_units'] for m in measures if m['repo']==repo)
 size=133.75+294.35+77+bank
 effort=formula('cocomo_effort',A=c['A'],KSLOC=size/1000,E=E,EM=c['other_EM'],SCED=c['SCED'],month_hours=c['month_hours'],day_hours=c['day_hours'],effort_phase_factor=c['effort_phase_factor'])
 diagnostics.append(dict(repo=repo,bank_units=bank,diagnostic_equivalent_units=size,diagnostic_jh=effort,status='partial_functional_analogue_not_retained',matching='Configuration et évaluation de règles dans un autre domaine. Couverture des droits de ressources et contrôles croisés FLOW non démontrée. Aucune moyenne avec COSMIC.'))
result=dict(version=1,id='policy-governance-rescan-2026-11-02',status='proposal_not_adopted',unit_id=u['id'],date='2026-11-02',baseline_jh=50,baseline_cost_eur_ht=valued['cost_eur_ht'],baseline_CFP=64,replaced_policy_CFP=removed,kept_CFP=kept_cfp,policy_CFP=new_cfp,total_CFP=kept_cfp+new_cfp,benchmark=benchmark,raw_jh=raw,rounding_jh=10,proposal_jh=candidate,delta_jh=candidate-50,proposal_cost_eur_ht=cost,delta_cost_eur_ht=cost-valued['cost_eur_ht'],roles=role_rows,tooling_eur_jh=tooling,core_total_before_jh=5950,core_total_candidate_jh=5950-50+candidate,processes=processes,removed_process_ids=[p['id'] for p in old_policy],kept_process_ids=[p['id'] for p in kept],old_component_allocations=r['trace']['component_allocations'],cocomo_diagnostics=diagnostics,measures=measures,repositories=repos,scan=scan,cocomo_parameters=c,source_archive=dict(encoding='gzip-base64-json-base64-files',data=base64.b64encode(gzip.compress(json.dumps(archive).encode())).decode()),inputs_sha256={basepath:sha(ROOT/basepath),'source/estimations-core-retenues.yaml':sha(ROOT/'source/estimations-core-retenues.yaml'),'audits/2026-10-30-audit-fonctions-transverses/proposal-inputs.json':sha(ROOT/'audits/2026-10-30-audit-fonctions-transverses/proposal-inputs.json')},assessment='COSMIC retenu pour cette proposition car les analogues OSS rescannés ne démontrent pas le périmètre complet. Le rendement historique à 20 h/CFP reste une hypothèse non calibrée sur FLOW. Les processus sont une spécification prévisionnelle, pas une mesure certifiée.',scope_exclusions=['Calcul des protections et optimisation dans le lot décisions','Compteurs et consommation des réservations dans Stock','Versions génériques et référentiels dans Master Data','Éditeurs génériques et approbations dans Process Management','Saisie des politiques réelles du Groupe, interfaces et migration dans intégration','Langage de règles arbitraire et preuve formelle générale des incompatibilités'],sensitivity=[])
for rate in (15,25):result['sensitivity'].append(dict(hours_per_CFP=rate,jh=formula('cosmic_effort',CFP=result['total_CFP'],hours_per_CFP=rate,factor=1,day_hours=7),status='hypothese_de_rendement_non_intervalle_statistique'))
assert all(sha(ROOT/p)==v for p,v in protected.items()),'Active source changed during rescan'
result['market_sources']=json.loads((OUT/'market-sources.json').read_text(encoding='utf-8'))
for name in ('source/calibration-couts.yaml','audits/2026-11-02-audit-politiques-allocation/rescan.py','audits/2026-11-02-audit-politiques-allocation/market-sources.json'):
    result['inputs_sha256'][name]=sha(ROOT/name)
save('results.json',result)
print(json.dumps({k:result[k] for k in ('policy_CFP','total_CFP','raw_jh','proposal_jh','delta_jh','baseline_cost_eur_ht','proposal_cost_eur_ht','delta_cost_eur_ht','core_total_candidate_jh')},ensure_ascii=False))
print(json.dumps({k:dict(examined=v['files_examined'],matches=v['matching_count']) for k,v in scan.items()}))
