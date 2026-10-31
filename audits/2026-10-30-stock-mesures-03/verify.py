from pathlib import Path
import json,hashlib,subprocess,sys
import yaml
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
md=load(ROOT/'audits/2026-10-30-master-data-comparable-reuse/measurements.json')
measurement=load(OUT/'mesures.json');trace=load(OUT/'chemins-critiques.json')
checks={};method_count=field_count=0
for product,summary in measurement['summary'].items():
 doc=load(OUT/(product+'-mesures.json'));program=declarative=0
 for f in doc['files']:
  raw=(ROOT/md['repos'][product]['root']/f['path']).read_bytes()
  assert hashlib.sha256(raw).hexdigest()==f['sha256']
  keys=[(n['kind'],n['start'],n['end']) for n in f['counted_nodes']]
  assert len(keys)==len(set(keys)),(product,f['path'],'node duplicated')
  assert len(keys)==f['program_units']
  assert all(not (r['start']<=n['start'] and n['end']<=r['end']) for r in f['excluded_ranges'] for n in f['counted_nodes'])
  ranges=[(m['start'],m['end']) for m in f['selected_methods']]
  for i,(a,b) in enumerate(ranges):
   assert all(b<c or d<a for c,d in ranges[i+1:]),'Overlapping selected methods'
  program+=f['program_units'];declarative+=f['declarative_units'];method_count+=len(f['selected_methods']);field_count+=len(f['declarations'])
 assert (program,declarative)==(summary['program_units'],summary['declarative_units'])
 assert program+declarative==summary['program_plus_declarative_at_weight_1']
 assert doc['stock_family_jh'] is None
 for product_trace in [t for t in trace['traces'] if t['product']==product]:
  assert len(product_trace['steps'])>=2
  assert all(key in trace['nodes'] for key in product_trace['steps'])
for key,node in trace['nodes'].items():
 raw=(ROOT/md['repos'][node['repo']]['root']/node['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==node['sha256']
 if node['funding_owner']=='master-data-java-spring':assert node['measured_in_stock'] is False
before=load(ROOT/'audits/2026-10-30-corrections-moteur-bicephale/hashes-after.json')
guard={k:v for k,v in before.items() if k.startswith(('source/','sources/','config/'))}
assert all(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==value for path,value in guard.items())
assert len(trace['traces'])==12
checks=dict(measured_products=4,critical_paths_static=12,evidence_nodes=len(trace['nodes']),shared_platform_nodes_not_recharged=sum(n['funding_owner']=='master-data-java-spring' for n in trace['nodes'].values()),selected_methods=method_count,source_and_model_fields=field_count,duplicate_counted_nodes=0,overlapping_method_ranges=0,excluded_program_nodes_counted=0,active_source_files_unchanged=len(guard),runtime_concurrency_tests=False,new_family_jh=None)
previous=load(ROOT/'audits/2026-10-30-stock-perimetres-02/verification.json')['summary']
progress=dict(stock_capabilities_framed=8,stock_native_selections_measured=4,stock_native_selections_total=4,
 previous_selected_methods=sum(r['methods'] for r in previous.values()),current_selected_methods=method_count,
 previous_boundary_methods=sum(r['mixed_boundary_methods'] for r in previous.values()),
 previously_boundary_methods_promoted=sum(r['mixed_methods_promoted'] for r in measurement['summary'].values()),
 remaining_boundary_method_entries=sum(r['remaining_mixed_method_entries'] for r in measurement['summary'].values()),
 new_capabilities_adopted=0,stock_full_family_estimates=0,campaign_capabilities_framed=14,adopted_capabilities=6,total_capabilities=88,adopted_coverage_pct=6.8,remaining_java_capabilities_to_estimate=82,cumulative_adopted_gross_jh=1500,master_data_months=17)
report=dict(id='stock-mesures-03',status='mesures_partielles_et_chemins_principaux_documentes',method_reference='source/fondamentaux.yaml#estimation_model',
 results=measurement['summary'],
 meaning='Les unités sont des instructions et déclarations syntaxiques sélectionnées. Elles ne sont ni des lignes physiques ni des CFP, ni le nombre de fonctions métier. Le total programme + déclaratif emploie un poids 1 affiché pour la lecture, sans calibration de productivité entre langages.',
 critical_path_findings=[
 dict(product='ERPNext / Frappe',write='Document métier vers sauvegarde Frappe et SQL, code générique partagé.',correction='Décalage des quantités futures, ordre date/création et borne au prochain inventaire identifiés.',concurrency='Requêtes for_update repérées, sérialisation complète non démontrée.'),
 dict(product='Odoo',write='Mise à jour du cache de champs puis flush et écriture SQL ; pas un appel direct write→SQL.',correction='Ajustement via un mouvement et synchronisation des quants.',concurrency='Verrou sur quants existants ; création et retries à qualifier.'),
 dict(product='Tryton',write='Transition de workflow vers ModelSQL.write ; ne pas assimiler le petit corps de assign à tout le comportement.',correction='Lignes d’inventaire vers mouvements correctifs ; Move.do financier non compté en totalité.',concurrency='Verrouillage de lignes ou de modèle dans le chemin natif d’affectation ; pas de test de contention.'),
 dict(product='Axelor',write='Mise à jour des quantités vers repository et JPA ; branches de réapprovisionnement exclues du comptage.',correction='Inventaire vers mouvements correctifs et actualisation des positions ; métadonnées de dernier inventaire distinguées de la quantité actuelle.',concurrency='Transaction repérée ; verrou exclusif non établi dans les chemins examinés. Garantie ouverte, sans conclure à une absence générale dans le produit.')],
 known_native_excess=measurement['known_native_excess'],
 validation=checks,progress=progress,
 uncertainty=dict(quantified=False,numeric_alignment_available=False,confidence_class=None,interpretation='Les incertitudes de rattachement des principaux appels ont diminué. L’incertitude sur l’effort de la famille complète n’est pas encore quantifiée.'),
 not_yet_costable_reasons=['Les vues, permissions et imports/raccordements non retenus ne sont pas mesurés.','Des méthodes mixtes restent en frontière ; certaines contiennent le workflow natif excédentaire, d’autres des dépendances à délimiter.','Le noyau observé ne couvre pas tous les faits externes, filiations/Handling Units, reprises, limites de connaissance et garanties Flow.','Les contrats de fourniture Finance, planification et retour produit restent à dimensionner, à partir de références et hypothèses bornées.','Le comptage COSMIC et la confrontation des activités ne sont pas encore réalisés pour cette famille.'],
 stock_family_gross_jh=None,
 next_iteration=dict(worthwhile=True,objective='Compléter la mesure de la présentation et des dépendances métier retenues, puis dimensionner les compléments Flow par analogies de code et construire le comptage COSMIC.',stop_rule='Ne pas refaire une inspection générale des mêmes fichiers. Toute nouvelle itération doit apporter des composants mesurés ou un calcul de périmètre explicitement complet ; aucun coefficient ne compense une omission.'))
(OUT/'bilan.yaml').write_text(yaml.safe_dump(report,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
(OUT/'verification.json').write_text(json.dumps(dict(status='passed',checks=checks,script_hashes={n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in ('measure.py','trace.py')}),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(checks=checks,progress=progress),ensure_ascii=False,indent=2))
