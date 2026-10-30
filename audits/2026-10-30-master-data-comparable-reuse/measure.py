from pathlib import Path
import json,sys,ast,re,hashlib,importlib.util,fnmatch,xml.etree.ElementTree as ET,collections,csv,io
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent;PREV=ROOT/"audits/2026-10-30-master-data-natif"
def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
m=load(PREV/"manifest.json")
for path in ["addons/product/security/product_security.xml","addons/product/security/ir.access.csv","addons/uom/security/uom_security.xml","addons/uom/security/ir.access.csv"]:
    f=ROOT/m["repos"]["odoo"]["root"]/path
    m["files"].append({"product":"odoo","repo":"odoo","path":path,"layer":"reference","sha256":hashlib.sha256(f.read_bytes()).hexdigest(),"reasons":["Droits spécifiques des objets Master Data"]})
for repo,folder in [("frappe","frappe/geo/doctype/country"),("frappe","frappe/geo/doctype/currency"),("erpnext","erpnext/setup/doctype/company")]:
    root=ROOT/m["repos"][repo]["root"]
    for f in (root/folder).glob("*"):
        if f.is_file() and f.suffix in {".py",".js",".json"} and not f.name.startswith("test_"):
            path=f.relative_to(root).as_posix()
            m["files"].append({"product":"erpnext","repo":repo,"path":path,"layer":"reference","sha256":hashlib.sha256(f.read_bytes()).hexdigest(),"reasons":["Référentiels de support natifs réutilisés"]})
spec=importlib.util.spec_from_file_location("oldmeasure",PREV/"measure.py");old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
# All rules below are source-scope decisions. No target effort or prior JH enters selection.
dt_erp=set("item item_attribute item_attribute_value item_barcode item_customer_detail item_supplier item_manufacturer item_variant item_variant_attribute item_variant_settings item_price price_list price_list_country uom_category uom_conversion_detail warehouse warehouse_type brand item_group uom uom_conversion_factor customer_group supplier_group customer supplier customer_number_at_supplier supplier_number_at_customer industry_type".split())
ax_names=set("Product ProductCategory ProductFamily ProductMultipleQty ProductVariant ProductVariantAttr ProductVariantConfig ProductVariantValue Unit UnitConversion Partner PartnerAddress PartnerCategory PartnerLink PartnerLinkType PartnerRole PartnerPriceList Address AddressTemplate AddressTemplateLine PriceList PriceListLine EmailAddress Tag StockLocation".split())
odoo_models=set("product_attribute product_attribute_value product_attribute_custom_value product_base_unit product_category product_pricelist product_pricelist_item product_product product_supplierinfo product_tag product_template product_template_attribute_line product_template_attribute_value product_uom uom_uom res_partner".split())
try_modules=set("party party_relationship product product_attribute product_measurements product_classification product_price_list product_price_list_dates".split())
generic_patterns={
"erpnext":["frappe/model/*","frappe/database/*","frappe/query_builder/*","frappe/api/*","frappe/permissions.py","frappe/auth.py","frappe/client.py","frappe/handler.py","frappe/share.py","frappe/desk/form/*","frappe/desk/listview.py","frappe/desk/reportview.py","frappe/desk/search.py","frappe/desk/treeview.py","frappe/core/doctype/data_import/*","frappe/core/doctype/data_export/*","frappe/core/doctype/doctype/*","frappe/core/doctype/docfield/*","frappe/core/doctype/docperm/*","frappe/core/doctype/role/*","frappe/core/doctype/user/*","frappe/core/doctype/user_permission/*","frappe/public/js/frappe/form/*","frappe/public/js/frappe/list/*","frappe/public/js/frappe/model/*","frappe/public/js/frappe/ui/*","frappe/utils/nestedset.py"],
"odoo":["odoo/orm/*","odoo/models/*","odoo/fields/*","odoo/api/*","odoo/http/*","odoo/sql_db.py","odoo/addons/base/models/ir_access.py","odoo/addons/base/models/ir_model.py","odoo/addons/base/models/ir_ui_view.py","odoo/addons/base/models/ir_exports.py","odoo/addons/base/models/res_users.py","odoo/addons/base/models/res_groups*.py","addons/base_import/*","addons/web/controllers/dataset.py","addons/web/models/*","addons/web/static/src/model/*","addons/web/static/src/views/form/*","addons/web/static/src/views/list/*","addons/web/static/src/views/fields/*","addons/web/static/src/search/*"],
"tryton":["trytond/trytond/model/*","trytond/trytond/backend/*","trytond/trytond/protocols/*","trytond/trytond/ir/model.py","trytond/trytond/ir/export.py","trytond/trytond/ir/rule.py","trytond/trytond/ir/ui/*","trytond/trytond/res/*","trytond/trytond/rpc.py","trytond/trytond/transaction.py","trytond/trytond/pyson.py","sao/src/model.js","sao/src/rpc.js","sao/src/screen.js","sao/src/view.js","sao/src/view/form.js","sao/src/view/tree.js","sao/src/view/list_form.js","sao/src/window.js","sao/src/session.js","sao/src/common.js"],
"axelor":["axelor-core/src/main/java/com/axelor/db/*","axelor-core/src/main/java/com/axelor/rpc/*","axelor-core/src/main/java/com/axelor/data/*","axelor-core/src/main/java/com/axelor/auth/*","axelor-core/src/main/java/com/axelor/meta/*","axelor-core/src/main/java/com/axelor/ui/*","axelor-core/src/main/resources/domains/*","axelor-web/src/main/java/com/axelor/web/service/RestService.java","axelor-front/src/views/form/*","axelor-front/src/views/grid/*","axelor-front/src/views/search/*","axelor-front/src/views/tree/*","axelor-front/src/services/*"]}
# Reference code natively shared with all domains is reused, not rebuilt for Master Data.
support_patterns={
"erpnext":["frappe/contacts/doctype/gender/*","frappe/contacts/doctype/salutation/*","frappe/geo/doctype/country/*","frappe/geo/doctype/currency/*","erpnext/setup/doctype/company/*"],
"odoo":["odoo/addons/base/models/res_country.py","odoo/addons/base/models/res_currency.py","odoo/addons/base/models/res_company.py"],
"tryton":["modules/country/*","modules/currency/*","modules/company/company.py"],
"axelor":["axelor-base/src/main/resources/domains/Country.xml","axelor-base/src/main/resources/domains/Currency*.xml","axelor-base/src/main/resources/domains/Company.xml","axelor-base/src/main/java/com/axelor/apps/base/service/Currency*.java","axelor-base/src/main/java/com/axelor/apps/base/service/Company*.java"]}
def matches(path,patterns):return any(fnmatch.fnmatchcase(path,p) for p in patterns)
def selection(row):
    p=row["path"];product=row["product"]
    if matches(p,generic_patterns[product]+support_patterns[product]):return "reused"
    if row["layer"]!="reference":return None
    if product=="erpnext":
        if row["repo"]=="frappe":return "new" if p.startswith("frappe/contacts/doctype/") or p=="frappe/contacts/address_and_contact.py" else None
        if "/doctype/" in p and p.split("/doctype/")[1].split("/")[0] in dt_erp:return "new"
        if p=="erpnext/controllers/item_variant.py":return "new"
    if product=="odoo":
        if p=="odoo/addons/base/models/res_partner.py" or p=="odoo/addons/base/views/res_partner_views.xml":return "new"
        if p.startswith("addons/product/models/") and Path(p).stem in odoo_models:return "new"
        if p.startswith("addons/product/views/") and not any(t in p for t in ["combo","document","report","label","supplierinfo"]):return "new"
        if p.startswith("addons/uom/") or p.startswith("addons/product/security/") or p=="addons/product/static/src/js/product_attribute_value_list.js":return "new"
        if p in ["addons/stock/models/stock_location.py","addons/stock/views/stock_location_views.xml"]:return "new"
    if product=="tryton":
        if p.startswith("modules/") and p.split("/")[1] in try_modules and not any(t in p.split("/") for t in ["scripts","doc"]):return "new"
        if p in ["modules/stock/location.py","modules/stock/location.xml"] or p.startswith("modules/stock/view/location_"):return "new"
    if product=="axelor":
        if "/resources/" in p and Path(p).stem in ax_names:return "new"
        name=Path(p).stem
        if "/java/" in p:
            allowed=("ProductService","ProductVariant","ProductCategory","ProductConversion","ProductMultipleQty","ProductPrice","ProductUpdate","ProductController","ProductBaseRepository","PartnerService","PartnerAddress","PartnerLink","PartnerPriceList","PartnerBaseRepository","PartnerController","AddressService","AddressController","AddressBaseRepository","UnitConversion","PriceList","StockLocationService")
            if name.startswith(allowed) and "api/" not in p:return "new"
    return None
# Named exclusions only; every excluded block/field and original line is written to the audit.
exclude_methods={
"erpnext":set("validate_opening_stock set_opening_stock validate_fixed_asset validate_retain_sample clear_retain_sample validate_item_tax_net_rate_range check_for_active_boms check_item_tax validate_warehouse_for_reorder stock_ledger_created has_submitted_assets delete_old_bins validate_duplicate_item_in_stock_reconciliation validate_properties_before_merge validate_duplicate_product_bundles_before_merge set_last_purchase_rate recalculate_bin_qty update_bom_item_desc validate_item_defaults update_defaults_from_item_group validate_stock_exists_for_template_item validate_serial_no_wise_valuation set_valuation_method_for_serial_no_wise_valuation validate_serialized_change_with_bundle _get_linked_submitted_documents validate_auto_reorder_enabled_in_stock_settings validate_serial_and_batch_no_enabled_in_stock_settings get_last_purchase_details get_purchase_voucher_details rebuild_bin_reservations check_stock_uom_with_bin get_item_defaults set_item_default validate_item_default_company_links validate_default_inventory_account get_asset_naming_series make_opening_stock_entry create_opening_stock_reconciliation set_opening_stock_serial_batch_bundle get_default_warehouse_for_opening_stock make_quotation make_opportunity make_payment_entry _set_missing_values get_loyalty_programs check_credit_limit send_emails check_overdue_billing_threshold get_overdue_billing_threshold get_customer_overdue_amount get_outstanding_invoices_for_customer get_past_due_payable_amounts get_overdue_portion get_customer_outstanding get_credit_limit load_dashboard_info validate_default_bank_account validate_internal_customer update_lead_status link_lead_records copy_communication validate_credit_limit_on_change set_loyalty_program add_role_for_user validate_default_in_transit_warehouse validate_disable_with_stock validate_warehouse_account validate_inventory_account get_bin_with_quantity warn_about_multiple_warehouse_account check_if_sle_exists get_warehouses_based_on_account get_warehouses_for_reorder".split()),
"odoo":set("_compute_application_statistics _compute_application_statistics_hook _compute_same_vat_partner_id _compute_standard_price _set_standard_price _search_standard_price _compute_cost_currency_id _compute_sql_cost_currency_id _compute_show_qty_update_button _compute_quantities _compute_quantities_dict _search_qty_available _set_qty_available _search_incoming_qty _search_outgoing_qty _search_virtual_available _compute_forecasted_without_stock _update_standard_price _search_product_quantity _get_invoice_policy _onchange_standard_price action_open_label_layout action_open_documents _compute_product_document_count _get_product_document_domain _demo_configure_variants _check_combo_ids_not_empty _check_sale_combo_ids _compute_is_empty _search_is_empty _compute_next_inventory_date _compute_replenish_location _check_replenish_location _get_putaway_strategy _get_next_inventory_date should_bypass_reservation _check_access_putaway _is_outgoing _get_weight _compute_weight".split()),
"tryton":set("_cost_price_method_domain_per_type get_cost_price default_cost_price_method default_cost_price get_cost_price_methods check_vies check_vies_button get_distance order_distance _distance_query check_type_for_moves get_empty_locations lost_found_used _get_quantity_grouping get_quantity search_quantity get_quantity_uom get_cost_value".split()),
"axelor":set("getDefaultBankDetails getPartnerExemptionList getPartnerExemptionSubList findPartnerMails findMailsFromPartner getSocialNetworkUrl printContactPhonebook printCompanyPhonebook printClientSituation getParamsMap findSentMails findReceivedMails findMails checkIbanValidity setPositiveBalance apiSireneFetchData setSocialNetworkUrl updateCostPrice printProductCatalog getStockIndicators getBadStockLocationLineId getContentStockLocationIds changeProductLocker".split())}
exclude_classes={"odoo":{"StockRoute"},"tryton":{"ProductCostPrice","ProductCostPriceMethod","ProductsByLocationsContext","ProductsByLocations","LocationLeadTime","WarehouseWasteLocation"},"erpnext":set(),"axelor":set()}
exclude_fields=set("saleSupplySelect procurementMethodSelect inventoryTypeSelect lastPurchaseDate lastPurchasePrice autoUpdateSalePrice managPriceCoef shippingCoef bankDetailsList paymentDelay invoiceComments opening_stock valuation_rate is_fixed_asset asset_category asset_naming_series include_item_in_manufacturing default_material_request_type valuation_method reorder_levels has_batch_no create_new_batch batch_number_series has_expiry_date retain_sample sample_quantity has_serial_no serial_no_series use_serial_no_wise_valuation item_defaults safety_stock last_purchase_rate enable_deferred_revenue no_of_months enable_deferred_expense no_of_months_exp taxes inspection_required_before_purchase inspection_required_before_delivery quality_inspection_template default_bom is_sub_contracted_item total_projected_qty over_delivery_receipt_allowance over_billing_allowance auto_create_assets grant_commission is_grouped_asset allow_negative_stock purchase_tax_withholding_category sales_tax_withholding_category stock_levels_html default_bank_account lead_name accounts credit_limits loyalty_program loyalty_program_tier default_commission_rate sales_team customer_pos_id so_required dn_required opportunity_name prospect_name tax_withholding_group account default_in_transit_warehouse qty_available virtual_available incoming_qty outgoing_qty standard_price cost_price cost_price_method stock_move_ids move_ids quant_ids putaway_rule_ids route_ids replenishment_ids last_inventory_date next_inventory_date valuation_in_account_id valuation_out_account_id invoice_ids invoice_count sale_order_count purchase_order_count accountMoveList stockLocationLineList stockMoveList stockMoveLineList accountManagementList accountingSituationList paymentCondition taxLine purchaseAccount saleAccount costPrice".split())
def measure(row,kind):
    path=ROOT/m["repos"][row["repo"]]["root"]/row["path"];ext=path.suffix;text=path.read_text(encoding="utf-8-sig")
    if kind=="reused":return old.measure(path),[]
    removed=[];program=decl=0
    def record(typ,name,line=None):removed.append({"kind":typ,"name":name,"line":line,"reason":"Hors contrat commun : transaction, stock physique, finance ou fonction spécialisée"})
    if ext==".py":
        lines=text.splitlines();inside=False
        for j,line in enumerate(lines):
            if "# begin: auto-generated types" in line:inside=True
            if inside:lines[j]=""
            if "# end: auto-generated types" in line:inside=False
        normalized=re.sub(r"(?m)^(\s*)except ([\w.]+(?:,\s*[\w.]+)+):",r"\1except (\2):","\n".join(lines))
        tree=ast.parse(normalized)
        def visit(n):
            nonlocal program
            if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in exclude_methods[row["product"]]:record("method",n.name,n.lineno);return
            if isinstance(n,ast.ClassDef) and n.name in exclude_classes[row["product"]]:record("class",n.name,n.lineno);return
            if isinstance(n,(ast.Assign,ast.AnnAssign)):
                targets=n.targets if isinstance(n,ast.Assign) else [n.target]
                names=[t.id for t in targets if isinstance(t,ast.Name)]
                if names and any(x in exclude_fields for x in names):record("field",",".join(names),n.lineno);return
            if isinstance(n,ast.stmt) and not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str)):program+=1
            for child in ast.iter_child_nodes(n):visit(child)
        visit(tree)
    elif ext in old.PARSERS:
        raw=text.encode();tree=old.PARSERS[ext].parse(raw)
        assert not tree.root_node.has_error,row["path"]
        def visit(n):
            nonlocal program,decl
            name_node=n.child_by_field_name("name")
            name=raw[name_node.start_byte:name_node.end_byte].decode() if name_node else ""
            if n.type=="method_declaration" and name in exclude_methods[row["product"]]:record("method",name,n.start_point.row+1);return
            key=n.child_by_field_name("key") if n.type=="pair" else None
            if key:
                keytext=raw[key.start_byte:key.end_byte].decode().strip("'\"")
                if keytext in exclude_fields:record("field_handler",keytext,n.start_point.row+1);return
            if ext==".java":
                if (n.type.endswith("_statement") and n.type!="empty_statement") or n.type in old.JAVA_EXTRA:program+=1
            else:
                if (n.type.endswith("_statement") and n.type not in {"empty_statement","export_statement"}) or n.type in old.JS_EXTRA:program+=1
                if n.type in {"jsx_opening_element","jsx_self_closing_element"}:decl+=1
            for child in n.named_children:visit(child)
        visit(tree.root_node)
    elif ext==".csv":
        records=list(csv.DictReader(io.StringIO(text)))
        for r in records:
            model=r.get("model_id:id","").replace("model_","")
            if any(token in model for token in ["combo","document","label"]):record("access_rule",r.get("id",model))
            else:decl+=1
    elif ext==".json":
        d=json.loads(text)
        fields=[]
        for f in d.get("fields",[]):
            if f.get("fieldname") in exclude_fields:record("field",f["fieldname"])
            else:fields.append(f)
        decl=1+len(fields)+sum(len(d.get(k,[])) for k in ["permissions","actions","links","states"])
    elif ext==".xml":
        tree=ET.fromstring(text)
        counts=[0]
        def visit(n):
            nonlocal decl
            tag=n.tag.split("}")[-1];name=n.attrib.get("name","");model=n.attrib.get("model","")
            if tag=="record" and model and (not model.startswith(("ir.","res.groups","res.group")) or model=="ir.message"):return
            if name in exclude_fields:record("field_or_widget",name);return
            if tag=="extra-code" and n.text and n.text.strip():
                raw=("class CountingWrapper {\n"+n.text+"\n}").encode()
                t=old.PARSERS[".java"].parse(raw)
                assert not t.root_node.has_error,("Embedded Java",row["path"])
                # Wrapper is artificial; generated Java is not counted a second time.
                for node in old.walk(t.root_node):
                    if node.type=="class_declaration" and node.child_by_field_name("name") and raw[node.child_by_field_name("name").start_byte:node.child_by_field_name("name").end_byte]==b"CountingWrapper":continue
                    if (node.type.endswith("_statement") and node.type!="empty_statement") or node.type in old.JAVA_EXTRA:
                        counts[0]+=1
                return
            if tag not in old.XML_WRAPPERS:decl+=1
            for child in n:visit(child)
        visit(tree)
        program+=counts[0]
    else:
        q=old.measure(path);program=q["program_units"];decl=q["declarative_units"]
    return {"program_units":program,"declarative_units":decl},removed
OUT.mkdir(parents=True,exist_ok=True)
rules={"generic_patterns":generic_patterns,"support_patterns":support_patterns,"excluded_methods":{k:sorted(v) for k,v in exclude_methods.items()},"excluded_classes":{k:sorted(v) for k,v in exclude_classes.items()},"excluded_fields":sorted(exclude_fields),"status":"Décisions d'ingénierie assistées par IA, non revues par un expert externe."}
(OUT/"scope-rules.json").write_text(json.dumps(rules,ensure_ascii=False,indent=2),encoding="utf-8")
rows=[];omitted=[];errors=[]
for r in m["files"]:
    kind=selection(r)
    if kind is None:omitted.append({"product":r["product"],"repo":r["repo"],"path":r["path"]});continue
    path=ROOT/m["repos"][r["repo"]]["root"]/r["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest()==r["sha256"]
    try:
        units,removed=measure(r,kind);rows.append({**r,"treatment":kind,**units,"excluded_blocks":removed})
    except Exception as e:errors.append({"path":r["path"],"error":str(e)})
summary={}
for product in ["erpnext","odoo","tryton","axelor"]:
    summary[product]={}
    for kind in ["new","reused"]:
        subset=[r for r in rows if r["product"]==product and r["treatment"]==kind]
        summary[product][kind]={"files":len(subset),"program_units":sum(r["program_units"] for r in subset),"declarative_units":sum(r["declarative_units"] for r in subset),"excluded_blocks":sum(len(r["excluded_blocks"]) for r in subset)}
result={"id":"master-data-comparable-reuse-24","repos":m["repos"],"files":rows,"omitted_files":omitted,"errors":errors,"summary":summary,"counting_convention_ref":"../2026-10-30-master-data-natif/measure.py","source_selection":"Sources inchangées ; projection de taille par blocs sélectionnés, pas extraction exécutable."}
(OUT/"measurements.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
# Capture a fresh baseline of currently tracked source/config/app content rather than assuming an old baseline.
baseline={}
for folder in ["source","config","app/src","app/scripts"]:
    for p in (ROOT/folder).rglob("*"):
        if p.is_file():baseline[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
if not (OUT/"baseline.json").exists():(OUT/"baseline.json").write_text(json.dumps({"files":baseline},indent=2),encoding="utf-8")
print(json.dumps({"summary":summary,"errors":errors,"excluded_entire_files":len(omitted)},ensure_ascii=False))
