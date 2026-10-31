"""Final funding/naming review and frozen iteration 8, independent of effort convergence."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 d=read(OUT/'iteration-07/inputs.json')
 save(OUT/'iteration-07/analysis.json',dict(results_sha256=sha(OUT/'iteration-07/results.json'),decision='Dernière revue de financement et sensibilité avant arrêt éventuel',findings=[
 dict(id='R7-01',finding='Une collision de nom entre exigence opérationnelle et exigence de capacité rend leur financement ambigu.',action='Nommer CapacityServiceRequirement l’objet de planification ; conserver champs et charge, contrats reliés explicitement.'),
 dict(id='R7-02',finding='Chaque comportement nouveau a un module cible énuméré et un propriétaire. Le réemploi d’un analogue ne finance pas sa reconstruction.',action='Contrôler les registres de mécanismes et modules, les consommations et toutes les capacités sans doublon.'),
 dict(id='R7-03',finding='Le chiffrage reste fondé sur les tailles supposées des adaptations ; absence de bilan de projet pour calibrer la précision.',action='Calculer les impacts des hypothèses déterminantes en unités de code, sans percentile ni enveloppe probabiliste.'),
 dict(id='R7-04',finding='Le total partiel de 2 220 JH de l’itération 4 ne doit pas être additionné au nouveau chiffrage complet.',action='Réconcilier 1 940 JH adoptés et la part complémentaire complète ; les 280 JH communs sont absorbés.')
 ],no_changed_COCOMO_coefficients=True))
 for f in d['families']:
  if f['slug']=='service-planning':
   for s in f['schemas']:
    if s['name']=='ServiceRequirement':s['name']='CapacityServiceRequirement'
 d['interface_contracts']=[
 dict(from_module='CapacityServiceRequirement',to_module='ServiceRequirement',relationship='Exigence de capacité planifiée vers instruction opérationnelle autorisée ; objets distincts, référence et version conservées.'),
 dict(from_module='ServiceFact',to_module='CaseEvent',relationship='Fait reconnu référencé dans le journal du dossier ; le journal ne reconstruit pas son interprétation métier.'),
 dict(from_module='PromiseOption',to_module='SupplyAssignment',relationship='Possibilité calculée distincte d’un engagement ; demande d’affectation sous autorité.'),
 dict(from_module='PlanScenario',to_module='PlanApplication',relationship='Scénario sans effet opérationnel ; application explicite après contrôles de version.')]
 registry=read(ROOT/'audits/2026-10-30-mecanismes-partages-04/funding.json')
 family_to_unit={f:g['id'] for g in d['economic_units'] for f in g['families']}
 mechanisms=[dict(id=m['id'],family_owner=m['owner'],economic_owner=family_to_unit[m['owner']],scope=m['name'],mode='included_common_work',common_amount_not_added=True) for m in registry['mechanisms']]
 for f in d['families']:
  for i,name in enumerate(f['module_names']):
   mechanisms.append(dict(id=f['slug']+'-local-'+str(i+1),family_owner=f['slug'],economic_owner=family_to_unit[f['slug']],scope=name,mode='new_specific_module'))
  for x in f.get('additional_modules',[]):
   mechanisms.append(dict(id=x['id'],family_owner=f['slug'],economic_owner=family_to_unit[f['slug']],scope=x['basis'],mode='new_additional_module'))
 save(OUT/'iteration-08/funding.json',dict(mechanisms=mechanisms,existing_claims=registry['claims'],baseline_owners=['master-data','stock','ownership'],single_target_owner=True,proposed_not_active_registry=True))
 d['funding_registry_ref']='audits/2026-10-30-chiffrage-complet/iteration-08/funding.json'
 d['source_catalog_ref']='audits/2026-10-30-chiffrage-complet/iteration-06/source-catalog.json'
 save(OUT/'iteration-08/inputs.json',d)
 save(OUT/'iteration-08/freeze.json',dict(inputs_sha256=sha(OUT/'iteration-08/inputs.json'),funding_sha256=sha(OUT/'iteration-08/funding.json'),analysis7_sha256=sha(OUT/'iteration-07/analysis.json'),before_effort=True))
 print('Iteration 8 inputs frozen; all target modules have one owner.')
if __name__=='__main__':main()
