"""Revue Java ciblée, preuves figées et reproduction des calculs antérieurs.
Les tailles des témoins sont informatives ; elles ne recalibrent pas l'effort.
"""
from pathlib import Path
import hashlib,importlib.util,json,math,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
import yaml
from model_context import model_session
from estimation_calculation import formula
GIT='C:/Program Files/Git/cmd/git.exe'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(name,d):(OUT/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def expected_or_save(name,d):
 if (OUT/name).exists():assert read(OUT/name)==d,name
 else:save(name,d)
def collect():
 h=read(OUT/'review.json')
 parser=load('parser03','audits/2026-10-30-stock-perimetres-02/build.py')
 counter=load('counter03','audits/2026-10-30-master-data-natif/measure.py')
 rows=[]
 for f in h['files']:
  repo=h['repos'][f['repo']];path=ROOT/repo['root']/f['path']
  raw,methods,decl=parser.parse(path)
  pinned=subprocess.run([GIT,'-C',str(ROOT/repo['root']),'show',repo['commit']+':'+f['path']],capture_output=True,check=True).stdout
  assert raw.replace(b'\r\n',b'\n')==pinned.replace(b'\r\n',b'\n'),str(path)
  selected=[];keys=set()
  if path.suffix=='.java':
   tree=counter.PARSERS['.java'].parse(raw)
   assert not tree.root_node.has_error
   nodes=list(counter.walk(tree.root_node))
   for selector in f['selectors']:
    candidates=[m for m in methods if parser.matches(m,selector)]
    assert len(candidates)==1,(f['path'],selector,candidates)
    method=candidates[0]
    units=[]
    for n in nodes:
     line=n.start_point.row+1;end=n.end_point.row+1
     if line>=method['start'] and end<=method['end'] and ((n.type.endswith('_statement') and n.type!='empty_statement') or n.type in counter.JAVA_EXTRA):
      key=(n.type,n.start_byte,n.end_byte)
      assert key not in keys,(f['path'],selector,key)
      keys.add(key);units.append(dict(type=n.type,start_byte=n.start_byte,end_byte=n.end_byte,start=line,end=end))
    selected.append(dict(selector=selector,name=method['name'],start=method['start'],end=method['end'],program_units=len(units),nodes=units))
  row=dict(**f,root_path=path.relative_to(ROOT).as_posix(),sha256=sha(path),git_blob_sha256=hashlib.sha256(pinned).hexdigest(),
   pinned_revision=repo['commit'],pinned_blob_equal_after_line_endings=True,
   source_url='https://github.com/'+repo['repository']+'/blob/'+repo['commit']+'/'+f['path'],
   selected_methods=selected,selected_program_units=len(keys),whole_file=counter.measure(path))
  rows.append(row)
 return h,rows
def freeze():
 h,rows=collect();previous=ROOT/h['previous']
 deps=[previous/'inputs.json',previous/'hypotheses.json',previous/'input-freeze.json',previous/'cosmic.json',
  previous/'cosmic-refinement.json',previous/'refinement-freeze.json',previous/'results.json',previous/'calculate.py',previous/'verification.json',
  ROOT/'audits/2026-10-30-master-data-natif/measure.py',ROOT/'audits/2026-10-30-stock-perimetres-02/build.py']
 protected=[ROOT/p for p in ['source/estimations-core-retenues.yaml','source/calculs-estimation-core.yaml','source/fondamentaux.yaml',
 'source/schema-fondamentaux.yaml','source/referentiel-capacites.yaml','sources/cartographie-scm-2026-10-24.yaml']]
 inputs=dict(review_sha256=sha(OUT/'review.json'),code=rows,dependencies={p.relative_to(ROOT).as_posix():sha(p) for p in deps},
  protected={p.relative_to(ROOT).as_posix():sha(p) for p in protected},
  policy='Aucune nouvelle taille ni coefficient d effort ; revue des hypothèses gelées avant reproduction des JH.')
 expected_or_save('inputs.json',inputs)
 expected_or_save('input-freeze.json',dict(inputs_sha256=sha(OUT/'inputs.json'),review_sha256=sha(OUT/'review.json'),
  effort_recalibration=False,policy='Preuves et position de revue fixées avant reproduction ; aucun objectif de rapprochement.'))
 print(json.dumps(dict(frozen=True,files=len(rows),selected_methods=sum(len(r['selected_methods']) for r in rows)),ensure_ascii=False))
def report():
 h=read(OUT/'review.json');d=read(OUT/'inputs.json');fr=read(OUT/'input-freeze.json')
 assert sha(OUT/'inputs.json')==fr['inputs_sha256'] and sha(OUT/'review.json')==fr['review_sha256']
 for key in ('dependencies','protected'):
  for p,s in d[key].items():assert sha(ROOT/p)==s,p
 _,observed=collect();assert observed==d['code']
 old=load('ownership02','audits/2026-10-30-propriete-stock-calcul-02/calculate.py')
 previous=ROOT/h['previous'];inputs=read(previous/'inputs.json');results=read(previous/'results.json')
 c=inputs['cocomo'];rows=[]
 with model_session():
  for oldrow in results['rows']:
   r=old.calculate(inputs,oldrow['id']);units=r['detail']['equivalent_units']
   exponent=c['B']+.01*c['SF_sum']
   independent=c['A']*(units/1000)**exponent*c['other_EM']*c['SCED']*c['month_hours']/c['day_hours']*c['effort_phase_factor']
   assert math.isclose(independent,r['jh'],rel_tol=1e-12)
   assert math.isclose(r['jh'],oldrow['jh'],rel_tol=1e-12) and r['rounded_jh']==oldrow['rounded_jh']
   rows.append(dict(id=r['id'],name=r['label'],jh=r['jh'],rounded_jh=r['rounded_jh'],
    equivalent_units=units,schedule_months=r['schedule_months'],
    reservation_ruler=inputs['banks'][r['id']]['central']['reservation_chain']['program_units'],
    correction_ruler=inputs['banks'][r['id']]['central']['correction_chain']['program_units'],
    new_behavior_units=sum(b['new_behavior_units'] for b in r['detail']['blocks']),
    program_units=r['detail']['program_units'],declarative_units=r['detail']['declarative_units']))
  functional=old.cosmic_count(inputs)
 assert functional['CFP']==80 and math.isclose(functional['jh'],80*20/7)
 java=next(r for r in rows if r['id']=='axelor');java_old=next(r for r in results['rows'] if r['id']=='axelor')
 modules=[b for b in java_old['detail']['blocks'] if b['id'] in ('OWN-F04','OWN-F05')]
 allocation=[a for a in java_old['allocation'] if a['id'] in ('OWN-F04','OWN-F05')]
 for r in rows:
  r['control_higher_jh']=functional['jh']-r['jh']
  r['control_higher_pct']=(functional['jh']-r['jh'])/r['jh']*100
  r['implied_hours_per_CFP']=r['jh']*7/80
  r['higher_than_java_jh']=r['jh']-java['jh']
  r['higher_than_java_pct']=(r['jh']-java['jh'])/java['jh']*100
 decisions=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'))['units']
 total=sum(u['total_jh'] for u in decisions)
 assert total==1840 and [(u['total_jh'],u['months']) for u in decisions]==[(1500,17),(340,10)]
 # Selected native witnesses are not full application closures or equivalent product sizes.
 journal=sum(r['selected_program_units'] for r in d['code'] if '/axelor-account/' in '/'+r['root_path'])
 query=sum(r['selected_program_units'] for r in d['code'] if r['path'].endswith('/StockHistoryServiceImpl.java'))
 budget=sum(b['new_behavior_units'] for b in modules)
 decision=dict(status='100_JH_maintenus_comme_hypothese_de_travail_non_consolidee',rounded_jh=java['rounded_jh'],exact_jh=java['jh'],
  reason='Le registre et les deux dates étaient déjà dimensionnés comme nouveaux modules. La revue ne démontre pas un manque de volume chiffrable permettant une correction de taille.',
  not_a_validation='Ni un équivalent Java complet, ni une productivité Flow, ni un coût de réalisation observé ne sont démontrés. Ne pas présenter 100 JH comme une estimation confirmée par les quatre produits.',
  provisional_volume=budget,allocation_jh=sum(x['allocated_jh'] for x in allocation),
  partial_witness_program_units=dict(journal=journal,dated_query=query),
  witness_limit='Ces témoins partiels contiennent des comportements financiers exclus et délèguent des services. Leur taille ne démontre ni une borne basse ni une borne haute du code Flow. Aucune soustraction ni conversion de ces tailles en JH.',
  module_assumptions=[dict(id=b['id'],behavior_units=b['new_behavior_units'],fraction=b['fraction']) for b in modules],
  journal_primitives_correction='Le libellé ancien sur les primitives de journal ne prouve que la disponibilité de persistance/audit techniques. Le journal de propriété et sa sélection de versions restent à construire dans OWN-F04/F05.',
  nominal_calculated_months=java['schedule_months'],retained_schedule_months=None,
  new_adoption=False,statistical_uncertainty=None,
  sensitive_assumption=next(s for s in java_old['sensitivities'] if s['id']=='registre-et-deux-dates'))
 progress=dict(total_capabilities=88,studied_or_proposed=16,studied_or_proposed_pct=16/88*100,
  adopted=14,adopted_pct=14/88*100,remaining_to_estimate=72,remaining_to_adopt=74,
  new_capabilities_studied=0,new_capabilities_adopted=0,
  advance='Frontière entre audit technique, historique Stock et registre de propriété clarifiée ; sources Java supplémentaires vérifiées.',
  effort_uncertainty_reduced=False,
  reason='La couverture sémantique est mieux qualifiée, mais les fractions de nouveau code et le rendement ISBSG restent non calibrés.')
 explanation=json.loads('{"other_OSS":{"arithmetic_reason":"Les mêmes fractions de modules multiplient des analogues de tailles différentes : décision/réservation Java 91 unités, ERPNext 178,05, Odoo 324,15, Tryton 346 ; correction Java 281,8, ERPNext 611,7, Odoo 528,3, Tryton 420,8. Le total Java est donc plus petit avant même COCOMO.","interpretation":"Ces différences portent sur les chaînes et conventions de code sélectionnées. Les appels à des services délégués, la génération de code et les frontières des composants diffèrent. Ce n\'est pas une mesure de productivité comparée, ni la preuve que Java coûterait moitié moins.","scope":"Les quatre montants dimensionnent le même besoin Flow par analogies natives, avec un patrimoine Master Data et Stock disponible. Ils ne sont pas quatre historiques de coût réellement consommé, ni quatre implémentations natives complètes du registre Flow.","no_additional_framework_discount":"Aucune nouvelle réduction Spring. Les mécanismes génériques sont déjà exclus du nouveau financement ; le nouveau comportement de propriété reste financé."},"COSMIC":{"same_scope_count":80,"arithmetic":"80 CFP × 20 h/CFP × 1 ÷ 7 h/JH = 228,57142857142858 JH.","gap_reason":"La voie fonctionnelle utilise un rendement historique, qui n\'est pas recalibré sur la réutilisation de Master Data et Stock ni sur ce composant. La voie COCOMO dépend d\'une taille de nouveau code supposée par analogie. Le désaccord peut provenir des deux ; aucun des deux biais n\'est mesuré.","java_implied_rate":"À 98,9157 JH, le calcul Java correspond à 8,6551 h/CFP. Le code étudié ne démontre pas ce rendement en projet.","no_convergence_claim":"L\'écart reste de 129,6557 JH, soit 131,077 % au-dessus du Java non arrondi. Ne pas moyenner, relever les coefficients ou transformer cet écart en confiance."},"source_review_limits":"Lecture statique des sources figées ; aucun démarrage des quatre ERP ni test fonctionnel de leurs garanties temporelles. L\'absence d\'analogue dans les chemins étudiés ne prouve pas son absence de tout le produit.","what_is_confirmed":"Les sources, les frontières des analogies, l\'arithmétique et le fait que les compléments sont déjà inclus dans le calcul.","what_is_not_confirmed":"La suffisance des fractions de nouveau code, le rendement du projet Flow et une équivalence native complète."}')
 out=dict(id=h['id'],decision=decision,explanation=explanation,findings=h['findings'],functional_example=h['functional_example'],native_comparisons=rows,
  functional_control=dict(CFP=80,jh=functional['jh'],hours_per_CFP=20,factor=1,
   explanation='Comptage inchangé : la date de connaissance est un attribut de la lecture déjà comptée. Le rendement historique reste non calibré sur ce composant ni sa réutilisation.',
   activities='Conventions des phases de la précédente itération conservées ; contrôle fonctionnel et COCOMO n ont pas une calibration commune observée.'),
  cumulative=dict(adopted_jh=total,Master_Data_jh=1500,Stock_jh=340,ownership_adopted_jh=None,
   conditional_addition_if_100_later_adopted=total+java['rounded_jh'],conditional_addition_is_not_a_retained_total=True,
   integrated_cocomo_total=False,schedules_added=False),
  progress=progress,
  recommendation=dict(another_general_source_iteration_worthwhile=False,
   proposed_next_step='Clore cette revue de code. Pour décider, présenter explicitement les 100 JH comme hypothèse Java/Spring et le contrôle à 229 JH, avec la sensibilité du registre. Une consolidation doit assumer ce désaccord ; aucune moyenne ni hausse mécanique.',
   targeted_reopening='Seulement si le périmètre change : moteur temporel général, clauses spécifiques, historique non borné avec exigences de performance nouvelles, ou nouvelles données de productivité.'),
  active_model_changed=False,application_changed=False,skill_changed=False,adoption=False)
 save('results.json',out)
 (OUT/'bilan.yaml').write_text(yaml.safe_dump(out,allow_unicode=True,sort_keys=False,width=110),encoding='utf-8')
 v=dict(passed=True,pinned_source_files=len(d['code']),selected_methods=sum(len(r['selected_methods']) for r in d['code']),
  prior_native_calculations_reproduced=4,independent_cocomo_arithmetic=True,CFP=80,
  no_new_effort_coefficients=True,protected_active_sources_unchanged=True,old_evidence_unchanged=True,
  adopted_jh=total,conditional_java_jh=java['rounded_jh'],adoption=False)
 save('verification.json',v)
 save('provenance.json',dict(files={p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='provenance.json'},
  dependencies=d['dependencies'],protected=d['protected'],raw_source_hashes={r['root_path']:r['sha256'] for r in d['code']}))
 print(json.dumps(dict(verification=v,decision=decision,native_comparisons=rows,progress=progress),ensure_ascii=False,indent=2))
if __name__=='__main__':
 if sys.argv[1:] == ['--freeze']:freeze()
 elif sys.argv[1:]==['--report']:report()
 else:raise SystemExit('Use --freeze or --report')
