"""Reproducible engineering challenge. Does not write any active model file."""
from pathlib import Path
from decimal import Decimal
from hashlib import sha256
import json, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import yaml
from core_product_estimate import apportioned
from calculate_costs import money_round
OUT=Path(__file__).resolve().parent
REL=OUT.relative_to(ROOT).as_posix()
def load(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
def digest(p): return sha256((ROOT/p).read_bytes()).hexdigest()
def calculate():
 inputs=load(REL+'/inputs.json')
 basis=load('audits/2026-11-02-adoption-perimetre-scenarios/basis.json')
 adopted=load('audits/2026-11-02-adoption-perimetre-scenarios/decision.json')
 active=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))
 units={u['id']:u for u in active['units'] if u['stack']=='java-spring'}
 valued={u['id']:u for u in basis['valued_units']}
 scenarios=load('audits/2026-11-02-revue-perimetre-scenarios/results.json')
 allowed={s['id'] for s in scenarios['scenarios']}
 seen=set();rows=[]
 for proposed in inputs['units']:
  old=units[proposed['id']];v=valued[old['id']]
  assert old['total_jh']==v['total_jh'] and [(r['id'],r['jh']) for r in old['roles']]==[(r['id'],r['jh']) for r in v['roles']]
  owners={m['id'] for m in v['funding'] if m['funding_owner']==old['id']}
  for w in proposed['work']:
   assert w['id'] not in seen; seen.add(w['id'])
   assert type(w['jh']) is int and w['jh']>0
   assert w['funding_ref'] in owners
   assert w['scenario_refs'] and set(w['scenario_refs'])<=allowed
   assert w['scope'] and w['reuse'] and w['effort_status']=='engineering_assumption_not_observed'
  total=sum(w['jh'] for w in proposed['work'])
  role_days=apportioned(total,{r['id']:r['jh'] for r in v['roles']})
  assert sum(role_days.values())==total
  labour=sum(Decimal(role_days[r['id']])*Decimal(str(r['rate_eur_jh'])) for r in v['roles'])
  tooling=Decimal(total)*Decimal(str(v['tooling_eur_jh']))
  cost=money_round(labour+tooling)
  rows.append(dict(id=old['id'],label=proposed['label'],adopted_jh=old['total_jh'],proposal_jh=total,delta_jh=total-old['total_jh'],adopted_cost_eur_ht=v['cost_eur_ht'],proposal_cost_eur_ht=cost,delta_cost_eur_ht=money_round(Decimal(str(cost))-Decimal(str(v['cost_eur_ht']))),roles=[dict(id=r['id'],label=r['label'],jh=role_days[r['id']],rate_eur_jh=r['rate_eur_jh']) for r in v['roles']],tooling_eur_jh=v['tooling_eur_jh'],comparisons=dict(cocomo_reference_jh=v['alignment']['reference_jh'],cosmic_jh=v['alignment']['functional']['jh'],CFP=v['trace']['CFP'],oss=[dict(id=r['id'],jh=r['jh']) for r in v['alignment']['rows']]),work=proposed['work']))
 assert len(rows)==len({r['id'] for r in rows})==4
 md=next(r for r in rows if r['id']=='master-data-java-spring')
 assert any(w['id']=='MD09' and w['jh']>0 for w in md['work'])
 refs=[REL+'/inputs.json',REL+'/calculate.py','source/estimations-core-retenues.yaml','source/version-modele.yaml','source/fondamentaux.yaml','source/calibration-couts.yaml','audits/2026-11-02-adoption-perimetre-scenarios/basis.json','audits/2026-11-02-adoption-perimetre-scenarios/decision.json','audits/2026-11-02-revue-perimetre-scenarios/results.json','audits/2026-10-30-audit-fonctions-transverses/proposal-inputs.json']
 adopted_total=sum(u['total_jh'] for u in units.values())
 assert adopted_total==adopted['proposal_jh']==7030
 delta=sum(r['delta_jh'] for r in rows);money_delta=money_round(sum(Decimal(str(r['delta_cost_eur_ht'])) for r in rows))
 return dict(id=inputs['id'],date=inputs['date'],status='proposal_not_adopted',method=inputs['method'],effort_basis=inputs['effort_basis'],units=rows,work_package_count=len(seen),adopted_jh=adopted_total,adopted_cost_eur_ht=adopted['construction_cost_eur_ht'],proposal_jh=adopted_total+delta,delta_jh=delta,delta_cost_eur_ht=money_delta,proposal_cost_eur_ht=money_round(Decimal(str(adopted['construction_cost_eur_ht']))+Decimal(str(money_delta))),native_capabilities=len({c['id'] for u in units.values() for c in u['capabilities']}),input_hashes={p:digest(p) for p in refs},checks=dict(unique_work_packages=True,scenario_refs_exist=True,funding_owner_preserved=True,roles_reconciled=True,correction_editing_included=True,active_budget_not_changed=True),economic_limits=['Aucun changement de budget actif, calendrier, intégration, fonctionnement ou Office FLOW.','La variation du total Core est conditionnelle au remplacement des quatre lots. Les autres lots restent inchangés.','Les JH sont des hypothèses détaillées d’ingénierie, pas des temps observés, un nouveau comptage COSMIC ou une nouvelle mesure COCOMO.','Les proportions de rôles et tarifs actifs servent à la valorisation. Elles ne constituent pas un plan de recrutement.','Pas de marge générale ni gain IA. Incertitude quantitative non calibrée.'])
def report(r):
 lines=['# Proposition de rechiffrage de quatre lots','', '**Proposition non adoptée. Les simulations conservent les 7 030 JH validés.**','', '## Résultats','', '| Lot | Retenu JH | Proposition JH | Variation JH | Proposition k€ HT |','|---|---:|---:|---:|---:|']
 for u in r['units']:lines.append(f"| {u['label']} | {u['adopted_jh']} | {u['proposal_jh']} | {u['delta_jh']:+} | {u['proposal_cost_eur_ht']/1000:.0f} |")
 lines+=['',f"En remplaçant ces quatre lots, le Core passerait à **{r['proposal_jh']} JH et {r['proposal_cost_eur_ht']/1000:.0f} k€ HT**, soit **{r['delta_jh']:+} JH et +{r['delta_cost_eur_ht']/1000:.0f} k€ HT**. Ce montant concerne la construction du produit, avant projection dans le temps.",'', '## Nature du chiffrage','',r['effort_basis'],'','Cette passe apporte une décomposition explicite en livrables et une frontière de financement. Les valeurs en JH sont proposées par estimation d’ingénierie. Elles ne sont ni déduites de la taille des fichiers ni observées dans un projet comparable. Une liste détaillée ne valide pas à elle seule la productivité. Les anciennes voies COCOMO II et COSMIC restent exposées ci-dessous comme repères, avec leurs écarts de périmètre. Ce contre-chiffrage n’est pas une troisième formule exécutée par le modèle actif.','', 'Les montants incluent les activités projet et le pilotage de l’équipe produit. Les QA de composants sont comprises dans chaque livrable. Les lignes de qualification croisée financent uniquement les interactions entre ces livrables. Aucun pilotage de programme ou Transformation Office n’est ajouté.','', '## Édition de redressement dans Master Data','', 'L’édition fait partie du produit. La ligne MD09 finance des formulaires de correction pour les six familles, avec motif, validation, provenance et gestion des conflits avec les contributions suivantes. Une correction crée une version et conserve les états publiés. Les différences de priorité entre sources et corrections doivent être rendues explicites. Le retour éventuel de la correction au système source et les règles propres à chaque marque appartiennent à l’intégration.','', 'Le montant Master Data ne résulte donc pas d’une suppression forfaitaire des fonctions d’édition. La consultation MD05, la correction MD09, le versionnement MD03 et le rejeu MD06 ont des livrables distincts.','', '## Comparaison avec les calculs existants','', '| Lot | COCOMO retenu avant arrondi JH | COSMIC actuel CFP | COSMIC actuel JH | Contre-chiffrage JH |','|---|---:|---:|---:|---:|']
 for u in r['units']:
  c=u['comparisons'];lines.append(f"| {u['label']} | {c['cocomo_reference_jh']:.1f} | {c['CFP']} | {c['cosmic_jh']:.1f} | {u['proposal_jh']} |")
 lines+=['','Les 5 CFP des ateliers portent sur la sauvegarde d’une vue et ne dimensionnent pas les trois interfaces nouvelles. Les 216 CFP de Process Management et les 68 CFP IT ne représentent pas tout le travail graphique et technique retenu. Les 420 CFP Master Data ne sont pas recomptés dans cette passe. Il ne faut ni sommer ces voies ni augmenter artificiellement les CFP pour atteindre le contre-chiffrage.','', 'Les références OSS et leurs quatre résultats sont conservés dans results.json avec les mesures et versions de la base figée. Aucun nouveau téléchargement ni rescan de dépôt distant n’a été réalisé pour cette passe.','']
 for u in r['units']:
  lines += [f"## {u['label']} — {u['proposal_jh']} JH",'','| Livrable | JH |','|---|---:|']
  for w in u['work']:lines.append(f"| {w['id']} · {w['label']} | {w['jh']} |")
  for w in u['work']:lines += ['',f"**{w['id']} — {w['label']}.** {w['scope']}",f"Réutilisation et frontière : {w['reuse']}",f"Financement : `{w['funding_ref']}`. Cas : {', '.join(w['scenario_refs'])}."]
 lines += ['', '## Conditions déterminantes','', '- Les six familles Master Data utilisent un cadre commun et une édition de redressement, pas six éditeurs autonomes.', '- Le studio utilise un catalogue d’actions et de champs borné. Un langage libre ou un éditeur universel impose un autre dimensionnement.', '- Les trois ateliers consomment les services métier financés. Aucun calcul de promesse, planification, optimisation ou transport supplémentaire.', '- Les consoles IT orchestrent les mécanismes déjà financés. Identité, sauvegardes, plateforme et noyaux de reprise ne sont pas reconstruits.', '- Le calendrier, le MCO et la durée du Transformation Office doivent être réexaminés séparément si cette proposition est adoptée. Aucun impact automatique de délai n’est déduit des JH.', '', f"Périmètre natif inchangé : {r['native_capabilities']} capacités. Les quatre lots sont étudiés. Aucun nouveau lot n’est adopté par ce document.", '', '## Reproduction','', f"Depuis la racine du dépôt : `python {REL}/calculate.py` puis `python {REL}/calculate.py --verify`. Les empreintes des sources, les contrôles et les répartitions de rôles sont dans results.json.", '', 'Les contrôles vérifient sommes, cas, propriétaires de financement, provenance et conservation du budget actif. Ils ne certifient pas les hypothèses de charge.']
 return '\n'.join(lines)+'\n'
if __name__=='__main__':
 r=calculate();encoded=json.dumps(r,ensure_ascii=False,indent=2)+'\n';text=report(r)
 if '--verify' in sys.argv:
  assert (OUT/'results.json').read_text(encoding='utf-8')==encoded,'Results changed'
  assert (OUT/'audit.md').read_text(encoding='utf-8')==text,'Report changed'
 else:
  (OUT/'results.json').write_text(encoded,encoding='utf-8');(OUT/'audit.md').write_text(text,encoding='utf-8')
 print(json.dumps({k:r[k] for k in ['status','work_package_count','adopted_jh','proposal_jh','delta_jh','proposal_cost_eur_ht','delta_cost_eur_ht','native_capabilities','checks']},ensure_ascii=False))
 print(json.dumps([{k:u[k] for k in ['label','adopted_jh','proposal_jh','proposal_cost_eur_ht','delta_jh']} for u in r['units']],ensure_ascii=False))
