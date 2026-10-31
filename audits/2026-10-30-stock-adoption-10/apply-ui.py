from pathlib import Path
ROOT=Path.cwd()
def replace(p,a,b):
 f=ROOT/p;s=f.read_text(encoding='utf-8');assert a in s,(p,a);f.write_text(s.replace(a,b),encoding='utf-8',newline='\n')
replace('tools/estimation_calculation.py',
"funding=[m for m in registry['mechanisms'] if m['id'] in {x['mechanism'] for x in specification['funding_claims']}]",
"funding=[dict(m,funding_mode=next(x['mode'] for x in specification['funding_claims'] if x['mechanism']==m['id'])) for m in registry['mechanisms'] if m['id'] in {x['mechanism'] for x in specification['funding_claims']}]")
replace('tools/retained_core.py',"    units = []\n    for original in validate()['units']:",
"    units = []\n    retained = validate()['units']\n    owner_labels = {u['id']:u['label'] for u in retained}\n    for original in retained:")
replace('tools/retained_core.py',"        for key in ('trace','funding','consolidation'): unit[key] = computed[key]",
"        for key in ('trace','funding','consolidation'): unit[key] = deepcopy(computed[key])\n        for mechanism in unit['funding']:\n            mechanism['funding_owner_label'] = owner_labels[mechanism['funding_owner']]")
replace('app/src/CoreEvaluationPage.tsx',
"<th>{L.candidate}</th><th>{L.effort}</th><th>{L.gap}</th>",
"<th>{L.candidate}</th><th>{L.common_effort}</th><th>{L.complement_effort}</th><th>{L.effort}</th><th>{L.gap}</th>")
replace('app/src/CoreEvaluationPage.tsx',"<th scope=\"row\">{r.label}</th><td>{n(r.jh,2)}",
"<th scope=\"row\">{r.label}</th><td>{r.common_jh==null?'—':n(r.common_jh,2)} {r.common_jh==null?'':L.jh_unit}</td><td>{r.complements_jh==null?'—':n(r.complements_jh,2)} {r.complements_jh==null?'':L.jh_unit}</td><td>{n(r.jh,2)}")
replace('app/src/CoreEvaluationPage.tsx',
"<li key={m.id}><strong>{m.label}</strong> — {m.note}</li>",
"<li key={m.id}><strong>{m.label}</strong> — {m.funding_mode==='consumed'?L.funding_consumed:L.funding_funded}. {L.funding_owner} : {m.funding_owner_label}. {m.note}</li>")
replace('app/src/CoreEvaluationPage.tsx',"  <p>{L.funding_owner} : {unit.label}</p>\n","")
replace('source/lecture-evaluations-economiques.yaml','**La famille Master Data Java/Spring est retenue, avec une répartition par rôle.**','**Les familles Master Data et Stock Java/Spring sont retenues, avec une répartition par rôle.**')
replace('source/lecture-evaluations-economiques.yaml','Le budget de la famille retenue inclut tous ses rôles et l’outillage de réalisation.','Le budget de chaque famille retenue inclut tous ses rôles et l’outillage de réalisation.')
replace('source/methode-evaluation-core.yaml','**Pour Master Data : ERPNext avec Frappe, Odoo, Tryton, Axelor avec Open Platform.**','**Pour les familles étudiées : ERPNext avec Frappe, Odoo, Tryton, Axelor avec Open Platform.**')
replace('source/methode-evaluation-core.yaml','      de code et les analogies restent distinctes des charges réellement observées.',
"""      de code et les analogies restent distinctes des charges réellement observées.
    - Pour une étude d’opportunité, les composants mêlant plusieurs responsabilités peuvent être dimensionnés par
      une part de pertinence supposée, avec un plancher de code métier mesuré et le retrait du patrimoine déjà
      financé. Les modules Flow nouveaux sont dimensionnés par fractions explicites de chaînes ou composants
      natifs, puis les modèles, vues et configurations sont ajoutés séparément. Les sensibilités de ces hypothèses
      restent distinctes des probabilités de dépassement.""")
for p,a,b in [
 ('source/README.md','Le contrat métier unique','Le contrat métier unique'),
]:pass
for path in ['source/README.md','tools/README.md']:
 f=ROOT/path;s=f.read_text(encoding='utf-8')
 s+='\n\nLa préparation Stock suit le contrat de calcul distinct native_component_analogies_v1 : attribution des composants mixtes, déduction du code Master Data déjà financé, analogies de modules, modèles et vues. Le module tools/estimation_stock.py est appelé par estimation_preparation.py ; les formules restent dans source/fondamentaux.yaml. Les preuves enregistrées suffisent au calcul et au téléchargement, sans dépôt OSS local. Les consommateurs affichent le propriétaire du financement réutilisé.\n'
 f.write_text(s,encoding='utf-8',newline='\n')
print('Écrans et lectures alignés')
