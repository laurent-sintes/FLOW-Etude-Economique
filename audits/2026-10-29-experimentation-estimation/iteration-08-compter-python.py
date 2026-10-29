from pathlib import Path
import ast,json,hashlib,subprocess
ROOT=Path.cwd(); OUT=ROOT/'audits/2026-10-29-experimentation-estimation'
SPECS=[
('PY-UOM','tryton','tmp/tryton-code-audit-2026-10-28/modules/product/uom.py',[(185,285)]),
('PY-APPLICABLE','odoo','tmp/odoo20-audit/addons/product/models/product_pricelist_item.py',[(382,407),(488,544)]),
('PY-CARRIER','tryton','tmp/tryton-code-audit-2026-10-28/modules/carrier/carrier.py',[(11,120)]),
('PY-IMPORT','tryton','tmp/tryton-code-audit-2026-10-28/trytond/trytond/model/modelstorage.py',[(1141,1472)])]
files=[]
for id,repo,rel,ranges in SPECS:
 raw=(ROOT/rel).read_bytes(); text=raw.decode('utf-8-sig'); tree=ast.parse(text)
 units=[]
 for n in ast.walk(tree):
  if not isinstance(n,ast.stmt) or not any(a<=n.lineno<=b for a,b in ranges):continue
  if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):continue
  typ='declaration' if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef,ast.Import,ast.ImportFrom)) else 'statement'
  units.append({'line':n.lineno,'end_line':n.end_lineno,'kind':type(n).__name__,'category':typ})
 files.append({'id':id,'repository_id':repo,'cache_path':rel,'sha256':hashlib.sha256(raw).hexdigest(),'ranges':ranges,'logical_units':len(units),'declarations':sum(x['category']=='declaration' for x in units),'units':sorted(units,key=lambda x:x['line']),'read_status':'code lu par assistant; blocs entiers au dela des seules lignes de preuve07','use':'analogie fonctionnelle et ordre de taille algorithmique seulement; aucun ratio de langage applique'})
repos=[('odoo','tmp/odoo20-audit','299075f17026b830a9755f3c43f3e83143995946'),('tryton','tmp/tryton-code-audit-2026-10-28','e011222dc305c431677e586706fd241dffe02236'),('axelor-suite','tmp/oss-audit-axelor','e7cbea53bae88d2540f59a70b09bf0f326f1022e'),('axelor-platform','tmp/oss-audit-axelor-platform','96caf51eb97fbab7750b7dadf10a371a55a490a3')]
checks=[]
for repo,rel,expected in repos:
 observed=subprocess.check_output(['git','-C',str(ROOT/rel),'rev-parse','HEAD'],text=True).strip()
 changed=subprocess.check_output(['git','-C',str(ROOT/rel),'diff','--name-only','HEAD'],text=True).splitlines()
 assert observed==expected,(repo,observed)
 checks.append({'id':repo,'path':rel,'expected_commit':expected,'observed_commit':observed,'tracked_files_changed':changed})
out={'convention':'PY_AST_STMT_V1: une instruction ast.stmt par noeud, y compris entetes if/for/try/fonctions/classes. Commentaires, docstrings et lignes vides exclus; expressions/collections multiligne restent une instruction. Decorateurs non comptes ici. Convention proxy logique, pas une conversion en Java.','files':files,'repository_checks':checks}
(OUT/'iteration-08-python-mesures.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps([{k:f[k] for k in ['id','logical_units','declarations','sha256']} for f in files],indent=2))
