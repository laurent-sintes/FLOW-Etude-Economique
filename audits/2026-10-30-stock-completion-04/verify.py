"""Reconcile the completed measurements, functional contract and estimate eligibility."""
from pathlib import Path
import json,hashlib,sys
from collections import Counter
import yaml
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
cosmic=load(OUT/'cosmic.json');sizes=load(OUT/'tailles-completees.json')
md=load(ROOT/'audits/2026-10-30-master-data-comparable-reuse/measurements.json')
groups={g['id'] for g in cosmic['groups']};process_ids=set();movement_ids=set();total=Counter()
for p in cosmic['processes']:
 assert p['id'] not in process_ids;process_ids.add(p['id']);seen=set();subtotal=Counter()
 assert p['functional_user'] and p['trigger']
 for m in p['movements']:
  assert m['id'] not in movement_ids;movement_ids.add(m['id']);assert m['group'] in groups
  key=(m['type'],m['group']);assert key not in seen;seen.add(key);assert m['cfp']==1
  subtotal[m['type']]+=1
 assert subtotal['E']>0 and subtotal['W']+subtotal['X']>0
 assert sum(subtotal.values())==p['count']['CFP'];total.update(subtotal)
assert sum(total.values())==cosmic['result']['CFP']
assert dict(total)==cosmic['result']['movements']
source_guard=load(ROOT/'audits/2026-10-30-corrections-moteur-bicephale/hashes-after.json')
guard={k:v for k,v in source_guard.items() if k.startswith(('source/','sources/','config/'))}
changed={k:v for k,v in guard.items() if hashlib.sha256((ROOT/k).read_bytes()).hexdigest()!=v}
assert not (set(changed)-{'source/reperes-synvance.yaml','config/application.yaml'}), changed
assert all(not k.startswith('sources/') for k in changed)
guard={k:v for k,v in guard.items() if k not in changed}
native_matrix=[];gates={}
for product in sizes:
 source=load(ROOT/f'audits/2026-10-30-stock-mesures-03/{product}-mesures.json')
 display=load(OUT/(product+'-presentation.json'))
 for f in display['files']:
  path=ROOT/md['repos'][product]['root']/f['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==f['sha256']
  for entry in f['selection']:
   if entry['kind']=='handler':
    text=path.read_bytes().decode('utf-8-sig');assert entry['start']<=entry['end']
  assert f['program_units']==sum(e.get('program_units',0) for e in f['selection'])
  assert f['declarative_units']==sum(e['kind']!='handler' for e in f['selection'])
 for p in cosmic['processes']:
  if p['id'] in ('S18','S19','S20','S21'):
   status='aucune équivalence complète établie dans la sélection'
   reason='Le contrat de fourniture/retour ou constat n’est pas démontré par le seul stock natif ; la comptabilité interne ne remplace pas le contrat Finance.'
  elif p['id']=='S17':
   status='requêtes de stock réutilisables, contrat de fourniture non mesuré'
   reason='Dates, version, correction et limites de connaissance du jeu fourni restent à implémenter/dimensionner.'
  else:
   status='appui partiel sur des mécanismes natifs'
   reason='Les processus Flow incluent protocole, double date, provenance, filtres et responsabilités à rapprocher ; aucune équivalence complète revendiquée.'
  native_matrix.append(dict(product=product,process=p['id'],capabilities=p['capabilities'],status=status,reason=reason))
 gates[product]=dict(code_pinned=True,presentation_fragments_measured=True,critical_paths_reviewed_statically=True,
  full_functional_contract_implemented_or_sized=False,application_dependencies_and_adapters_complete=False,
  shared_funding_isolated=True,native_full_family_effort_calculable=False,COCOMO_JH=None,
  reason='Les tailles mesurent une sélection élargie ; des contributions métier et adaptateurs ne sont pas dimensionnés. Les quatre nombres COCOMO issus de ces fragments ne seraient pas quatre coûts de la famille Stock.')
assert all(s['native_full_family_cocomo_jh'] is None for s in sizes.values())
boundary=load(OUT/'frontieres-classees.json');assert len(boundary)==41
packages=[
dict(id='STOCK-F01',caps=['BC-009','BC-010'],work='Faits, soldes externes et corrections : identité, dates du fait/connaissance, autorité et filiation.',reuse=['master-data-admission','master-data-versions'],new='Sémantique des faits de stock, application unique des effets, règles événements/soldes et propagation des corrections.',cosmic=['S01','S02','S03'],size_status='non dimensionné ; code natif de correction utilisable comme analogue, pas équivalent complet'),
dict(id='STOCK-F02',caps=['BC-011','BC-012'],work='Positions explicables, apports attendus et fourniture versionnée.',reuse=['master-data-common-domain','master-data-protection'],new='Rapprochement des producteurs, fraîcheur et limites, fourniture à la planification sans double compte.',cosmic=['S05','S06','S07','S17'],size_status='projections de base mesurées ; contrats et dépendances producteurs non dimensionnés'),
dict(id='STOCK-F03',caps=['BC-013'],work='Protocoles, constats et décisions de correction justifiées.',reuse=['java-spring-framework-services','master-data-protection'],new='Rapprochement des comptages et mouvements concomitants, paramètres de contrôle et autorité de correction.',cosmic=['S08','S09','S10','S11','S12'],size_status='primitives et présentation mesurées ; contrat complet non dimensionné'),
dict(id='STOCK-F04',caps=['BC-018'],work='Engagements, révision, consommation/libération et concurrence.',reuse=['java-spring-framework-services'],new='Invariants, conflits, échéances métier et politique de retry sous garanties déclarées.',cosmic=['S13','S14','S15','S16'],size_status='primitives natives mesurées ; garantie cible et adaptations non dimensionnées'),
dict(id='STOCK-F05',caps=['BC-016'],work='Faits à Finance et suivi des retours.',reuse=['master-data-admission','master-data-versions'],new='Contrat de contribution, correction liée, acceptation/rejet/référence de prise en compte ; aucune écriture comptable.',cosmic=['S18','S19','S21'],size_status='contrat fonctionnel décrit ; code équivalent non mesuré'),
dict(id='STOCK-F06',caps=['BC-017'],work='Constats produit et corrections documentées.',reuse=['master-data-common-domain','master-data-admission'],new='Fait, produit, contexte, preuve et fourniture au responsable produit ; aucun PLM ni diagnostic causal.',cosmic=['S20'],size_status='contrat fonctionnel décrit ; code équivalent non mesuré'),
dict(id='STOCK-F07',caps=['BC-009','BC-010','BC-011','BC-012','BC-013','BC-016','BC-017','BC-018'],work='Reprise et mise en service Stock.',reuse=['master-data-reprise','master-data-service'],new='Rapprocher faits/quantités/réservations après reprise et vérifier objectifs de service propres au stock.',cosmic=[],size_status='exigences non fonctionnelles hors CFP ; effort spécifique non dimensionné')]
report=dict(id='stock-completion-04',status='contrat_fonctionnel_compte_perimetres_natifs_elargis_mais_non_complets',
 completed_this_iteration=['Sélections de présentation/permissions établies dans les 14 fichiers de contexte.','41 frontières natives restantes classées explicitement ; aucune méthode mêlée ajoutée sans justification.','Contrat complet proposé pour les huit capacités, avec groupes et déclencheurs COSMIC.','Compléments Stock et réutilisation Master Data isolés en sept ensembles de travaux sans durée inventée.','Critères d’éligibilité des quatre calculs natifs vérifiés : insuffisants pour un total de famille.'],
 measured_selections=sizes,cosmic_result=cosmic['result'],cosmic_contract='cosmic.json',cosmic_not_certified=True,
 native_calculation_eligibility=gates,missing_work_packages=packages,
 alignment=dict(numeric_gap_jh=None,numeric_gap_pct=None,reason='Périmètre natif mesuré partiel versus contrat fonctionnel Flow complet ; comparaison numérique non recevable à ce stade.'),
 current_estimates=dict(cumulative_adopted_gross_jh=1500,master_data_months=17,stock_retained_jh=None,functional_stock_comparison_only_jh=cosmic['result']['indicative_jh'],functional_is_added_to_budget=False),
 progress=dict(stock_capabilities_with_explicit_functional_contract=8,stock_capabilities_with_proposed_COSMIC=8,native_selections_with_added_presentation=4,native_full_family_estimates_ready=0,
 previously_measured_native_method_count=169,presentation_files_reviewed=14,remaining_native_boundary_entries_classified=41,
 new_capabilities_adopted=0,adopted_capabilities=6,total_capabilities=88,adopted_coverage_pct=6.8,campaign_capabilities_framed=14,remaining_java_capabilities_to_estimate=82),
 uncertainty='La description fonctionnelle et les limites sont plus explicites. Le repère de 20 h/CFP reste une hypothèse de comparaison, pas une calibration Flow. Les CFP ne dimensionnent pas seuls les exigences de concurrence, de reprise et de service.',
 next_iteration=dict(worthwhile=True,change_of_focus_required=True,
 objective='Dimensionner les compléments Stock-F01 à F07 par analogies complètes et réutilisation qualifiée, puis construire quatre assiettes complètes incluant ces compléments avant COCOMO.',
 not_worthwhile='Poursuivre le seul découpage des mêmes méthodes natives ou comparer leurs fragments au comptage COSMIC complet.',
 reason='Les manques sont maintenant localisés : ce ne sont pas seulement des appels non suivis. Ils portent sur des responsabilités Flow absentes ou non établies dans les sélections natives.',
 decision_gate='Si les compléments restent non dimensionnables, proposer une méthode d’analogie par mécanismes complets ; ne pas présenter les quatre fragments comme des coûts de Stock.'))
(OUT/'matrice-native-cosmic.json').write_text(json.dumps(native_matrix,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'bilan.yaml').write_text(yaml.safe_dump(report,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
verification=dict(status='passed',CFP=cosmic['result']['CFP'],processes=len(process_ids),groups=len(groups),movement_counts=dict(total),
 logical_count_reconciled=True,duplicate_process_or_movement_ids=0,duplicate_group_type_per_process=0,
 native_full_family_estimates_ready=0,active_source_files_unchanged=len(guard),unrelated_changed_sources_not_modified_by_this_iteration=sorted(changed),
 data_sources={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'source/fondamentaux.yaml',ROOT/'source/referentiel-capacites.yaml',ROOT/'source/analyse-perimetre-core.yaml',ROOT/'audits/2026-10-30-master-data-decomposition-gap/benchmark-decision.json']})
(OUT/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(COSMIC=cosmic['result'],native_totals_ready=0,cumulative_adopted_jh=1500,checks=verification),ensure_ascii=False,indent=2))
