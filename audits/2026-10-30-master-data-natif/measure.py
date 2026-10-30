from pathlib import Path
import ast,json,hashlib,sys,collections,re,xml.etree.ElementTree as ET
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"tmp/master-data-native-23/parser-deps"))
from tree_sitter import Language,Parser
import tree_sitter_java,tree_sitter_javascript,tree_sitter_typescript
PARSERS={".java":Parser(Language(tree_sitter_java.language())),".js":Parser(Language(tree_sitter_javascript.language())),".jsx":Parser(Language(tree_sitter_javascript.language())),".ts":Parser(Language(tree_sitter_typescript.language_typescript())),".tsx":Parser(Language(tree_sitter_typescript.language_tsx()))}
JAVA_EXTRA={"class_declaration","interface_declaration","enum_declaration","record_declaration","annotation_type_declaration","method_declaration","constructor_declaration","field_declaration","local_variable_declaration","package_declaration","import_declaration","catch_clause","switch_label"}
JS_EXTRA={"function_declaration","generator_function_declaration","class_declaration","lexical_declaration","variable_declaration","method_definition","interface_declaration","type_alias_declaration","enum_declaration","import_statement"}
XML_WRAPPERS={"odoo","data","tryton","domain-models","object-views","templates","template","views"}
def walk(root):
    stack=[root]
    while stack:
        node=stack.pop();yield node;stack.extend(node.named_children)
def measure(path):
    text=path.read_text(encoding="utf-8-sig");ext=path.suffix;program=declarations=0;details={}
    if ext==".py":
        generated_ranges=[]
        inside=False;lines=text.splitlines()
        for i,line in enumerate(lines):
            if "# begin: auto-generated types" in line:inside=True
            if inside:
                generated_ranges.append(i+1);lines[i]=""
            if "# end: auto-generated types" in line:inside=False
        parsed_text="\n".join(lines)
        # Python 3.14 PEP 758 syntax: normalize parentheses only for the Python 3.12 parser.
        parsed_text,normalizations=re.subn(r"(?m)^(\s*)except ([\w.]+(?:,\s*[\w.]+)+):",r"\1except (\2):",parsed_text)
        tree=ast.parse(parsed_text,filename=str(path))
        for n in ast.walk(tree):
            if isinstance(n,ast.stmt):
                # Docstrings are documentation, not executable expressions.
                if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):continue
                program+=1
        details={"convention":"AST Python : instructions, déclarations et imports ; docstrings et blocs typés auto-générés exclus","generated_lines_excluded":len(generated_ranges),"python314_except_normalizations":normalizations}
    elif ext in PARSERS:
        tree=PARSERS[ext].parse(text.encode())
        errors=[{"type":n.type,"row":n.start_point.row+1} for n in walk(tree.root_node) if n.type=="ERROR" or n.is_missing]
        if errors:raise ValueError(json.dumps(errors[:8]))
        for n in walk(tree.root_node):
            t=n.type
            if ext==".java":
                if (t.endswith("_statement") and t not in {"empty_statement"}) or t in JAVA_EXTRA:program+=1
            else:
                if (t.endswith("_statement") and t not in {"empty_statement","export_statement"}) or t in JS_EXTRA:program+=1
                # JSX is declarative UI, not a second executable statement.
                if t in {"jsx_opening_element","jsx_self_closing_element"}:declarations+=1
        details={"convention":"Arbre syntaxique : instructions et déclarations ; JSX compté séparément"}
    elif ext==".xml":
        tree=ET.fromstring(text)
        removed_records=0
        # Instance records (country lists, sample products, etc.) are input data, not program declarations.
        for parent in list(tree.iter()):
            for child in list(parent):
                tag=child.tag.split("}")[-1]
                model=child.attrib.get("model","")
                if tag=="record" and model and (not model.startswith(("ir.","res.groups","res.group")) or model=="ir.message"):
                    parent.remove(child);removed_records+=1
        tags=collections.Counter()
        for n in tree.iter():
            tag=n.tag.split("}")[-1]
            if tag not in XML_WRAPPERS:declarations+=1;tags[tag]+=1
        details={"xml_tags":dict(tags),"seed_records_excluded":removed_records}
    elif ext==".html":
        class Counter(HTMLParser):
            def __init__(self):super().__init__();self.count=0
            def handle_starttag(self,tag,attrs):
                if tag not in {"html","head","body"}:self.count+=1
            def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)
        counter=Counter();counter.feed(text);declarations=counter.count
        details={"convention":"Un élément HTML source ; attributs et styles non recomptés"}
    elif ext==".json":
        d=json.loads(text);assert d.get("doctype")=="DocType"
        declarations=1+sum(len(d.get(k,[])) for k in ["fields","permissions","actions","links","states"])
        details={"doctype":d.get("name"),"fields":len(d.get("fields",[])),"child":bool(d.get("istable"))}
    else:raise ValueError(ext)
    return {"program_units":program,"declarative_units":declarations,"physical_lines":len(text.splitlines()),"details":details}
def main():
    m=json.loads((OUT/"manifest.json").read_text(encoding="utf-8"))
    rows=[];errors=[]
    for r in m["files"]:
        path=ROOT/m["repos"][r["repo"]]["root"]/r["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest()==r["sha256"]
        try:rows.append({**r,**measure(path)})
        except Exception as e:errors.append({"repo":r["repo"],"path":r["path"],"error":str(e)})
    summary={}
    for product in ["erpnext","odoo","tryton","axelor"]:
        subset=[r for r in rows if r["product"]==product]
        summary[product]={"files":len(subset),"program_units":sum(r["program_units"] for r in subset),"declarative_units":sum(r["declarative_units"] for r in subset),"physical_lines":sum(r["physical_lines"] for r in subset),"by_layer":{layer:{"files":sum(r["layer"]==layer for r in subset),"program_units":sum(r["program_units"] for r in subset if r["layer"]==layer),"declarative_units":sum(r["declarative_units"] for r in subset if r["layer"]==layer)} for layer in ["reference","platform"]},"largest_files":[{k:r[k] for k in ["repo","path","program_units","declarative_units"]} for r in sorted(subset,key=lambda r:r["program_units"]+r["declarative_units"],reverse=True)[:12]]}
    result={"summary":summary,"errors":errors,"files":rows,"counting_status":"proxy de taille logique ; convention reproductible, non calibrée sur les quatre technologies","generated_code_policy":"Pas de Java généré depuis les domaines XML, ni de bundles JS compilés ; les générateurs sont hors frontière. Les déclarations sources sont conservées.","test_policy":"Tests de référence exclus de la taille produit ; effort de vérification inclus par le modèle COCOMO, pas ajouté après."}
    (OUT/"measurements.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"summary":summary,"errors":errors},ensure_ascii=False))
if __name__=="__main__":main()
