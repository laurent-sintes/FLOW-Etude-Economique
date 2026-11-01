import type {Bootstrap,Data,Projection} from './context';

/** Presentation scope only. Preserve all parameter values for historical scenarios. */
export function visibleOptions<T extends Record<string,any>>(ui:Data,rows:T[],key='stack'):T[]{
 const ids=ui.essential?.active_options;
 return Array.isArray(ids)?rows.filter(row=>ids.includes(row[key])):rows;
}
export function visibleProjection(ui:Data,projection:Projection):Projection{
 return {...projection,options:visibleOptions(ui,projection.options)};
}
export function scopeBootstrap(data:Bootstrap):Bootstrap{
 if(!data.ui?.essential?.active_options)return data;
 const {ui}=data,content={...data.content};
 if(content.framework){
  const F=content.framework;
  content.framework={...F,tariffs:visibleOptions(ui,F.tariffs,'key'),sources:{...F.sources,annual_gains:visibleOptions(ui,F.sources.annual_gains,'key')}};
 }
 if(content.core_evaluation)content.core_evaluation=visibleOptions(ui,content.core_evaluation);
 if(content.core_product_scope)content.core_product_scope={...content.core_product_scope,options:visibleOptions(ui,content.core_product_scope.options)};
 const glossary={...data.glossary,options:Object.fromEntries(Object.entries(data.glossary.options).filter(([id])=>!ui.essential?.active_options||ui.essential.active_options.includes(id)))};
 return {...data,content,glossary,baseline:visibleProjection(ui,data.baseline)};
}

/** Filter the documentary register without altering historical options or any budget. */
export function visibleBudgetReview(ui:Data,budget:Data):Data{
 const additions=visibleOptions(ui,budget.additions),ids=new Set(additions.map(row=>row.id));
 const optionLabels=Object.fromEntries(Object.entries(budget.option_labels).filter(([stack])=>!ui.essential?.active_options||ui.essential.active_options.includes(stack)));
 return {...budget,option_labels:optionLabels,additions,reviews:budget.reviews.map((review:Data)=>({...review,addition_refs:review.addition_refs.filter((id:string)=>ids.has(id)),non_budget_treatments:visibleOptions(ui,review.non_budget_treatments)})),summary:{...budget.summary,unique_reserves:additions.length,unpriced_reserves:additions.filter(row=>row.net_extra_initial_eur_ht===null&&row.net_extra_annual_eur_ht===null).length}};
}
