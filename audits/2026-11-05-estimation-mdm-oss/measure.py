from pathlib import Path
import sys,json,hashlib,subprocess,re,xml.etree.ElementTree as ET
import base64,gzip
ROOT=Path.cwd();W=ROOT/'tmp/mdm-cocomo-2026-11-05'
sys.path[:0]=[str(W/'parser-deps'),str(ROOT/'tmp/master-data-native-23/parser-deps')]
from tree_sitter import Language,Parser
import tree_sitter_java,tree_sitter_javascript,tree_sitter_php
P={'.java':Parser(Language(tree_sitter_java.language())),'.js':Parser(Language(tree_sitter_javascript.language())),'.php':Parser(Language(tree_sitter_php.language_php()))}
EXTRA={'.java':{'class_declaration','interface_declaration','enum_declaration','record_declaration','annotation_type_declaration','method_declaration','constructor_declaration','field_declaration','local_variable_declaration','package_declaration','import_declaration','catch_clause','switch_label'},'.js':{'function_declaration','generator_function_declaration','class_declaration','lexical_declaration','variable_declaration','method_definition','import_statement'},'.php':{'class_declaration','interface_declaration','trait_declaration','enum_declaration','method_declaration','function_definition','property_declaration','const_declaration','namespace_use_declaration','namespace_definition','use_declaration'}}
def walk(n):
 stack=[n]
 while stack:
  n=stack.pop();yield n;stack.extend(n.named_children)
def measure(raw,ext):
 if ext=='.sql':
  s=raw.decode('utf-8-sig');s=re.sub(r'/\*.*?\*/|--[^\n]*','',s,flags=re.S);s=re.sub(r"'(?:''|[^'])*'","''",s)
  return dict(program_units=s.count(';')+1,declarative_units=0,parse_errors=[])
 if ext in {'.xml','.xsd'}:
  root=ET.fromstring(raw.decode('utf-8-sig'))
  nodes=list(root.iter());entries=[n for n in nodes if n.tag.split('}')[-1]=='entry']
  if entries:return dict(program_units=len(entries),declarative_units=0,parse_errors=[])
  return dict(program_units=0,declarative_units=sum(n.tag.split('}')[-1] not in {'schema','annotation','documentation'} for n in nodes),parse_errors=[])
 if ext=='.json':
  d=json.loads(raw.decode('utf-8-sig'))
  def leaves(d):
   if isinstance(d,dict):return sum(leaves(v) for v in d.values())
   if isinstance(d,list):return sum(leaves(v) for v in d)
   return 1
  return dict(program_units=0,declarative_units=leaves(d),parse_errors=[])
 tree=P[ext].parse(raw);nodes=list(walk(tree.root_node));err=[n.start_point.row+1 for n in nodes if n.type=='ERROR' or n.is_missing]
 return dict(program_units=sum((n.type.endswith('_statement') and n.type not in {'empty_statement','export_statement','text_interpolation'}) or n.type in EXTRA[ext] for n in nodes),declarative_units=0,parse_errors=err)
def select(repo,p):
 if any(x in p.lower().split('/') for x in ('tests','test','vendors','vendor','generated','migrations','i18n','translation','translations')):return None
 if repo=='pimcore-admin':
  if re.search(r'(wysiwyg|video|image|asset|document|hotspot|geopoint|geobounds|rgba|slider|password|urlslug)',p,re.I):return None
  if p.startswith('public/js/pimcore/object/') or p.startswith('public/js/pimcore/settings/object/'):return 'model'
  if p.startswith('public/js/pimcore/element/versions/'):return 'lifecycle'
 if repo=='unidata':
  if p.startswith('backend/src/main/java/com/unidata/mdm/backend/service/wf/') and any(s in p for s in ('UserManager','UserIdentity','GroupManager','GroupIdentity')):return None
  if p.startswith('common/src/main/resources/schemas/') and any(s in p for s in ('meta-','matching-','classifiers-')):return 'model'
  if p.startswith('backend/src/main/java/com/unidata/mdm/backend/po/') and '/initializer/' not in p and '/job/' not in p and not any(s in p for s in ('Binary','CharacterLarge','Measurement')):return 'lifecycle'
  if p.startswith('backend/src/main/java/com/unidata/mdm/backend/dao/') and any(s in p for s in ('Data','Matching','Etalon','Origin','Meta','Relation','DQ','Cluster')):return 'lifecycle'
  if p.startswith('backend/src/main/resources/db/') and Path(p).name in {'records-sql.xml','relations-sql.xml','vistory-sql.xml','matching-sql.xml','cluster-sql.xml','meta-sql.xml','meta-draft-sql.xml','classifier-data-sql.xml','classifiers-sql.xml','import-data-job-sql.xml'}:return 'lifecycle'
 if repo=='atrocore':
  if not p.startswith(('app/Atro/','client/src/')):return None
  name=Path(p).stem
  if re.search(r'(Matching|MatchedRecord|Cluster|Consolidation|DataLineage)',p,re.I):return 'identity'
  if 'DataPipeline' in p or '/data-pipeline/' in p:return 'ingestion'
  if name in {'Entity','EntityField','Attribute','AttributePanel','Classification','ClassificationAttribute','EntityUniqueIndex'} and '/Core/' not in p:return 'model'
  if '/views/admin/entity-manager/' in p or '/Core/EntityTypeHandlers/' in p:return 'model'
  if name in {'Action','ActionExecution','ActionHistoryRecord','ActionManager','NotificationRule','NotificationTemplate'} or '/Core/EntityMethods/' in p:return 'lifecycle'
  if re.search(r'(Webhook|Connection)',name):return 'distribution'
 if repo=='unidata':
  base='backend/src/main/java/com/unidata/mdm/backend/'
  if p.startswith(base):
   q=p[len(base):]
   for prefix,g in [('service/model/','model'),('service/matching/','identity'),('service/cleanse/','ingestion'),('service/wf/','lifecycle'),('service/integration/','distribution'),('service/notification/','distribution'),('service/data/','lifecycle')]:
    if q.startswith(prefix):return g
   if q.startswith('api/rest/') and '/dto/' not in q:
    if re.search('Match|Cluster',q):return 'identity'
    if re.search('Data|Meta|Entity|Classifier|Model',q):return 'model' if re.search('Meta|Model|Entity',q) else 'lifecycle'
  base='frontend/app/view/'
  if p.startswith(base):
   q=p[len(base):]
   for prefix,g in [('admin/entity/','model'),('admin/schema/','model'),('admin/dataquality/','ingestion'),('admin/duplicates/','identity'),('admin/sourcesystems/','model'),('steward/cluster/','identity'),('steward/dataimport/','ingestion'),('steward/dataentity/','lifecycle')]:
    if q.startswith(prefix):return g
 if repo=='pimcore':
  if p.startswith('models/DataObject/ClassDefinition/'):
   allowed={'BooleanSelect','Checkbox','Date','Datetime','Input','Numeric','Select','Multiselect','ManyToOneRelation','ManyToManyRelation','ManyToManyObjectRelation','QuantityValue','CalculatedValue','Localizedfields','Classificationstore','Table','Textarea','Url'}
   if '/Data/' not in p or Path(p).stem in allowed:return 'model'
  if p in {'models/DataObject/ClassDefinition.php','models/DataObject/Concrete.php','models/DataObject/AbstractObject.php'}:return 'model'
  if p.startswith(('models/Version/','models/Schedule/')) or p=='models/Version.php':return 'lifecycle'
  if p.startswith(('lib/Workflow/','bundles/CoreBundle/Workflow/')):return 'lifecycle'
 if repo=='pimcore-cmf' and p.startswith('src/'):
  if any(p.startswith('src/'+s) for s in ('CustomerDuplicatesService/','CustomerMerger/','DataSimilarityMatcher/','DuplicatesIndex/','CustomerSaveValidator/','DataValidator/','DataTransformer/')):return 'identity' if not p.startswith(('src/DataValidator/','src/DataTransformer/')) else 'ingestion'
 if repo=='pimcore-importer' and p.startswith('src/'):
  if any(p.startswith('src/'+s+'/') for s in ('DataSource','Mapping','Processing','Queue','Resolver','Settings','Tool')):return 'ingestion'
 if repo=='pimcore-datahub' and p.startswith('src/'):
  if any(p.startswith('src/'+s+'/') for s in ('Configuration','Model','Service')):return 'distribution'
  if p.startswith('src/GraphQL/') and ('DataObject' in p or Path(p).name in {'PermissionInfoTrait.php','WorkspaceHelper.php'}):return 'distribution'
 return None

def main():
 repos={};files=[];rejected=[]
 for repo in ('atrocore','unidata','pimcore','pimcore-cmf','pimcore-importer','pimcore-datahub','pimcore-admin'):
  folder=W/repo;sha=subprocess.check_output(['git','-C',str(folder),'rev-parse','HEAD'],text=True).strip();date=subprocess.check_output(['git','-C',str(folder),'show','-s','--format=%cs'],text=True).strip()
  repos[repo]=dict(commit=sha,date=date,origin=subprocess.check_output(['git','-C',str(folder),'remote','get-url','origin'],text=True).strip())
  paths=subprocess.check_output(['git','-C',str(folder),'ls-files'],text=True).splitlines()
  for p in paths:
   ext=Path(p).suffix
   if ext not in P and ext not in {'.json','.xml','.xsd'}:continue
   group=select(repo,p)
   prototype=(repo=='atrocore' and p in {'app/Atro/Resources/metadata/entityDefs/Account.json','app/Atro/Resources/metadata/entityDefs/Address.json','app/Atro/Resources/metadata/entityDefs/Contact.json'}) or (repo=='pimcore-cmf' and p=='install/class_source/optional/class_Customer_export.json')
   if prototype:group='family_prototype'
   if not group:continue
   raw=(folder/p).read_bytes();row=dict(repo=repo,path=p,group=group,sha256=hashlib.sha256(raw).hexdigest(),**measure(raw,ext))
   (rejected if row['parse_errors'] else files).append(row)
 # Retain each latest non-dropped stored function once, not all historical migrations.
 latest={}
 folder=W/'unidata';paths=sorted((folder/'database/src/main/resources/db/migration').rglob('*.sql'),key=lambda p:tuple(int(n) for n in re.match(r'V([0-9.]+)',p.name).group(1).split('.')) if re.match(r'V([0-9.]+)',p.name) else ())
 for path in paths:
  try:text=path.read_text(encoding='utf-8-sig')
  except UnicodeDecodeError:text=path.read_text(encoding='cp1251')
  relative=path.relative_to(folder).as_posix()
  events=[]
  for m in re.finditer(r'(?is)create\s+(?:or\s+replace\s+)?function\s+([\w.]+)\s*\(.*?\)\s*returns\s+.*?\bas\s+(\$[\w]*\$)(.*?)\2[^;]*;',text):events.append((m.start(),'create',m))
  for m in re.finditer(r'(?is)drop\s+function\s+(?:if\s+exists\s+)?([\w.]+)\s*\([^;]*;',text):events.append((m.start(),'drop',m))
  for _,kind,m in sorted(events,key=lambda e:e[0]):
   key=m.group(1).lower()
   if kind=='drop':latest.pop(key,None)
   else:latest[key]=(relative,m.group(0),text.count('\n',0,m.start())+1,hashlib.sha256(path.read_bytes()).hexdigest())
 for name,(path,fragment,line,source_sha) in latest.items():
  # Installation/administration migrations are not target record management.
  if not any(s in name for s in ('record','relation','origin','etalon','vistory','timeline','match','cluster','classifier')):continue
  raw=fragment.encode('utf-8');files.append(dict(repo='unidata',path=path,fragment=name,start_line=line,group='lifecycle',sha256=hashlib.sha256(raw).hexdigest(),source_sha256=source_sha,**measure(raw,'.sql')))
 out=dict(version=1,repos=repos,files=files,rejected=rejected,sql_resolution='Latest definition per function name after drops in numeric migration order. Overloads and successful database deployment are not established by this static review.')
 (W/'inventory.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 for repo in repos:
  subset=[f for f in files if f['repo']==repo];print(repo,repos[repo]['commit'],len(subset),'program',sum(f['program_units'] for f in subset),'declarative',sum(f['declarative_units'] for f in subset))
 print('parse errors',len(rejected),[(f['repo'],f['path'],f['parse_errors'][:3]) for f in rejected][:10])
def verify_archive():
 audit=Path(__file__).resolve().parent
 inventory=json.loads((audit/'measurements.json').read_text(encoding='utf-8'))
 code=json.loads((audit/'code.json').read_text(encoding='utf-8'))
 files=json.loads(gzip.decompress(base64.b64decode(code['data'])))
 for r in inventory['files']:
  key=r['repo']+'/'+r['path']+('#'+r['fragment'] if r.get('fragment') else '')
  raw=base64.b64decode(files[key]);assert hashlib.sha256(raw).hexdigest()==r['sha256'],key
  measured=measure(raw,Path(r['path']).suffix)
  assert all(measured[k]==r[k] for k in ('program_units','declarative_units','parse_errors')),key
 print(json.dumps(dict(status='passed',remeasured=len(inventory['files']),network=False)))

if __name__=='__main__':
 if '--verify-archive' in sys.argv:verify_archive()
 else:main()

