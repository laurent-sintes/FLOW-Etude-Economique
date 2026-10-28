// Resolve narrative variables from current model values; no presentation content.
export function investmentVariables(data){
 const n=(value,digits=0)=>new Intl.NumberFormat(data.presentation.locale,{minimumFractionDigits:digits,maximumFractionDigits:digits}).format(value);
 const a=data.sensibilite_finance_sap,p=data.comparaison_prix_integration;
 return {
  bonus_continuite_pct:data.scenario.integration_make.bonus_continuite_build_pct,
  budget_sap_meur_3:n(data.options[4].integration/1e6,3),budget_sap_keur_0:n(data.options[4].integration/1e3),
  budget_microsoft_keur_0:n(data.options[3].integration/1e3),
  ancre_make_meur_3:n(a.integration_sap_apres_retrait_eur_ht/1e6,3),finance_jh:n(a.jh_finance_fpa),
  complements_sap_meur_3:n((a.complements_generiques_sap_eur_ht+a.qualification_automation_sap_eur_ht)/1e6,3),
  finance_lot2_jh:n(a.lots[0].jh_finance_fpa),lot2_jh:n(a.lots[0].jh_externes),lot2_prix_meur_3:n(a.lots[0].prix_lot_eur_ht/1e6,3),
  finance_lot3_jh:n(a.lots[1].jh_finance_fpa),lot3_jh:n(a.lots[1].jh_externes),lot3_prix_meur_3:n(a.lots[1].prix_lot_eur_ht/1e6,3),
  base_sap_jh:n(p.jh_base_sap_proxy),delaware_retraite_meur_3:n(a.base_delaware_apres_retrait_eur_ht/1e6,3),
  delaware_moyen_eur_jh_0:n(a.base_delaware_apres_retrait_eur_ht/p.jh_base_sap_proxy),
  ...Object.fromEntries(data.options.slice(0,3).map(o=>[`integration_${o.stack==='java-spring'?'java':o.stack}_meur_3`,n(o.integration_source/1e6,3)]))
 };
}
