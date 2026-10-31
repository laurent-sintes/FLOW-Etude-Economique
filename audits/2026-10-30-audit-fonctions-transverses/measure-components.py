"""Freeze coherent professional components, without measuring generated bundles or tests."""
from pathlib import Path
import ast,collections,hashlib,importlib.util,json,re,subprocess,sys
R=Path.cwd();O=R/'audits/2026-10-30-audit-fonctions-transverses';sys.path.insert(0,str(R/'tmp/master-data-native-23/parser-deps'))
spec=importlib.util.spec_from_file_location('counter',R/'audits/2026-10-30-master-data-natif/measure.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
repos=json.loads((R/'audits/2026-10-30-audit-comptage-cocomo/source-inventory.json').read_text(encoding='utf-8'))['repos'];ev=json.loads((O/'evidence.json').read_text(encoding='utf-8'))
groups={
 'process-studio':{'label':'Studio de processus, publication et adaptation Temporal','purpose':'business-runtime','functions':['process-studio'],'paths':{'frappe':['frappe/public/js/workflow_builder','frappe/workflow/doctype/workflow','frappe/model/workflow.py'],'studio':['react/bpm/src/BPMN','react/bpm/src/components','react/bpm/src/services','react/bpm/src/context','react/bpm/src/hooks','react/bpm/src/utils','src/main/java/com/axelor/studio/bpm/service','src/main/java/com/axelor/studio/bpm/web']}},
 'human-forms':{'label':'Portail des tâches et studio de formulaires','purpose':'business-runtime','functions':['forms'],'paths':{'frappe':['frappe/public/js/form_builder','frappe/workflow/doctype/workflow_action','frappe/public/js/frappe/form'],'odoo':['addons/web/static/src/views/form'],'tryton':['sao/src/view/form.js'],'platform':['axelor-front/src/views/form'],'studio':['react/studio/src/Editor','react/studio/src/Properties','react/studio/src/Panels','react/studio/src/services','react/studio/src/store','react/studio/src/helpers']}},
 'analytics-mining':{'label':'Pilotage métier, tableaux de bord et Process Mining','purpose':'business-runtime','functions':['analytics','process-mining'],'paths':{'frappe':['frappe/desk/doctype/dashboard','frappe/desk/doctype/dashboard_chart','frappe/desk/doctype/dashboard_chart_source','frappe/public/js/frappe/views/dashboard','frappe/desk/query_report.py'],'odoo':['addons/web/static/src/views/graph','addons/web/static/src/views/pivot'],'tryton':['sao/src/view/graph.js'],'platform':['axelor-front/src/views/dashboard']}},
 'admin-security':{'label':'Administration du produit, habilitations et sécurité','purpose':'it-complement','functions':['backoffice','identities','permissions','settings','application-security'],'paths':{'frappe':['frappe/desk/doctype/workspace','frappe/core/doctype/user','frappe/core/doctype/role','frappe/core/doctype/role_profile','frappe/core/doctype/system_settings','frappe/permissions.py','frappe/auth.py'],'odoo':['addons/web/static/src/webclient','odoo/addons/base/models/res_users.py','odoo/addons/base/models/res_config.py','odoo/addons/base/models/ir_access.py'],'tryton':['sao/src/tab.js','trytond/trytond/res/user.py','trytond/trytond/ir/model.py','trytond/trytond/ir/configuration.py','trytond/trytond/security.py'],'platform':['axelor-front/src/layout','axelor-core/src/main/java/com/axelor/auth','axelor-core/src/main/java/com/axelor/meta/MetaPermissions.java','axelor-core/src/main/java/com/axelor/app/AppSettings.java']}},
 'operations-lifecycle':{'label':'Traitements, audit, purges, sauvegardes et migrations','purpose':'it-complement','functions':['audit-technical','jobs','job-console','retention','backup','upgrades','diagnostics'],'paths':{}},
 'data-services':{'label':'Imports, documents, notifications et langues','purpose':'it-complement','functions':['bulk-data','notifications','documents','internationalization'],'paths':{'frappe':['frappe/core/doctype/data_import','frappe/public/js/frappe/data_import','frappe/core/doctype/file','frappe/public/js/frappe/file_uploader','frappe/email/doctype/email_queue'],'odoo':['addons/base_import/models/base_import.py','addons/base_import/static/src'],'tryton':['trytond/trytond/ir/export.py','trytond/trytond/ir/attachment.py','modules/notification_email/notification.py'],'platform':['axelor-core/src/main/java/com/axelor/data','axelor-core/src/main/java/com/axelor/mail','axelor-core/src/main/java/com/axelor/meta/MetaFiles.java','axelor-core/src/main/java/com/axelor/i18n']}}
}
# Final boundary review: administrative views and operational implementations, not only controllers.
groups['operations-lifecycle']['paths']={
 'platform':['axelor-core/src/main/java/com/axelor/quartz','axelor-core/src/main/java/com/axelor/db/audit','axelor-core/src/main/java/com/axelor/meta/loader','axelor-core/src/main/resources/views/Schedules.xml','axelor-core/src/main/resources/domains/MetaSchedule.xml','axelor-core/src/main/resources/domains/AuditLog.xml'],
 'frappe':['frappe/core/doctype/scheduled_job_log','frappe/core/doctype/scheduled_job_type','frappe/core/doctype/rq_job','frappe/core/doctype/error_log','frappe/core/doctype/log_settings','frappe/core/doctype/version','frappe/core/doctype/activity_log']}
for name in ['User','Group','Permission','MetaPermission','Role','Team','MFA','UserToken']:
 for folder in ['views','domains']:groups['admin-security']['paths']['platform'].append('axelor-core/src/main/resources/'+folder+'/'+name+'.xml')
for folder in ['views','domains']:
 for name in ['WkfModel','WkfProcess','WkfProcessConfig','WkfTaskConfig','WkfInstance','WkfMigration','WkfInstanceVariable','WkfInstanceMigrationHistory','WkfProcessUpdate']:
  groups['process-studio']['paths']['studio'].append('src/main/resources/'+folder+'/'+name+'.xml')
groups['supply-workbenches']={'label':'Ateliers visuels de planification et de décision','purpose':'business-runtime','functions':['analytics'],'paths':{'frappe':['frappe/public/js/frappe/views/calendar','frappe/public/js/frappe/views/kanban'],'odoo':['addons/web/static/src/views/calendar','addons/web/static/src/views/kanban'],'tryton':['sao/src/view/calendar.js'],'platform':['axelor-front/src/views/calendar','axelor-front/src/views/kanban']}}

# Complete each perimeter with all previously inspected entry points for these functions.
for g in groups.values():
 for f in ev['families']:
  if f['id'] in g['functions']:
   for e in f['evidence']:g['paths'].setdefault(e['repo'],[]).append(e['path'])
exts={'.py','.java','.js','.jsx','.ts','.tsx','.vue','.xml','.json','.html'};files={};missing=[];excluded=[]
def measure(p):
 if p.suffix!='.vue':
  if p.suffix in ('.jsx','.tsx') and re.search(r'\bin=\{',p.read_text(encoding='utf-8-sig')):
   text=p.read_text(encoding='utf-8-sig');fixed=re.sub(r'\bin=\{','inX={',text);tree=c.PARSERS[p.suffix].parse(fixed.encode());assert not tree.root_node.has_error,str(p);program=decl=0
   for n in c.walk(tree.root_node):
    if (n.type.endswith('_statement') and n.type not in {'empty_statement','export_statement'}) or n.type in c.JS_EXTRA:program+=1
    if n.type in {'jsx_opening_element','jsx_self_closing_element'}:decl+=1
   return dict(program_units=program,declarative_units=decl,physical_lines=len(text.splitlines()),details={'normalization':'JSX property in renamed inX only in parser memory; no source modification'})
  return c.measure(p)
 text=p.read_text(encoding='utf-8-sig');program=decl=0
 for match in re.finditer(r'<script[^>]*>([\s\S]*?)</script>',text):
  script=match.group(1);tree=c.PARSERS['.js'].parse(script.encode());assert not tree.root_node.has_error,str(p)
  for n in c.walk(tree.root_node):
   if (n.type.endswith('_statement') and n.type not in {'empty_statement','export_statement'}) or n.type in c.JS_EXTRA:program+=1
 templates=re.findall(r'<template[^>]*>([\s\S]*?)</template>',text)
 for tpl in templates:decl+=len(re.findall(r'<[A-Za-z][\w.-]*(?:\s|/?>)',tpl))
 return dict(program_units=program,declarative_units=decl,physical_lines=len(text.splitlines()),details={'convention':'Vue: AST du script et balises du template; styles exclus, déclaratif proxy non calibré.'})
for gid,g in groups.items():
 for repo,paths in g['paths'].items():
  root=R/repos[repo]['root']
  for path in sorted(set(paths)):
   target=root/path
   if not target.exists():missing.append((gid,repo,path));continue
   for p in sorted(target.rglob('*') if target.is_dir() else [target]):
    if not p.is_file() or p.suffix not in exts:continue
    rel=p.relative_to(root).as_posix();name=p.name
    if any(part in {'tests','test','__tests__','node_modules','dist','build','images'} for part in p.parts) or name.startswith('test_') or name.endswith(('.test.js','.test.ts','.spec.js','.spec.ts','Test.java','.bundle.js')):continue
    if p.suffix=='.json':
     try:
      if json.loads(p.read_text(encoding='utf-8-sig')).get('doctype')!='DocType':continue
     except (ValueError,AttributeError):continue
    key=repo+':'+rel
    if key in files:
     files[key].setdefault('consumed_by',[])
     if gid!=files[key]['group'] and gid not in files[key]['consumed_by']:files[key]['consumed_by'].append(gid)
     continue
    try:m=measure(p)
    except Exception as e:excluded.append(dict(repo=repo,path=rel,error=str(e)));continue
    files[key]=dict(repo=repo,product='erpnext' if repo=='frappe' else 'axelor' if repo in ('platform','studio') else repo,path=rel,group=gid,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),commit=repos[repo]['commit'],url='https://github.com/'+repos[repo]['repository']+'/blob/'+repos[repo]['commit']+'/'+rel,**m)
# Close relative JavaScript/Vue imports. External packages remain provided kernels.
frontier=list(files);seen=set(frontier);external=set();closure=[]
while frontier:
 key=frontier.pop();x=files[key];p=R/repos[x['repo']]['root']/x['path']
 if p.suffix not in {'.js','.jsx','.ts','.tsx','.vue'}:continue
 text=p.read_text(encoding='utf-8-sig')
 for ref in re.findall(r"(?:from\s*|import\s*|require\s*\()['\"]([^'\"]+)['\"]",text):
  if not ref.startswith('.'):
   external.add(ref.split('/')[0]);continue
  base=p.parent/ref;options=[base]+[Path(str(base)+e) for e in ['.js','.jsx','.ts','.tsx','.vue']]+[base/('index'+e) for e in ['.js','.jsx','.ts','.tsx','.vue']]
  target=next((t.resolve() for t in options if t.is_file() and t.suffix in {'.js','.jsx','.ts','.tsx','.vue'}),None)
  if target is None:continue
  root=(R/repos[x['repo']]['root']).resolve();assert target.is_relative_to(root)
  rel=target.relative_to(root).as_posix();newkey=x['repo']+':'+rel
  if newkey in seen:continue
  seen.add(newkey)
  try:m=measure(target)
  except Exception as e:excluded.append(dict(repo=x['repo'],path=rel,error=str(e)));continue
  row=dict(repo=x['repo'],product=x['product'],path=rel,group=x['group'],sha256=hashlib.sha256(target.read_bytes()).hexdigest(),commit=x['commit'],url='https://github.com/'+repos[x['repo']]['repository']+'/blob/'+x['commit']+'/'+rel,relative_import_of=key,**m);files[newkey]=row;frontier.append(newkey);closure.append(newkey)

# Each file has exactly one owner. Integrity is checked against pinned repository blobs.
for repo in repos:
 rr=[x for x in files.values() if x['repo']==repo]
 if not rr:continue
 q=''.join(x['commit']+':'+x['path']+'\n' for x in rr);result=subprocess.run(['C:/Program Files/Git/cmd/git.exe','-C',str(R/repos[repo]['root']),'cat-file','--batch'],input=q.encode(),capture_output=True,check=True).stdout;pos=0
 for x in rr:
  end=result.index(b'\n',pos);header=result[pos:end].decode();assert not header.endswith('missing'),x['path'];n=int(header.rsplit(' ',1)[1]);raw=result[end+1:end+1+n];pos=end+n+2;actual=(R/repos[repo]['root']/x['path']).read_bytes();assert raw.replace(b'\r\n',b'\n')==actual.replace(b'\r\n',b'\n'),x['path'];x['pinned_equal']=True
summary={gid:{p:dict(files=sum(x['group']==gid and x['product']==p for x in files.values()),program=sum(x['program_units'] for x in files.values() if x['group']==gid and x['product']==p),declarative=sum(x['declarative_units'] for x in files.values() if x['group']==gid and x['product']==p)) for p in ['erpnext','odoo','tryton','axelor']} for gid in groups}
data=dict(status='measured_analogues_not_project_actuals',repos=repos,groups=groups,files=list(files.values()),summary=summary,missing_paths=missing,excluded=excluded,counting='AST logical proxy + separate generator/UI declarations; not physical SLOC. Vue/JSX/TS and declarative weights need sensitivity, not USC certification.',relative_import_closure=closure,external_packages=sorted(external),scope='Coherent component packages; external libraries called by these components are provided, not recursively rebuilt. No claim of exhaustive transitive code closure.')
(O/'components-measured.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(files=len(files),missing=missing,excluded=excluded,summary=summary),ensure_ascii=False))
