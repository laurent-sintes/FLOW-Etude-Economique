"""Comparaison diagnostique des quatre OSS. Aucun temps de tâche, aucune écriture du modèle actif."""
from pathlib import Path
import ast, json, hashlib, re, textwrap, subprocess, math
ROOT=Path.cwd()
A=ROOT/'audits/2026-10-30-master-data-4-oss'
I=json.loads((A/'entrees.json').read_text(encoding='utf-8'))
checks=[]
def check(ok,label):
    if not ok: raise AssertionError(label)
    checks.append(label)
def dump(name,obj): (A/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def python_count(text,select=None):
    # Generated type blocks are explicitly not authored application source.
    text=re.sub(r'(?m)^[ \t]*# begin: auto-generated types[\s\S]*?^[ \t]*# end: auto-generated types[^\n]*','',text)
    tree=ast.parse(text)
    nodes=ast.walk(tree)
    if select:
        chosen=[n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in select]
        check(len(chosen)==len(select),'Python selected functions: '+str(select))
        nodes=(v for n in chosen for v in ast.walk(n))
    units=[]
    for n in nodes:
        if not isinstance(n,ast.stmt) or isinstance(n,(ast.Import,ast.ImportFrom,ast.Pass)):continue
        if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):continue
        units.append({'line':n.lineno,'end_line':n.end_lineno,'kind':type(n).__name__})
    return {'logical':len(units),'units':units,'line_coordinates':'Source after removing generated blocks; function selections on unchanged ERPNext item source retain original lines.'}
def java_count(text):
    text=re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*[\s\S]*?\*/|//[^\n]*',lambda m:'' if m[0].startswith('/') else 'STR',text)
    text=re.sub(r'(?m)^\s*(package|import)\s+[^;]+;','',text)
    annotations=len(re.findall(r'(?m)^\s*@',text))
    text=re.sub(r'(?m)^\s*@[^\n]+','',text)
    par=0; pending='';units=[]
    for c in text:
        if c=='(':par+=1
        if c==')':par-=1
        if c in ';{' and par==0:
            if pending.strip(): units.append(re.sub(r'\s+',' ',pending.strip()))
            pending=''
        elif c=='}' and par==0:pending=''
        else:pending+=c
    check(par==0,'Balanced Java parentheses')
    return {'logical':len(units),'units':units,'annotations_excluded':annotations}
def xml_count(text):
    import xml.etree.ElementTree as ET
    tree=ET.fromstring(text)
    seed_nodes=0
    for parent in tree.iter():
        for child in list(parent):
            if child.tag.split('}')[-1]=='record' and child.attrib.get('model') in ['product.uom','product.uom.category','uom.uom']:
                seed_nodes+=sum(1 for _ in child.iter())
                parent.remove(child)
    tags=[e.tag.split('}')[-1] for e in tree.iter()]
    excluded={'odoo','tryton','data','domain-models','object-views','module','extra-code'}
    decl=sum(t not in excluded for t in tags)
    # Only authored domain Java CDATA, not HTML help or literal strings.
    embedded=[]
    if 'domain-models' in tags:
        for e in tree.iter():
            tag=e.tag.split('}')[-1];c=e.text or ''
            if tag=='extra-code' or (tag=='string' and 'return ' in c):
                embedded.append(java_count(c))
    return {'declarative':decl,'logical':sum(p['logical'] for p in embedded),'elements':tags,'embedded':embedded,'seed_data_nodes_excluded':seed_nodes}
def doctype_count(text):
    j=json.loads(text)
    fields=[f for f in j['fields'] if f['fieldtype'] not in ['Column Break','Section Break','Tab Break','HTML','Button','Fold']]
    props=[k for k in ['allow_import','allow_rename','autoname','editable_grid','quick_entry','track_changes','sort_field','sort_order','show_name_in_global_search'] if k in j]
    return {'logical':0,'declarative':1+len(fields)+len(j.get('permissions',[]))+len(props),'field_names':[f['fieldname'] for f in fields],'permission_rules':len(j.get('permissions',[])),'behavior_properties':props}
def cocomo(units):
    p=I['model'];E=p['B']+.01*p['scale_sum']
    pm=p['A']*(units/1000)**E*p['effort_multiplier']
    t=p['C']*pm**(p['D']+.2*(E-p['B']))
    jh=pm*p['person_month_hours']/p['jh_hours']
    return {'logical_equivalent_hypothesis':units,'ksloc':units/1000,'E':E,'pm_elaboration_construction':pm,'jh_elaboration_construction':jh,'jh_inception':jh*.06,'jh_transition':jh*.12,'jh_full_lifecycle_hypothesis':jh*1.18,'months_elaboration_construction':t,'months_full_lifecycle_hypothesis':t*1.25}
# Meaningful small fixtures for counting logic, not exact output snapshots.
check(python_count('"""doc"""\nimport os\nx=(1+\n 2)\nif x:\n print(x)\n')['logical']==3,'Python comments/docstring/import/multiline conventions')
check(java_count('import a.B;\nclass C { int n; void f(){ String x=";{}"; /* ; */ if(true) { n++; } } }')['logical']==6,'Java delimiters in comments and literals ignored')
check(xml_count('<odoo><record id="x"><field name="a"/></record></odoo>')['declarative']==2,'XML declaration convention')
check(xml_count('<tryton><data><record model="product.uom"><field name="name">kg</field></record><record model="ir.ui.view"><field name="type">form</field></record></data></tryton>')['declarative']==2,'Initial master data excluded, view declarations retained')
check(abs(cocomo(11326)['jh_elaboration_construction']-921.0026258269762)<1e-8,'Previous nominal COCOMO independently reproduced')
baseline=json.loads((A/'baseline.json').read_text(encoding='utf-8'))
for f,h in baseline['files'].items():check(sha(ROOT/f)==h,'Preserved '+f)
products=[];measurements=[];pins=[]
for p in I['products']:
    logical=declarative=0
    for spec in p['files']:
        f=(A if spec.get('relative_audit') else ROOT)/spec['path']
        text=f.read_text(encoding='utf-8-sig')
        if spec['kind']=='python':r=python_count(text,spec.get('select_functions'))
        elif spec['kind']=='java':r=java_count(text)
        elif spec['kind']=='xml':r=xml_count(text)
        elif spec['kind']=='doctype':r=doctype_count(text)
        elif spec['kind']=='access_csv':
            import csv,io
            r={'logical':0,'declarative':len(list(csv.DictReader(io.StringIO(text))))}
        else:raise ValueError(spec)
        logical+=r.get('logical',0);declarative+=r.get('declarative',0)
        measurements.append({'product':p['id'],'path':str(f.relative_to(ROOT).as_posix()),'sha256':sha(f),'kind':spec['kind'],'selection':spec.get('select_functions','whole file except generated type blocks'),'result':r})
    if p.get('root'):
        # Local pin plus git-object comparison protects the read-only source baseline.
        try:
            head=subprocess.check_output(['git','-C',str(ROOT/p['root']),'rev-parse','HEAD'],text=True,stderr=subprocess.STDOUT).strip()
            check(head==p['commit'],'Pinned commit '+p['id'])
            dirty=subprocess.check_output(['git','-C',str(ROOT/p['root']),'diff','--name-only','HEAD','--',*[str(Path(s['path']).relative_to(p['root'])).replace('\\','/') for s in p['files']]],text=True,stderr=subprocess.STDOUT).strip()
            check(not dirty,'Measured tracked files unchanged '+p['id'])
            pins.append({'product':p['id'],'head':head,'selected_files_clean':True})
        except subprocess.CalledProcessError as e:
            pins.append({'product':p['id'],'expected':p['commit'],'git_check':'unavailable','detail':e.output[:300]})
    variants=[{'declaration_weight':w,**cocomo(logical+w*declarative)} for w in [0,.5,1,2]]
    check(all(variants[i]['jh_full_lifecycle_hypothesis']<=variants[i+1]['jh_full_lifecycle_hypothesis'] for i in range(3)),'Monotonic declaration sensitivity '+p['id'])
    products.append({'id':p['id'],'name':p['name'],'logical_units':logical,'declarative_units':declarative,'scenarios':variants,'main':variants[2],'scope':'Enveloppe native du témoin, suppléments recensés. Framework déjà disponible, construction complète du socle exclue. Pas charge observée ni estimation Spring.'})
# Inspect Frappe direct dependencies without pretending to measure the whole framework.
frappe=json.loads((A/'frappe-extraits.json').read_text(encoding='utf-8'));framework=[]
for file in frappe:
    for e in file['excerpts']:
        block=textwrap.dedent(e['code'])
        # Parse complete function including multiline signatures.
        tree=ast.parse(block)
        node=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)))
        block=ast.get_source_segment(block,node)
        r=python_count(block)
        framework.append({'file':file['id'],'url':file['url'],'name':e['name'],'start_line':e['start_line'],'end_line':e['end_line'],'logical_units':r['logical'],'source_blob_sha':file['git_blob_sha']})
check(len(framework)==18,'18 direct Frappe entry points retained')
# Counts are not added to the module effort: these libraries are reused, not rebuilt.
cfp=sum(p[k] for p in I['cosmic']['processes'] for k in ['E','R','W','X'])
check(cfp==26,'Witness COSMIC independent sum')
b=I['isbsg']
isbsg=[cfp*(b['hours_per_cfp']+delta)*b['size_factor']/7 for delta in [-b['spread'],0,b['spread']]]
check(b['size_band'][0]<=cfp<=b['size_band'][1],'ISBSG size correction applies to witness size band')
old=json.loads((ROOT/'audits/2026-10-30-master-data-calcul/resultats.json').read_text(encoding='utf-8'))
oldbase=cocomo(11326)
oldisbsg=old['isbsg']['main']['effort_jh'][1]
comparison={'previous_cocomo_ec_jh':oldbase['jh_elaboration_construction'],'full_lifecycle_cocomo_hypothesis_jh':oldbase['jh_full_lifecycle_hypothesis'],'isbsg_full_lifecycle_jh':oldisbsg,'before_gap_pct':100*(oldbase['jh_elaboration_construction']/oldisbsg-1),'after_phase_alignment_gap_pct':100*(oldbase['jh_full_lifecycle_hypothesis']/oldisbsg-1),'retained_estimate':None,'meaning':'Same broad phases under published default percentages; functions and staff populations still not fully reconciled. No adjustment to the ISBSG rate to force agreement.'}
dist=json.loads((ROOT/'audits/2026-10-30-master-data-calcul/repartitions-sources.json').read_text(encoding='utf-8'))
phase_weights=[.06,.24,.76,.12]
activities=[]
for row in dist['cocomo']['activities']:
    fraction=sum(w*p/100 for w,p in zip(phase_weights,row['percent_by_phase']))
    activities.append({'id':row['id'],'label':('Déploiement et préparation' if row['id']=='deployment' else row['label']),'fraction_of_ec_base':fraction,'fraction_of_full_lifecycle':fraction/1.18,'jh_previous_scenario_aligned':fraction*oldbase['jh_elaboration_construction']})
check(abs(sum(x['fraction_of_ec_base'] for x in activities)-1.18)<1e-9,'Activities conserve all four phase effort')
check(abs(sum(x['jh_previous_scenario_aligned'] for x in activities)-oldbase['jh_full_lifecycle_hypothesis'])<1e-8,'No additional effort from allocation')
dump('mesures-code.json',{'files':measurements,'pins':pins,'frappe_direct_dependencies':framework,'frappe_selected_logical_units':sum(x['logical_units'] for x in framework),'frappe_count_usage':'Structure evidence only; direct paths not exhaustive and not added as reconstruction effort.'})
out={'id':I['id'],'date':I['date'],'status':'diagnostic_completed_no_validated_flow_budget','products':products,'cosmic_witness_cfp':cfp,'isbsg_java_witness_jh':isbsg,'isbsg_python_estimate':None,'phase_alignment_previous_master_data':comparison,'full_lifecycle_activity_allocation':activities,'progress':{'products_with_cocomo_application':4,'products_with_observed_effort_validation':0,'candidate_contract_processes':7,'witness_scope_fully_equivalent_source_envelopes':False,'family_capabilities_examined_cumulative':6,'family_capabilities_total':6,'family_capabilities_with_complete_reconciled_effort':0,'all_core_capabilities_newly_validated':0},'uncertainty':{'source_provenance':'Reduced: 4 pinned native implementations, declarative portions visible.','framework_omission':'Reduced qualitatively: Frappe paths and other frameworks explicit; no complete residual Spring size.','activity_boundary':'Reduced: 4-phase convention and allocation executable. Staff and content mapping remain conditional.','numerical_prediction_interval':'Not narrowed: no observed effort, no calibrated declarative weights, different native stacks, very small witness.','flow_budget':'Unknown; no reduction percentage asserted.'},'retained':I['retained'],'checks':checks}
dump('resultats.json',out)
dump('verification.json',{'status':'arithmetic_passed','checks':len(checks),'active_files_preserved':len(baseline['files']),'visual_review':'pending'})
print(json.dumps({'products':[{'name':p['name'],'logical':p['logical_units'],'declarative':p['declarative_units'],'jh_ec':p['main']['jh_elaboration_construction'],'jh_four_phases':p['main']['jh_full_lifecycle_hypothesis']} for p in products],'cfp':cfp,'isbsg_java':isbsg,'previous_alignment':comparison,'frappe_direct_units':sum(x['logical_units'] for x in framework),'checks':len(checks)},ensure_ascii=False))
