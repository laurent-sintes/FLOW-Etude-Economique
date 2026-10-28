from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
from pypdf import PdfReader
import re,hashlib,json,zipfile
root=Path(__file__).resolve().parent.parent
p=root/'outputs/01a1530f-f378-7fd1-9654-468c9b2141b6/FLOW_Dossier_client_2026-10-21'
expected='3e03e49dc0938bb14db38aaa88f67fa010f278f32297ecf0bd81b51a8cd77762'
original=p.parent/'FLOW_Make_abaques_et_prix_France_v4.xlsx'
assert hashlib.sha256(original.read_bytes()).hexdigest()==expected
assert hashlib.sha256((p/'FLOW_Comparaison.xlsx').read_bytes()).hexdigest()==expected
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):self.links.extend(v for k,v in attrs if k in ['href','src'])
links=0;web=set();errors=[]
for file in p.rglob('*.html'):
 text=file.read_text(encoding='utf-8'); parsed=Links();parsed.feed(text)
 for bad in ['1,1845','1,152175','726 JH','376,975','472 JH','440 JH','Service annuel</strong>','C:/Dev/','C:\\Users\\','tmp/synvance','ancienne feuille','version détaillée archivée','quatre retouches','sept cellules']:
  assert bad not in text,(file.name,bad)
 for link in parsed.links:
  if urlsplit(link).scheme in ['http','https']:web.add(link);continue
  target=(file.parent/unquote(link.split('#')[0])).resolve()
  if not target.exists():errors.append((file.name,link))
  assert target.is_relative_to(p.resolve()),(file,link)
  links+=1
assert not errors,errors
pdf=PdfReader(p/'FLOW_Etude_decision.pdf');full='\n'.join(page.extract_text() for page in pdf.pages)
for val in ['41,96','50,69','40,97','1,75','2,54','2,56']:assert val in full,val
for page in pdf.pages:
 for a in page.get('/Annots',[]):
  action=a.get_object().get('/A',{})
  uri=action.get('/URI','')
  if uri and not uri.startswith('http'):assert (p/unquote(uri)).exists(),uri
report={'status':'PASS','unchanged_workbook_sha256':expected,'html_pages':len(list(p.rglob('*.html'))),'local_links_checked':links,'external_reference_urls':len(web),'external_note':'Contrôle local uniquement ; voir les rapports de vérification publique distincts dans tmp.','pdf_pages':len(pdf.pages),'source_files':len(list((p/'sources').rglob('*.*')))}
(root/'tmp/client_package_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
zip_path=p.with_suffix('.zip')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for file in sorted(p.rglob('*')):
  if file.is_file():z.write(file,Path(p.name)/file.relative_to(p))
with zipfile.ZipFile(zip_path) as z:assert z.testzip() is None
print(json.dumps(report,ensure_ascii=False));print('ZIP',zip_path,zip_path.stat().st_size)
