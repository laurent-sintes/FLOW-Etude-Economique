from pathlib import Path
import json, hashlib, subprocess, fnmatch
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
GIT=r"C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe"
REPOS={
"erpnext":("tmp/master-data-native-23/erpnext","frappe/erpnext","ade850bbd6a7412e9994a9637d2c5c713771632a"),
"frappe":("tmp/master-data-native-23/frappe","frappe/frappe","2fcb9397a1f1da353b21e53d2f97ec56653acd02"),
"odoo":("tmp/odoo20-audit","odoo/odoo","299075f17026b830a9755f3c43f3e83143995946"),
"tryton":("tmp/tryton-code-audit-2026-10-28","tryton/tryton","e011222dc305c431677e586706fd241dffe02236"),
"axelor":("tmp/oss-audit-axelor","axelor/axelor-open-suite","e7cbea53bae88d2540f59a70b09bf0f326f1022e"),
"platform":("tmp/oss-audit-axelor-platform","axelor/axelor-open-platform","96caf51eb97fbab7750b7dadf10a371a55a490a3")}
groups=[]; missing=[]; files={}; skipped=[]
allowed={".py",".java",".js",".ts",".tsx",".jsx",".xml",".json",".html"}
excluded_parts={"tests","test","__tests__","__snapshots__","node_modules","i18n","locale","locales","translations","demo","demos","fixtures","patches","migration","migrations","generated","dist","build","static_lib","libs","owl2","fonts","icons"}
def eligible(p):
    if p.suffix not in allowed or any(x in excluded_parts for x in p.parts):return False
    n=p.name
    return not (n.startswith(("test_","conftest","__manifest__")) or n.endswith((".test.js",".test.ts",".spec.ts",".d.ts",".min.js")) or n in {"package.json","tsconfig.json"})
def add(product,repo,patterns,reason,layer):
    root=ROOT/REPOS[repo][0]; found=[]
    for pattern in patterns:
        matches=list(root.glob(pattern))
        if not matches: missing.append([repo,pattern])
        for m in matches:
            for p in ([m] if m.is_file() else m.rglob("*")):
                if not p.is_file():continue
                rel=p.relative_to(root)
                if not eligible(rel):continue
                # ERPNext/Frappe JSON must be native DocType metadata, not data fixtures.
                if p.suffix==".json":
                    try:d=json.loads(p.read_text(encoding="utf-8-sig"))
                    except Exception:continue
                    if not isinstance(d,dict) or d.get("doctype")!="DocType":continue
                key=(product,repo,rel.as_posix())
                if key not in files:
                    files[key]={"product":product,"repo":repo,"path":rel.as_posix(),"layer":layer,"reasons":[],"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
                if reason not in files[key]["reasons"]:files[key]["reasons"].append(reason)
                found.append(rel.as_posix())
    groups.append({"product":product,"repo":repo,"patterns":patterns,"reason":reason,"layer":layer,"matched_files":len(set(found))})
def dt(product,repo,module,names,reason,layer="reference"):
    add(product,repo,[f"{module}/doctype/{n}" for n in names.split()],reason,layer)
# Explicit comparison basket: records, variants, partners, conversions/packaging,
# catalog tariffs, locations and carrier/service references, native administration.
dt("erpnext","erpnext","erpnext/stock","item item_attribute item_attribute_value item_barcode item_customer_detail item_default item_lead_time item_manufacturer item_price item_quality_inspection_parameter item_reorder item_supplier item_tax item_variant item_variant_attribute item_variant_settings item_website_specification item_alternative price_list price_list_country uom_category uom_conversion_detail warehouse warehouse_type","Articles, variantes, tarifs, unités et sites")
dt("erpnext","erpnext","erpnext/setup","brand item_group uom uom_conversion_factor customer_group supplier_group territory terms_and_conditions party_type","Classifications et conditions de référence")
dt("erpnext","erpnext","erpnext/selling","customer customer_credit_limit industry_type party_specific_item product_bundle product_bundle_item supplier_number_at_customer","Clients et conditionnements composés")
dt("erpnext","erpnext","erpnext/buying","supplier customer_number_at_supplier","Fournisseurs")
dt("erpnext","erpnext","erpnext/accounts","shipping_rule shipping_rule_condition shipping_rule_country payment_term payment_terms_template payment_terms_template_detail","Services de livraison et conditions tarifaires")
add("erpnext","frappe",["frappe/contacts"],"Contacts et adresses natifs","reference")
add("erpnext","erpnext",["erpnext/controllers/item_variant.py","erpnext/utilities/product.py","erpnext/stock/get_item_details.py","erpnext/utilities/transaction_base.py","erpnext/controllers/queries.py"],"Calculs et consultations appelés par les référentiels, fichiers conservés entiers","reference")
add("erpnext","frappe",["frappe/model","frappe/database","frappe/query_builder","frappe/api","frappe/types","frappe/__init__.py","frappe/app.py","frappe/auth.py","frappe/boot.py","frappe/cache_manager.py","frappe/client.py","frappe/defaults.py","frappe/exceptions.py","frappe/handler.py","frappe/permissions.py","frappe/sessions.py","frappe/share.py","frappe/translate.py","frappe/modules"],"Persistance, métadonnées, API, permissions et chargement","platform")
dt("erpnext","frappe","frappe/core","doctype docfield docperm docshare custom_docperm role user user_permission has_role role_profile user_role_profile defaultvalue version deleted_document dynamic_link file data_export data_import data_import_log data_import_skipped_row data_import_value_mapping module_def language translation access_log audit_trail error_log","Administration, imports, historique et droits","platform")
add("erpnext","frappe",["frappe/custom/doctype/custom_field","frappe/custom/doctype/property_setter","frappe/desk/form","frappe/desk/listview.py","frappe/desk/reportview.py","frappe/desk/search.py","frappe/desk/treeview.py","frappe/desk/utils.py","frappe/desk/doctype_settings"],"Métadonnées, formulaires, listes, recherche et arbres","platform")
add("erpnext","frappe",["frappe/utils/"+n+".py" for n in "__init__ data dateutils caching csvutils xlsxutils diff file_manager formatters html_utils image jinja local logger messages nestedset number_format password password_strength response safe_exec background_jobs redis_wrapper redis_queue typing_validations user".split()],"Services utilitaires sélectionnés ; capacités supplémentaires internes conservées","platform")
add("erpnext","frappe",["frappe/public/js/frappe/"+n for n in "form list model ui utils data_import file_uploader doctype color_picker icon_picker phone_picker".split()]+["frappe/public/js/frappe/*.js"],"Interface native formulaire/liste, contrôles et navigation","platform")
# Odoo
add("odoo","odoo",["addons/product/models","addons/product/views","addons/product/wizard","addons/product/static/src","addons/uom/models","addons/uom/views"],"Produits, variantes, fournisseurs produits, tarifs et unités","reference")
add("odoo","odoo",["odoo/addons/base/models/res_partner.py","odoo/addons/base/models/res_country.py","odoo/addons/base/models/res_currency.py","odoo/addons/base/models/res_company.py","odoo/addons/base/views/res_partner_views.xml","odoo/addons/base/views/res_country_views.xml","odoo/addons/base/views/res_currency_views.xml","addons/contacts"],"Partenaires, adresses et référentiels géographiques","reference")
add("odoo","odoo",["addons/stock/models/stock_location.py","addons/stock/models/stock_warehouse.py","addons/stock/models/stock_package_type.py","addons/stock/models/stock_storage_category.py","addons/stock/views/stock_location_views.xml","addons/stock/views/stock_warehouse_views.xml","addons/stock/views/stock_package_type_view.xml","addons/stock/views/stock_storage_category_views.xml","addons/delivery/models/delivery_carrier.py","addons/delivery/models/delivery_price_rule.py","addons/delivery/models/delivery_zip_prefix.py","addons/delivery/views/delivery_carrier_views.xml"],"Sites, conditionnements et services de livraison ; fichiers natifs entiers","reference")
add("odoo","odoo",["odoo/orm","odoo/models","odoo/fields","odoo/api","odoo/http","odoo/modules","odoo/tools","odoo/service","odoo/sql_db.py","odoo/exceptions.py","odoo/netsvc.py"],"ORM, API, chargement et services natifs ; utilitaires conservés entiers","platform")
add("odoo","odoo",["odoo/addons/base/models/"+n+".py" for n in "ir_access ir_actions ir_attachment ir_binary ir_config_parameter ir_default ir_exports ir_fields ir_filters ir_http ir_logging ir_model ir_module ir_qweb ir_qweb_fields ir_sequence ir_ui_menu ir_ui_view res_groups res_groups_privilege res_users res_users_settings res_lang image_mixin avatar_mixin decimal_precision properties_base_definition properties_base_definition_mixin".split()],"Métadonnées, accès, formulaires, utilisateurs et fichiers","platform")
add("odoo","odoo",["addons/base_import","addons/web/controllers","addons/web/models","addons/web/static/src/core","addons/web/static/src/model","addons/web/static/src/search","addons/web/static/src/views/form","addons/web/static/src/views/list","addons/web/static/src/views/fields","addons/web/static/src/webclient","addons/web/static/src/*.js"],"Import, contrôles, listes, formulaires et navigation natifs","platform")
# Tryton
add("tryton","tryton",["modules/"+n for n in "party party_relationship country currency company product product_attribute product_measurements product_classification product_image product_kit product_price_list product_price_list_dates carrier carrier_weight carrier_subdivision".split()],"Produits, variantes, parties, unités, classifications, tarifs et transporteurs","reference")
add("tryton","tryton",["modules/stock/location.py","modules/stock/location.xml","modules/stock/view/location*.xml"],"Sites et hiérarchie de stockage","reference")
add("tryton","tryton",["trytond/trytond/"+n for n in "model backend protocols tools wizard modules sql".split()]+["trytond/trytond/"+n+".py" for n in "__init__ application cache config const convert exceptions filestore i18n pool pyson routing rpc security transaction url wsgi".split()],"Persistance, API, expressions, chargement et services du serveur","platform")
add("tryton","tryton",["trytond/trytond/ir/"+n+".py" for n in "action attachment avatar cache configuration date error export lang message model module note resource rule sequence session translation".split()]+["trytond/trytond/ir/ui","trytond/trytond/res"],"Métadonnées, droits, historique et utilisateurs","platform")
add("tryton","tryton",["sao/src/"+n+".js" for n in "action common html_sanitizer model notification pyson rpc sao screen session tab view window wizard".split()]+["sao/src/view/form.js","sao/src/view/tree.js","sao/src/view/list_form.js"],"Client navigateur Sao, listes et formulaires ; client bureau exclu","platform")
# Axelor suite native models + controller/service/repository classes selected by semantic names.
base_entities="Product ProductCategory ProductCompany ProductFamily ProductMultipleQty ProductPackaging ProductVariant ProductVariantAttr ProductVariantConfig ProductVariantValue Unit UnitConversion Partner PartnerAddress PartnerCategory PartnerLink PartnerLinkType PartnerPriceList PartnerRole Address AddressTemplate AddressTemplateLine Country Currency CurrencyConversionLine PriceList PriceListLine Site Company City Region Department IndustrySector EmailAddress Tag TradingName GeographicalArea EconomicArea AlternativeBarcode AlternativeBarcodeType"
for sub in ["domains","views"]:
    add("axelor","axelor",[f"axelor-base/src/main/resources/{sub}/{n}.xml" for n in base_entities.split()],"Modèles et vues natifs des référentiels","reference")
add("axelor","axelor",["axelor-base/src/main/java/com/axelor/apps/base/**/"+n+"*.java" for n in "Product Unit Partner Address Country Currency PriceList Site Company City Region TradingName Barcode".split()],"Services, contrôleurs et dépôts associés aux référentiels","reference")
stock_entities="StockLocation ShipmentMode FreightCarrierMode FreightCarrierCustomerAccountNumber"
for sub in ["domains","views"]:
    add("axelor","axelor",[f"axelor-stock/src/main/resources/{sub}/{n}.xml" for n in stock_entities.split()],"Sites et transporteurs","reference")
add("axelor","axelor",["axelor-stock/src/main/java/com/axelor/apps/stock/**/"+n+"*.java" for n in stock_entities.split()],"Comportements natifs des sites et transporteurs","reference")
add("axelor","axelor",["axelor-base/src/main/java/com/axelor/apps/base/"+n+".java" for n in "AxelorException AxelorAlertException AxelorMessageException ResponseMessageType".split()]+["axelor-base/src/main/java/com/axelor/apps/base/service/ExceptionService.java","axelor-base/src/main/java/com/axelor/apps/base/service/app/AppBaseService*.java","axelor-base/src/main/java/com/axelor/apps/base/service/app/AppService*.java","axelor-base/src/main/java/com/axelor/apps/base/utils"],"Utilitaires communs du module métier","reference")
add("axelor","platform",["axelor-core/src/main/java/com/axelor/"+n for n in "app auth cache concurrent data db event events file inject meta rpc script text ui".split()]+["axelor-common/src/main/java","axelor-web/src/main/java","axelor-core/src/main/resources/domains"],"Persistance, métadonnées, import, accès et API natifs","platform")
add("axelor","platform",["axelor-front/src/"+n for n in "components hooks layout routes services store utils view-containers".split()]+["axelor-front/src/views/"+n for n in "form grid search tree types.ts".split()]+["axelor-front/src/App.tsx","axelor-front/src/main.tsx"],"Interface React native, formulaires, grilles, recherche et navigation","platform")
add("axelor","axelor",["axelor-supplychain/src/main/resources/domains/FreightCarrier*.xml","axelor-supplychain/src/main/resources/views/FreightCarrier*.xml","axelor-supplychain/src/main/java/com/axelor/apps/supplychain/**/FreightCarrier*.java"],"Tarification native des services de transport","reference")
# Child DocType metadata linked by Table/Table MultiSelect must not be silently omitted.
doctype_index={}
for repo in ["erpnext","frappe"]:
    root=ROOT/REPOS[repo][0]
    for p in root.glob("**/doctype/*/*.json"):
        if p.stem==p.parent.name:
            doctype_index.setdefault((repo,p.stem),[]).append(p)
changed=True
while changed:
    changed=False
    for key,rec in list(files.items()):
        if rec["repo"] not in {"erpnext","frappe"} or not rec["path"].endswith(".json"):continue
        root=ROOT/REPOS[rec["repo"]][0]
        d=json.loads((root/rec["path"]).read_text(encoding="utf-8-sig"))
        for field in d.get("fields",[]):
            if field.get("fieldtype") not in {"Table","Table MultiSelect"}:continue
            child=(field.get("options") or "").lower().replace(" ","_")
            if not child:continue
            matches=doctype_index.get((rec["repo"],child),[])
            if not matches:
                other="frappe" if rec["repo"]=="erpnext" else "erpnext"
                oroot=ROOT/REPOS[other][0];matches=doctype_index.get((other,child),[])
                rr=other; rt=oroot
            else:rr=rec["repo"];rt=root
            for p in matches:
                if (rec["product"],rr,p.relative_to(rt).as_posix()) not in files:
                    add(rec["product"],rr,[p.parent.relative_to(rt).as_posix()],f"Sous-table de {d.get('name')}: {field.get('fieldname')}",rec["layer"]);changed=True
baseline=json.loads((ROOT/"audits/2026-10-30-master-data-4-oss/baseline.json").read_text(encoding="utf-8-sig"))
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in baseline["files"].items()),"Sources actives modifiées"
(OUT/"baseline.json").write_text(json.dumps(baseline,ensure_ascii=False,indent=2),encoding="utf-8")
repos={}
for key,(path,url,sha) in REPOS.items():
    actual=subprocess.check_output([GIT,"-C",str(ROOT/path),"rev-parse","HEAD"],text=True).strip()
    assert actual==sha,(key,actual,sha)
    repos[key]={"root":path,"repository":url,"commit":sha,"url":f"https://github.com/{url}/tree/{sha}"}
manifest={"id":"master-data-native-23","date":"2026-10-30","meaning":"Reconstruction théorique native de la sélection de sources, avec mécanismes de plateforme sélectionnés financés une fois par alternative. Ni coût historique, ni adoption OSS, ni estimation Spring.","repos":repos,"groups":groups,"unmatched_patterns":missing,"files":sorted(files.values(),key=lambda r:(r["product"],r["repo"],r["path"]))}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"files":len(files),"by_product":{p:sum(r["product"]==p for r in files.values()) for p in ["erpnext","odoo","tryton","axelor"]},"unmatched_patterns":missing},ensure_ascii=False))
