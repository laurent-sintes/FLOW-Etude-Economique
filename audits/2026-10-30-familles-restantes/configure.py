from pathlib import Path
import json,yaml
ROOT=Path.cwd();OUT=ROOT/'audits/2026-10-30-familles-restantes'
plan=json.loads((OUT/'plan.json').read_text(encoding='utf-8'))
# Historical costs are deliberately not loaded. Only pinned source references and observations are reused.
historical={}
for folder in ['audits/2026-10-29-experimentation-estimation','audits/2026-10-30-couverture-core']:
 for p in (ROOT/folder).glob('iteration-*-preuves.json'):
  try:d=json.loads(p.read_text(encoding='utf-8-sig'))
  except Exception:continue
  for e in d.get('evidence',[]):
   if not isinstance(e,dict) or not e.get('repository') or not e.get('path'):continue
   historical[p.name+':'+e['id']]=dict(e,prior_evidence=p.relative_to(ROOT).as_posix())
def entries(iteration,ids):
 return [historical[iteration+'-preuves.json:'+id] for id in ids]
configs=[
('eligibility',None,[],['buying/doctype/supplier/supplier.py'],r'block|hold|warn|check|suspend',.7,.75),
('policies','iteration-16',['O161','T161','A161'],['stock/doctype/putaway_rule/putaway_rule.py','stock/reorder_item.py'],r'rule|warehouse|orderpoint|reorder|policy',.65,.5),
('disposition','iteration-18',['O182','T182','A182'],['stock/doctype/quality_inspection/quality_inspection.py'],r'valid|check|process|control|decision|cancel|repair|inspection',.6,.75),
('orders','iteration-13',['O1','O2','O3','T1','T2','T3','T4','A1','A2','A3'],['selling/doctype/sales_order/sales_order.py','buying/doctype/purchase_order/purchase_order.py'],r'confirm|valid|process|update.*qty|return|cancel|amend|merge|split|draft|submit',.65,.5),
('master-plan','iteration-14',['O2','T2','A3'],['manufacturing/doctype/production_plan/production_plan.py','stock/doctype/material_request/material_request.py'],r'plan|requirement|procure|supply|schedule|compute|request|mrp',.65,.6),
('plan-preparation','iteration-16',['O161','T161','A161'],['manufacturing/doctype/sales_forecast/sales_forecast.py','manufacturing/doctype/production_plan/production_plan.py'],r'forecast|requirement|plan|supply|quantity|qty|compute|reconcile',.6,.65),
('backlog','iteration-14',['O1','O3','T1','A1'],['stock/doctype/stock_reservation_entry/stock_reservation_entry.py','stock/doctype/pick_list/pick_list.py'],r'assign|reserv|priority|available|qty|release|quantity',.6,.6),
('optimization','iteration-16',['O161','T161','A161'],['stock/reorder_item.py','manufacturing/doctype/production_plan/production_plan.py'],r'reorder|supply|plan|stock.*rule|generate|compute',.65,.75),
('promising','iteration-14',['O1','O2','T1','T2','A1','A2','A3','A4'],['stock/get_item_details.py','manufacturing/doctype/work_order/work_order.py'],r'available|forecast|quantity|qty|capacity|margin|supply|compute.*date',.55,.6),
('service-planning','iteration-16',['O162','T162','A162'],['manufacturing/doctype/workstation/workstation.py','stock/doctype/delivery_trip/delivery_trip.py'],r'available|capacity|interval|duration|time|calendar|slot|plan|schedule',.6,.65),
('coordination','iteration-17',['O172','T174','A172'],['stock/doctype/delivery_trip/delivery_trip.py','stock/doctype/delivery_note/delivery_note.py'],r'confirm|cancel|assign|create.*move|validate|done|process|status',.5,.65),
('assurance','iteration-18',['O181','T182','T184','A182'],['stock/doctype/delivery_note/delivery_note.py','stock/doctype/quality_inspection/quality_inspection.py'],r'track|result|inspection|valid|check|status|done|process',.55,.6),
('goods-orders','iteration-18',['O181','O182','O183','T181','T182','A181','A182'],['stock/doctype/pick_list/pick_list.py','stock/doctype/packing_slip/packing_slip.py','stock/doctype/quality_inspection/quality_inspection.py'],r'valid|check|process|done|create|repair|cancel|pack|quality|inspection',.4,.55),
('transport-orders','iteration-17',['O172','T171','T172','A171','A172'],['stock/doctype/shipment/shipment.py','stock/doctype/delivery_trip/delivery_trip.py'],r'shipment|carrier|booking|valid|rate|status|package|cancel|create|confirm|delivery',.5,.65),
('customs','iteration-18',['O181','T181','T183','A181'],['stock/doctype/shipment/shipment.py'],r'valid|document|attachment|shipment|custom|export|process|status',.25,.8),
('financial-services','iteration-19',['O191','O192','T191','T192','A191','A192'],['accounts/doctype/payment_request/payment_request.py','accounts/doctype/sales_invoice/sales_invoice.py'],r'payment|refund|transaction|request|invoice|process|cancel|post|state|status',.3,.45),
('workflow',None,[],[],r'workflow|transition|trigger|process|event|queue|confirm|validate',.65,.8),
('human-work',None,[],[],r'assign|activity|task|deadline|escalat|schedule|user|work',.6,.55),
('supervision','iteration-20',['T202'],[],r'history|log|event|revert|cancel|exception|message|intervention|state',.5,.75),
('intelligence','iteration-20',['O201','T201','A201'],[],r'query|select|group|report|count|duration|aggregate|analysis',.7,.8),
]
repos=json.loads((ROOT/'audits/2026-10-30-master-data-comparable-reuse/measurements.json').read_text(encoding='utf-8'))['repos']
repository_to_id={v['repository']:k for k,v in repos.items()}
for f,conf in zip(plan['families'],configs):
 slug,iteration,ids,erp,pattern,share,extra=conf
 es=[]
 for id in ids:
  key=(iteration+'-preuves.json:'+id) if iteration else ''
  if key in historical:es.append(historical[key])
 refs=[]
 for e in es:
  repo=repository_to_id.get(e['repository'])
  if repo:refs.append(dict(repo=repo,path=e['path'],prior_evidence=e['prior_evidence'],observed=e.get('observation',e.get('observed')),limit=e.get('limit',e.get('flow_delta')),excerpts=e.get('excerpts',[])))
 for p in erp:refs.append(dict(repo='erpnext',path='erpnext/'+p,prior_evidence=None))
 f.update(slug=slug,source_candidates=refs,method_pattern=pattern,attribution=share,complement_fraction=extra)
# Explicit supplementary sources for families whose prior exploration was incomplete.
extra={
'eligibility':[('odoo','addons/purchase/models/purchase_order.py'),('odoo','addons/purchase/models/res_partner.py'),('tryton','modules/sale_credit_limit/sale.py'),('tryton','modules/account_credit_limit/party.py'),('axelor','axelor-supplychain/src/main/java/com/axelor/apps/supplychain/service/saleorder/SaleOrderCheckBlockingSupplychainServiceImpl.java')],
'assurance':[('tryton','modules/stock/shipment.py')],
'workflow':[('frappe','frappe/model/workflow.py'),('frappe','frappe/workflow/doctype/workflow_action/workflow_action.py'),('odoo','addons/base_automation/models/base_automation.py'),('odoo','odoo/addons/base/models/ir_cron.py'),('tryton','trytond/trytond/model/workflow.py'),('tryton','trytond/trytond/ir/queue_.py'),('tryton','trytond/trytond/ir/trigger.py'),('axelor','axelor-purchase/src/main/java/com/axelor/apps/purchase/service/PurchaseRequestWorkflowServiceImpl.java')],
'human-work':[('frappe','frappe/desk/doctype/todo/todo.py'),('frappe','frappe/automation/doctype/assignment_rule/assignment_rule.py'),('odoo','addons/mail/models/mail_activity.py'),('tryton','modules/res_user_role/user.py'),('tryton','trytond/trytond/ir/trigger.py'),('axelor','axelor-project/src/main/java/com/axelor/apps/project/service/ProjectTaskServiceImpl.java')],
'supervision':[('frappe','frappe/core/doctype/activity_log/activity_log.py'),('frappe','frappe/model/workflow.py'),('odoo','addons/mail/models/mail_message.py'),('odoo','addons/base_automation/models/base_automation.py'),('axelor','axelor-project/src/main/java/com/axelor/apps/project/service/ProjectTaskServiceImpl.java'),('axelor','axelor-stock/src/main/java/com/axelor/apps/stock/service/StockLocationLineHistoryServiceImpl.java')],
'intelligence':[('erpnext','erpnext/selling/report/sales_analytics/sales_analytics.py'),('frappe','frappe/desk/reportview.py')]
}
for f in plan['families']:
 for repo,path in extra.get(f['slug'],[]):f['source_candidates'].append(dict(repo=repo,path=path,prior_evidence=None))
 f['product_coverage']={p:sum((x['repo']==p or p=='erpnext' and x['repo']=='frappe') for x in f['source_candidates']) for p in ['erpnext','odoo','tryton','axelor']}
plan['repos']=repos
(OUT/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([dict(family=f['slug'],sources=f['product_coverage'],missing=[x['path'] for x in f['source_candidates'] if not (ROOT/repos[x['repo']]['root']/x['path']).is_file()]) for f in plan['families']],ensure_ascii=False,indent=2))
