import fs from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';
import {createContentRenderer} from './presentation_content.mjs';
import {investmentVariables} from './investment_content.mjs';

const data=JSON.parse(await fs.readFile('tmp/investissement-10-ans/inputs.json','utf8'));
execFileSync(process.execPath,['tools/check_generator_content.mjs'],{stdio:'pipe'});
const presentation=data.presentation, glossary=data.glossaire, explanations=data.explications;
if(!presentation||!glossary||!explanations)throw new Error('ERR_CONTENT_INPUT');
const t=createContentRenderer(presentation,glossary);
const checkingModel=process.argv.includes('--check-model');
const emittedText=[];
const explanationVariables=investmentVariables(data);
const expandExplanation=text=>t.render(text,explanationVariables);
if(process.argv.includes('--check-content')){
 const walk=x=>typeof x==='string'?expandExplanation(x):Array.isArray(x)?x.map(walk):x&&typeof x==='object'?Object.fromEntries(Object.entries(x).map(([k,v])=>[k,walk(v)])):x;
 const resolved=walk(explanations);
 if(resolved.references.length!==30||resolved.perimetre_compare.length!==10||resolved.methodes_calcul.length!==12||resolved.definitions_perimetre.length!==10)throw new Error('ERR_CONTENT_STRUCTURE');
 console.log(process.argv.includes('--json')?JSON.stringify(resolved):JSON.stringify({status:'valid',blocks:75}));
 process.exit(0);
}
const expected=JSON.parse(await fs.readFile('tmp/investissement-10-ans/expected.json','utf8'));
const price=data.comparaison_prix_integration;
const wb=Workbook.create();
const [syn,hyp,plan,scope,calc,src]=[t("contenus.synthese"),t("contenus.hypotheses"),t("contenus.investissements"),t("contenus.perimetre"),t("contenus.calculs"),t("contenus.sources")].map(n=>wb.worksheets.add(n));
// Single visual contract for authoring and native Excel finalization. No economic inputs.
const ui=presentation.charte;
const {ink,blue,pale,muted,input}=ui,green=t("palette.24705a");
const visual={version:1,ui,sheets:[],headers:[],sections:[],panels:[],fit:[]};
const phaseFill=presentation.couleurs_phases;
const fmt=t("formats.0_00_0_00"), fmt1=t("formats.0_0_0_0"),fmtK=t("formats.0_0_0_0_2");
const names=data.options.map(o=>o.nom), columns=['C','D','E','F','G'];
const rowBase=i=>6+16*i;
const val=(s,a,v)=>{s.getRange(a).values=[[v]];if(typeof v==='string')emittedText.push({sheet:s.name,address:a,value:v});};
const formula=(s,a,f)=>{s.getRange(a).formulas=[[f]]; if([hyp,calc].includes(s))s.getRange(a).format.font.color=f.includes('!')?green:ink;};
function hypUnits(text){return text.replace(/(\d+(?:,\d+)?)\s*M€/g,(_,n)=>t("contenus.variable_k", {p0: new Intl.NumberFormat(presentation.locale,{maximumFractionDigits:3}).format(Number(n.replace(',','.'))*1000)}));}
function merged(s,range,text,height=29){s.getRange(range).merge();val(s,range.split(':')[0],s===hyp?hypUnits(text):text);s.getRange(range).format.wrapText=true;s.getRange(range).format.rowHeight=height;s.getRange(range).format.horizontalAlignment='left';}
function header(s,r,labels,start=1){const q=s.getRangeByIndexes(r-1,start,1,labels.length);q.values=[labels];labels.forEach((value,i)=>{if(typeof value==='string')emittedText.push({sheet:s.name,address:`${String.fromCharCode(65+start+i)}${r}`,value});});q.format={fill:ink,font:{name:ui.font,size:ui.headerFont,bold:true,color:t("palette.ffffff")},wrapText:true,horizontalAlignment:'center'};visual.headers.push({sheet:s.name,address:`${String.fromCharCode(65+start)}${r}:${String.fromCharCode(64+start+labels.length)}${r}`});}
function section(s,r,text,end='G'){const address=t("contenus.bvariable_variablevariable", {p0: r, p1: end, p2: r});merged(s,address,text,ui.hypSection);visual.sections.push({sheet:s.name,address});}
function fitText(s,addresses,minHeight=ui.line){visual.fit.push({sheet:s.name,addresses,minHeight});}
function reading(s,r,labelRange,bodyRange,label,body){
 merged(s,labelRange,label,34);merged(s,bodyRange,body,34);
 visual.panels.push({sheet:s.name,label:labelRange,body:bodyRange});fitText(s,[labelRange,bodyRange],30);
}
function editable(s,address,format,min,max,type='decimal'){
 const q=s.getRange(address);q.setNumberFormat(format);q.format.fill=input;q.format.font.color=ui.inputText;
 q.dataValidation={rule:{type,operator:'between',formula1:min,formula2:max}};
}
for(const [s,last,rows,title] of [[syn,'H',36,t("contenus.flow_core_system_simulation_sur_10_ans")],[hyp,'G',88,t("contenus.hypotheses_modifiables")],[plan,'L',47,t("contenus.depenses_annuelles_sur_10_ans")],[scope,'E',31,t("contenus.flow_et_synvance_perimetre_compare")],[calc,'L',90,t("contenus.calcul_de_la_repartition_annuelle")],[src,'G',88,t("contenus.sources_et_valeurs_de_reference")]]){
 visual.sheets.push({name:s.name,last,end:rows});
 s.showGridLines=false;s.getRange(t("contenus.a1_variablevariable", {p0: last, p1: rows})).format={font:{name:ui.font,size:ui.body,color:ink},verticalAlignment:'center'};
 merged(s,t("contenus.b2_variable2", {p0: last}),title,30);s.getRange(t("contenus.b2_variable2", {p0: last})).format.font={size:16,bold:true,color:ink};
 s.getRange(t("contenus.b3_variable3", {p0: last})).format.borders={bottom:{style:'thin',color:blue}};
 s.getRange(t("contenus.c6_variablevariable", {p0: last, p1: rows})).format.horizontalAlignment='right';
 s.tabColor=s===syn?ink:s===hyp?blue:t("palette.b8cad8");
}

// Input values are generated from the YAML. No formulas read an external workbook.
header(src,6,[t("libelles.reference_m_ht_sauf_duree"),...names]);
merged(src,'B4:G4',t("contenus.ces_valeurs_de_reference_alimentent_la_simulation_pour_make_la_lig"),50);
const sourceLabels={7:t("libelles.build_flow_core_system"),8:t("libelles.variable_contrepoint_make_budget_buy"),9:t("libelles.variable_an"),10:t("libelles.variable_an_2"),11:t("libelles.variable_an_3"),12:t("libelles.variable_an_4"),13:t("libelles.annuites_documentees"),14:t("libelles.variable_annee_1"),15:t("libelles.variable_annee_2"),16:t("libelles.variable_annee_3"),17:t("libelles.variable_annee_4"),18:t("libelles.variable_annee_5"),20:t("libelles.variable_mois_de_reference"),21:t("libelles.variable_buy_mois"),22:t("libelles.indexation_ipaas")};
for(const [r,label]of Object.entries(sourceLabels))val(src,'B'+r,label);
data.options.forEach((o,i)=>{
 const c=columns[i];const b=o.base_annuelle;
 for(const[r,v]of [[7,o.build],[8,o.integration_source],[9,b.services_mco],[10,b.hebergement],[11,b.ipaas],[12,b.licences_complementaires]])val(src,c+r,v/1e6);
 val(src,c+'13',o.prix_abonnements.length);
 for(let k=0;k<5;k++)val(src,c+(14+k),o.prix_abonnements[k]===undefined?null:o.prix_abonnements[k]/1e6);
 val(src,c+'20',o.build_mois);val(src,c+'21',o.mode==='Buy'?o.integration_mois:null);
 val(src,c+'22',o.ipaas_indexation_logiciel?t("libelles.logiciel"):t("libelles.cloud"));
 val(src,c+'19',o.ventilation_services.core===null?null:o.ventilation_services.core/1e6);
});
val(src,'B19',t("libelles.dont_services_variable_make_an"));src.getRange('C19:G19').setNumberFormat(fmt);
for(const r of [7,8,21])src.getRange('B'+r).format.wrapText=true;
src.getRange('B19').format.wrapText=true;
src.getRange('C7:G18').setNumberFormat(fmt);src.getRange('C13:G13').setNumberFormat(t("formats.0"));src.getRange('C20:G21').setNumberFormat(t("formats.0"));
src.getRange('C22:G22').format.horizontalAlignment='left';
src.getRange('B9:B18').format.wrapText=true;
val(src,'B23',t("libelles.inflation_ingenierie_services"));val(src,'C23',data.taux.tjm_ingenierie);
val(src,'B24',t("libelles.inflation_licences"));val(src,'C24',data.taux.licences_logiciels);
val(src,'B25',t("libelles.inflation_cloud"));val(src,'C25',data.taux.cloud);src.getRange('C23:C25').setNumberFormat(t("formats.0_0"));
section(src,27,t("libelles.origine_et_portee_des_valeurs"));
const refs=explanations.references.map(r=>[expandExplanation(r.libelle),expandExplanation(r.texte)]);
refs.forEach(([label,text],j)=>{const r=28+j*2;val(src,'B'+r,label);src.getRange('B'+r).format.font.bold=true;src.getRange('B'+r).format.wrapText=true;merged(src,`C${r}:G${r}`,text,43);});

section(hyp,6,t("libelles.1_variable"));header(hyp,7,[t("libelles.parametre"),...names]);
section(hyp,11,t("libelles.2_variable"));header(hyp,12,[t("libelles.parametre"),...names]);
section(hyp,16,t("libelles.3_variable_pleine_capacite"));header(hyp,17,[t("libelles.composante_k_ht_an"),...names]);
const hlabels={8:t("libelles.duree_du_variable_mois"),9:t("libelles.budget_du_variable_k_ht"),13:t("libelles.duree_de_l_variable_mois"),14:t("libelles.budget_de_l_variable_k_ht"),15:t("libelles.variable"),18:t("libelles.maintenance_et_evolution_du_core_system"),19:t("libelles.maintenance_et_evolution_de_l_integration_beaumanoir"),20:t("libelles.paas_plateforme_d_execution"),21:t("libelles.ipaas_plateforme_d_integration"),22:t("libelles.autres_licences_achetees_separement"),23:t("libelles.abonnement_editeur_logiciel_maintien_et_cloud_inclus"),24:t("libelles.total_mco_annuel_run")};
for(const[r,label]of Object.entries(hlabels))val(hyp,'B'+r,label);
data.options.forEach((o,i)=>{
 const c=columns[i];const b=o.base_annuelle;
 val(hyp,c+'8',o.build_mois);
 if(i<3){editable(hyp,c+'8',t("formats.0"),36,60,'whole');formula(hyp,c+'13',t("formules.average_f_13_g_13"));formula(hyp,c+'14',t("formules.g_58_1_c_15"));formula(hyp,c+'15',t("formules.c_15"));}
 else {val(hyp,c+'13',o.integration_mois);editable(hyp,c+'13',t("formats.0"),6,60,'whole');val(hyp,c+'14',o.integration/1e3);editable(hyp,c+'14',fmtK,0,100000);}
 val(hyp,c+'9',o.build/1e3);if(i<3)editable(hyp,c+'9',fmtK,0,100000);
 if(i<3){
  for(const[r,v]of [[18,o.ventilation_services.core],[19,o.ventilation_services.integration]]){val(hyp,c+r,v/1e3);editable(hyp,c+r,fmtK,0,20000);}
 }else{
  hyp.getRange(`${c}18:${c}19`).merge();val(hyp,c+'18',o.ventilation_services.groupes/1e3);editable(hyp,c+'18',fmtK,0,20000);
  hyp.getRange(`${c}18:${c}19`).format.fill=input;
 }
 for(const[r,v]of [[20,b.hebergement],[21,b.ipaas],[22,b.licences_complementaires]]){val(hyp,c+r,v/1e3);editable(hyp,c+r,fmtK,0,20000);}
 formula(hyp,c+'23',t("formules.if_variable_variable13_0_0_variable_variable14_1000", {p0: c, p1: c}));
 const fields=[8,9,13,14,18,20,21,22];if(i<3)fields.push(19);
 formula(hyp,c+'25',t("formules.if_and_count_variable_variable_min_variable_0_variable13_6_variabl", {p0: fields.map(r=>t("formules.variablevariable", {p0: c, p1: r})).join(t("formules.valeur")), p1: fields.length, p2: fields.map(r=>t("formules.variablevariable", {p0: c, p1: r})).join(t("formules.valeur")), p3: c, p4: c, p5: c, p6: c, p7: i<3?t("formules.and_variable8_36_variable8_60_count_c_15_1_c_15_0_c_15_0_5", {p0: c, p1: c}):t("formules.variable8_0", {p0: c})}));
 formula(hyp,c+'24',t("formules.if_variable25_sum_variable18_variable23_na", {p0: c, p1: c, p2: c}));
});
formula(hyp,'B25',t("formules.if_countifs_c25_g25_a_corriger_0_saisie_a_corriger"));
merged(hyp,'B26:G26',t("contenus.microsoft_et_sap_prestations_client_non_ventilees_entre_core_et_in"),37);
hyp.getRange('C8:G8').setNumberFormat(t("formats.0"));hyp.getRange('C13:G13').setNumberFormat(t("formats.0_0_2"));
hyp.getRange('C9:G9').setNumberFormat(fmtK);hyp.getRange('C14:G14').setNumberFormat(fmtK);hyp.getRange('C18:G23').setNumberFormat(fmtK);
val(hyp,'C15',data.scenario.integration_make.bonus_continuite_build_pct/100);editable(hyp,'C15',t("formats.0_2"),0,0.5);hyp.getRange('D15:E15').setNumberFormat(t("formats.0_2"));
for(const c of ['F','G'])val(hyp,c+'15',t("libelles.sans_objet"));
hyp.getRange('F8:G9').setNumberFormat(t("formats.variable"));hyp.getRange('C23:E23').setNumberFormat(t("formats.variable"));
for(const r of [8,9,13,14,15,18,19,20,21,22,23])hyp.getRange('B'+r).format.wrapText=true;
for(const c of ['F','G'])hyp.getRange(c+'18').setNumberFormat(fmtK);
hyp.getRange('B24:G24').format={fill:pale,font:{bold:true},wrapText:true};hyp.getRange('C24:G24').setNumberFormat(fmtK);
hyp.getRange('C25:G25').conditionalFormats.add('containsText',{text:t("contenus.corriger"),format:{fill:t("palette.fbe3e3"),font:{color:t("palette.a42222"),bold:true}}});
merged(hyp,'B4:G4',t("contenus.tous_les_budgets_sont_en_k_ht_le_mco_est_en_k_ht_an_cellules_jaune"),48);
section(hyp,27,t("libelles.parametres_transverses_inflation_annuelle"));
for(const[r,label,v]of [[28,t("contenus.inflation_ingenierie_services"),data.taux.tjm_ingenierie],[29,t("contenus.inflation_licences"),data.taux.licences_logiciels],[30,t("contenus.inflation_cloud"),data.taux.cloud]]){val(hyp,'B'+r,label);val(hyp,'C'+r,v);editable(hyp,'C'+r,t("formats.0_0"),0,0.15);}
const hnotes=explanations.conventions_lecture.map(expandExplanation);hnotes.forEach((t,i)=>merged(hyp,`B${31+i}:G${31+i}`,t,44));

// Read-only challenge: the active Make convention follows the SAP anchor in row 58.
section(hyp,37,t("libelles.controle_des_budgets_d_integration_reperes_non_substituables"));
header(hyp,38,[t("libelles.repere_en_k_ht"),...names]);
val(hyp,'B39',t("libelles.budget_retenu_dans_la_simulation"));
val(hyp,'B40',t("libelles.chiffrage_par_activites"));
val(hyp,'B41',t("libelles.ecart_a_expliquer_par_livrable"));
for(const c of ['F','G'])formula(hyp,c+'39',t("formules.variable14", {p0: c}));
for(const c of ['C','D','E']){
 formula(hyp,c+'39',t("formules.variable14", {p0: c}));
 formula(hyp,c+'40',t("formules.variable_variable8_1000", {p0: c}));
 formula(hyp,c+'41',t("formules.variable39_variable40", {p0: c, p1: c}));
}
hyp.getRange('C39:G41').setNumberFormat(fmtK);
merged(hyp,'B43:G43',expandExplanation(explanations.notes_methodologiques.comparaison_interfaces),60);
merged(hyp,'B45:G45',expandExplanation(explanations.notes_methodologiques.references_publiques_sap),70);
merged(hyp,'B47:G47',expandExplanation(explanations.notes_methodologiques.portee_plage_publique),52);
merged(hyp,'B49:G49',expandExplanation(explanations.notes_methodologiques.ancre_make_finance),130);
merged(hyp,'B51:G51',expandExplanation(explanations.notes_methodologiques.references_dynamiques),52);
section(hyp,53,t("libelles.variable_retrait_finance_fp_a_budget_buy_sap_inchange"));
header(hyp,54,[t("libelles.lot_delaware"),t("libelles.jh_du_lot"),t("libelles.jh_finance"),t("libelles.prix_du_lot_k"),t("libelles.prix_moyen_jh"),t("libelles.retrait_k")]);
data.sensibilite_finance_sap.lots.forEach((lot,i)=>{
 const r=55+i;val(hyp,'B'+r,t("libelles.lot_variable_variable", {p0: lot.numero, p1: lot.libelle}));
 val(hyp,'C'+r,lot.jh_externes);val(hyp,'D'+r,lot.jh_finance_fpa);
 val(hyp,'E'+r,lot.prix_lot_eur_ht/1e3);
 formula(hyp,'F'+r,t("formules.evariable_1000_cvariable", {p0: r, p1: r}));
 formula(hyp,'G'+r,t("formules.dvariable_evariable_cvariable", {p0: r, p1: r, p2: r}));
});
val(hyp,'B57',t("libelles.finance_fp_a_hors_perimetre_flow_retrait_indicatif"));formula(hyp,'D57',t("formules.sum_d55_d56"));formula(hyp,'G57',t("formules.sum_g55_g56"));
val(hyp,'B58',t("libelles.ancre_make_avant_bonus"));formula(hyp,'G58',t("formules.g14_g57"));
val(hyp,'B59',t("libelles.dont_complements_etude_pilotage_et_preparation"));val(hyp,'G59',data.sensibilite_finance_sap.complements_sap_pilotage_preparation_retenus_dans_ancre_make_eur_ht/1e3);
val(hyp,'B60',t("libelles.dont_lots_delaware_retraites_mix_non_ventile"));formula(hyp,'G60',t("formules.g58_g59"));
val(hyp,'B62',t("libelles.gain_de_continuite_make"));formula(hyp,'G62',t("formules.g58_c_15"));
val(hyp,'B63',t("libelles.budget_make_apres_bonus"));formula(hyp,'G63',t("formules.g58_g62"));
hyp.getRange('C55:D57').setNumberFormat(t("formats.0"));hyp.getRange('E55:E56').setNumberFormat(fmtK);
hyp.getRange('F55:F56').setNumberFormat(t("formats.0_00"));hyp.getRange('G55:G63').setNumberFormat(fmtK);
hyp.getRange('B55:B63').format.wrapText=true;
merged(hyp,'B61:G61',expandExplanation(explanations.notes_methodologiques.methode_retrait_finance),92);

section(hyp,64,t("libelles.comparaison_de_prix_esn_miroir_des_jh_sap_sensibilite_budget_actif"));
val(hyp,'B65',t("libelles.base_hors_finance_e_jh_f_k_g_jh"));formula(hyp,'F65',t("formules.g60"));val(hyp,'G65',price.jh_base_sap_proxy);formula(hyp,'E65',t("formules.f65_1000_g65"));
header(hyp,66,[t("libelles.profil"),t("libelles.part_des_jh"),t("libelles.jh_proxy"),t("libelles.tjm_jh_ht"),t("libelles.cout_k"),t("libelles.origine")]);
const profileRows=[
 ['integration_metier',67,t("libelles.integration_metier_configuration"),t("libelles.onappli")],
 ['integration_it_donnees_qualification',68,t("libelles.integration_it_donnees_qualification"),t("libelles.onappli")],
 ['developpement_java_react',69,t("libelles.developpement_java_react"),t("libelles.onappli")],
 ['pilotage',70,t("libelles.pilotage_inclus_dans_les_jh"),t("libelles.onappli")]
];
for(const [key,r,label,origin] of profileRows){
 const p=price.profils_base[key];val(hyp,'B'+r,label);val(hyp,'C'+r,p.part_pct/100);editable(hyp,'C'+r,t("formats.0_2"),0,1);
 formula(hyp,'D'+r,t("formules.g_65_cvariable", {p0: r}));val(hyp,'E'+r,p.tjm_eur_ht);editable(hyp,'E'+r,t("formats.0"),0,2000);
 formula(hyp,'F'+r,t("formules.dvariable_evariable_1000", {p0: r, p1: r}));val(hyp,'G'+r,origin);
}
val(hyp,'B71',t("libelles.sous_total_profils"));formula(hyp,'C71',t("formules.sum_c67_c70"));formula(hyp,'D71',t("formules.sum_d67_d70"));formula(hyp,'F71',t("formules.sum_f67_f70"));
formula(hyp,'G71',t("formules.if_abs_c71_1_0_000001_parts_a_corriger"));
val(hyp,'B72',t("libelles.outillage_additionnel_non_retenu"));val(hyp,'F72',0);
section(hyp,73,t("libelles.complements_d_integration_specifiques_jh_de_l_etude_revalorises_pa"));
const compByRole={integration_metier:0,integration_it_donnees_qualification:0,developpement_java_react:0};
for(const row of Object.values(price.complements_jh_par_nature))compByRole[row.profil]+=row.jh;
for(const [r,label,role,tariffRow] of [[74,t("contenus.configuration_metier"),'integration_metier',67],[75,t("contenus.integration_it_qualification"),'integration_it_donnees_qualification',68],[76,t("contenus.extensions_java_react"),'developpement_java_react',69]]){
 val(hyp,'B'+r,label);val(hyp,'C'+r,compByRole[role]);formula(hyp,'E'+r,t("formules.evariable", {p0: tariffRow}));formula(hyp,'F'+r,t("formules.cvariable_evariable_1000", {p0: r, p1: r}));
}
val(hyp,'B77',t("libelles.sous_total_complements"));formula(hyp,'C77',t("formules.sum_c74_c76"));formula(hyp,'F77',t("formules.sum_f74_f76"));
val(hyp,'B78',t("libelles.outillage_additionnel_non_retenu"));val(hyp,'F78',0);
val(hyp,'B79',t("libelles.pilotage_etude_sur_ces_seuls_complements"));val(hyp,'C79',price.pilotage_complements_pct/100);formula(hyp,'F79',t("formules.f77_c79"));
val(hyp,'B80',t("libelles.preparation"));val(hyp,'F80',price.preparation_eur_ht/1e3);
val(hyp,'B81',t("libelles.prix_esn_par_profils_indicatif"));formula(hyp,'F81',t("formules.if_g71_sum_f71_f72_f77_f80_na"));
val(hyp,'B82',t("libelles.ecart_avec_l_ancre_sap_avant_bonus"));formula(hyp,'F82',t("formules.f81_g58"));formula(hyp,'G82',t("formules.g58"));
val(hyp,'B83',t("libelles.sap_buy_avec_complements_esn_indicatif"));formula(hyp,'F83',t("formules.g14_g59_sum_f77_f80"));formula(hyp,'G83',t("formules.g14"));
val(hyp,'B84',t("libelles.esn_programme_stress_bas"));val(hyp,'E84',data.scenario.comparaison_prix_integration_miroir_sap.contrepoint_integrateur_eur_jh.bas);formula(hyp,'F84',t("formules.g65_c77_e84_1000_f80"));
val(hyp,'B85',t("libelles.esn_programme_stress_haut"));val(hyp,'E85',data.scenario.comparaison_prix_integration_miroir_sap.contrepoint_integrateur_eur_jh.haut);formula(hyp,'F85',t("formules.g65_c77_e85_1000_f80"));
merged(hyp,'B86:G86',expandExplanation(explanations.notes_methodologiques.gouvernance_sap),62);
merged(hyp,'B87:G87',expandExplanation(explanations.notes_methodologiques.limites_tarifs_esn),85);
hyp.getRange('C67:C71').setNumberFormat(t("formats.0_2"));hyp.getRange('C79').setNumberFormat(t("formats.0_2"));
hyp.getRange('D67:D71').setNumberFormat(t("formats.0_0_2"));hyp.getRange('C74:C77').setNumberFormat(t("formats.0_00"));
hyp.getRange('E65:E70').setNumberFormat(t("formats.0"));hyp.getRange('F65:F85').setNumberFormat(fmtK);
hyp.getRange('G65').setNumberFormat(t("formats.0"));hyp.getRange('G82:G83').setNumberFormat(fmtK);

// Annual schedules use M€; annual Hypothèses inputs use k€ and convert once on entry.
for(let i=0;i<5;i++){
 const r=rowBase(i),h=columns[i];
 header(calc,r,[names[i],...Array.from({length:10},(_,k)=>k+1)]);calc.getRange(`C${r}:L${r}`).setNumberFormat(t("formats.an_0"));
 const labels=[t("libelles.part_du_variable"),t("libelles.part_de_l_variable"),t("libelles.fraction_d_annee_en_variable"),t("libelles.build_flow_core_system"),t("libelles.integration_et_migration_groupe_beaumanoir"),t("libelles.services_mco_et_evolutions"),t("libelles.variable_et_variable_separes"),t("libelles.abonnement_editeur_logiciel_maintien_et_cloud_inclus"),t("libelles.autres_licences_achetees_separement"),t("libelles.mco_annuel_run"),t("libelles.total_annuel"),t("libelles.cumul")];
 labels.forEach((l,j)=>val(calc,'B'+(r+j+1),l));
 for(const offset of [2,4,5])calc.getRange('B'+(r+offset)).format.wrapText=true;
 for(let y=1;y<=10;y++){
  const c=String.fromCharCode(66+y),yr=`${c}$${r}`,bh=t("contenus.hypotheses_variable_8", {p0: h}),dh=t("contenus.hypotheses_variable_13", {p0: h}),end=`(${bh}+${dh})`;
  formula(calc,c+(r+1),t("formules.if_variable_variable_25_na_if_variable_0_0_max_0_min_variable_12_v", {p0: h, p1: bh, p2: yr, p3: bh, p4: yr, p5: bh}));
  formula(calc,c+(r+2),t("formules.if_variable_variable_25_na_max_0_min_variable_12_variable_max_vari", {p0: h, p1: yr, p2: end, p3: yr, p4: bh, p5: dh}));
  formula(calc,c+(r+3),t("formules.if_variable_variable_25_na_max_0_variable_12_max_variable_1_12_var", {p0: h, p1: yr, p2: yr, p3: end}));
  formula(calc,c+(r+4),t("formules.variablevariable_variable_variable_9_1000", {p0: c, p1: r+1, p2: h}));
  formula(calc,c+(r+5),t("formules.variablevariable_variable_variable_14_1000", {p0: c, p1: r+2, p2: h}));
  formula(calc,c+(r+6),t("formules.variablevariable_sum_variable_variable_18_variable_19_1000_1_varia", {p0: c, p1: r+3, p2: h, p3: h, p4: yr}));
  formula(calc,c+(r+7),t("formules.variablevariable_1000_variable_variable_20_1_variable_c_30_variabl", {p0: c, p1: r+3, p2: h, p3: yr, p4: h, p5: h, p6: yr}));
  formula(calc,c+(r+8),t("formules.if_variable_variable_13_0_0_index_variable_variable_14_variable_18", {p0: h, p1: h, p2: h, p3: yr, p4: h, p5: yr, p6: h}));
  formula(calc,c+(r+9),t("formules.variablevariable_variable_variable_22_1000_1_variable_c_29_variabl", {p0: c, p1: r+3, p2: h, p3: yr}));
  formula(calc,c+(r+10),t("formules.sum_variablevariable_variablevariable", {p0: c, p1: r+6, p2: c, p3: r+9}));
  formula(calc,c+(r+11),t("formules.sum_variablevariable_variablevariable_variablevariable", {p0: c, p1: r+4, p2: c, p3: r+5, p4: c, p5: r+10}));
  formula(calc,c+(r+12),y===1?t("formules.variablevariable_2", {p0: c, p1: r+11}):t("formules.variablevariable_variablevariable", {p0: String.fromCharCode(65+y), p1: r+12, p2: c, p3: r+11}));
 }
 calc.getRange(`C${r+1}:L${r+3}`).setNumberFormat(t("formats.0_0"));calc.getRange(`C${r+4}:L${r+12}`).setNumberFormat(fmt);
 calc.getRange(`B${r+11}:L${r+11}`).format={fill:pale,font:{bold:true}};
}
merged(calc,'B4:L4',t("contenus.chaque_bloc_detaille_une_solution_en_m_ht_les_trois_premieres_lign"),52);

header(syn,6,[t("libelles.solution_comparee"),t("libelles.mode"),t("libelles.build_flow_core_system"),t("libelles.integration_et_migration_groupe_beaumanoir"),t("libelles.variable_10_ans"),t("libelles.total_10_ans"),t("libelles.variable_ans")]);
merged(syn,'B4:H4',t("contenus.cinq_solutions_alternatives_sur_dix_ans_en_m_ht_le_build_l_integra"),38);
for(let i=0;i<5;i++){
 const r=7+i,b=rowBase(i);val(syn,'B'+r,names[i]);val(syn,'C'+r,glossary.notions[data.options[i].mode.toLowerCase()].libelle);
 for(const[c,offset]of [['D',4],['E',5],['F',10],['G',11]])formula(syn,c+r,t("formules.sum_variable_cvariable_lvariable", {p0: b+offset, p1: b+offset}));
 formula(syn,'H'+r,t("formules.sum_variable_cvariable_lvariable", {p0: b+3, p1: b+3}));
}
syn.getRange('D7:G11').setNumberFormat(fmt1);syn.getRange('H7:H11').setNumberFormat(t("formats.0_0_2"));syn.getRange('G7:G11').format={fill:pale,font:{bold:true}};
syn.getRange('D10:D11').setNumberFormat(t("formats.variable"));
function summaryReading(r,label,body){
 reading(syn,r,`B${r}:C${r}`,`D${r}:H${r}`,label,body);
}
summaryReading(13,t("contenus.lecture_du_total"),t("contenus.chaque_solution_est_une_alternative_le_total_sur_dix_ans_additionn"));
summaryReading(15,t("contenus.build_des_options_buy"),t("contenus.sans_objet_le_progiciel_existe_deja_ses_adaptations_client_et_la_m"));
summaryReading(17,t("contenus.variable"),t("contenus.le_mco_complet_commence_apres_l_integration_les_abonnements_buy_de"));
summaryReading(19,t("contenus.limite_de_l_etude"),t("contenus.make_utilise_une_ancre_sap_apres_retrait_indicatif_de_finance_et_g"));
const totalChart=syn.charts.add('bar',[syn.getRange('B6:B11'),syn.getRange('G6:G11')]);
totalChart.title=t("contenus.depenses_sur_dix_ans_m_ht");totalChart.hasLegend=false;totalChart.setPosition('B22','I36');
totalChart.series.items[0].fill=blue;

header(plan,6,[t("libelles.annee"),...names]);
merged(plan,'B4:L4',t("contenus.chaque_colonne_presente_les_depenses_annuelles_d_une_solution_alte"),48);
for(let y=1;y<=10;y++){val(plan,'B'+(6+y),t("libelles.annee_2")+y);for(let i=0;i<5;i++)formula(plan,columns[i]+(6+y),t("formules.variable_variablevariable", {p0: String.fromCharCode(66+y), p1: rowBase(i)+11}));}
val(plan,'B17',t("libelles.total_sur_10_ans"));for(const c of columns)formula(plan,c+'17',t("formules.sum_variable7_variable16", {p0: c, p1: c}));
plan.getRange('C7:G17').setNumberFormat(fmt);plan.getRange('B17:G17').format={fill:pale,font:{bold:true}};
val(plan,'B21',t("libelles.detail_de_l_option"));plan.getRange('C21:F21').merge();val(plan,'C21',names[0]);plan.getRange('C21:F21').format.fill=input;
plan.getRange('C21').dataValidation={rule:{type:'list',values:names}};
header(plan,23,[t("libelles.m_ht"),...Array.from({length:10},(_,i)=>t("libelles.an")+(i+1))]);
for(const[r,label,off]of [[24,t("contenus.build_flow_core_system"),4],[25,t("contenus.integration_et_migration_groupe_beaumanoir"),5],[26,t("contenus.mco_annuel_run"),10],[27,t("contenus.total_annuel"),11]]){
 val(plan,'B'+r,label);for(let y=1;y<=10;y++){
 const c=String.fromCharCode(66+y);formula(plan,c+r,t("formules.choose_match_c_21_variable_c_6_g_6_0_variable", {p0: data.options.map((_,i)=>t("formules.variable_variablevariable_2", {p0: c, p1: rowBase(i)+off})).join(t("formules.valeur"))}));
 }}
plan.getRange('C24:L27').setNumberFormat(fmt);plan.getRange('B27:L27').format={fill:pale,font:{bold:true}};
for(const r of [24,25])plan.getRange('B'+r).format.wrapText=true;
const annualChart=plan.charts.add('line',plan.getRange('B6:G16'));annualChart.title=t("contenus.depenses_annuelles_m_ht");annualChart.setPosition('B30','M46');
ui.optionColors.forEach((c,i)=>{annualChart.series.items[i].line={fill:c,style:'solid',width:2};});

scope.getRange('B:B').format.columnWidth=26;scope.getRange('C:E').format.columnWidth=35;
merged(scope,'B4:E4',t("contenus.cette_vue_rapproche_les_fonctions_attendues_de_flow_des_capacites_"),48);
header(scope,6,[t("libelles.fonction"),t("libelles.flow_trois_make"),t("libelles.microsoft_k3"),t("libelles.sap_omsa")]);
const scopeRows=explanations.perimetre_compare.map(r=>[r.fonction,r.make,r.microsoft,r.sap].map(expandExplanation));
scopeRows.forEach((row,i)=>{scope.getRange(`B${7+i}:E${7+i}`).values=[row];scope.getRange(`B${7+i}:E${7+i}`).format={wrapText:true,horizontalAlignment:'left',fill:i%2===0?t("palette.f3f6f9"):t("palette.ffffff")};});
reading(scope,19,'B19:B19','C19:E19',t("libelles.limite_des_preuves"),t("contenus.un_manque_de_preuve_ne_demontre_pas_une_absence_de_fonction_les_co"));
reading(scope,21,'B21:B21','C21:E21',t("libelles.couverture_oms"),t("contenus.sap_omsa_couvre_une_partie_du_cycle_oms_microsoft_propose_des_capa"));
reading(scope,23,'B23:B23','C23:E23',t("libelles.tracabilite"),t("contenus.les_preuves_et_reserves_sont_detaillees_dans_sources_et_dans_la_no"));

// Shared compact charter. Keep all cell addresses and economic formulas unchanged.
function height(s,rows,h,last='L'){for(const r of rows)s.getRange(t("contenus.avariable_variablevariable", {p0: r, p1: last, p2: r})).format.rowHeight=h===0?0.75:h;}
function notes(s,rows,last,h=30){for(const r of rows)s.getRange(t("contenus.bvariable_variablevariable", {p0: r, p1: last, p2: r})).format={font:{size:ui.note,color:muted},rowHeight:h,verticalAlignment:'top',wrapText:true};}
for(const [s,last,end] of [[syn,'H',36],[hyp,'G',88],[plan,'L',47],[scope,'E',31],[calc,'L',90],[src,'G',86]]){
 s.getRange(t("contenus.a1_variablevariable", {p0: last, p1: end})).format.rowHeight=ui.line;
 s.getRange('A:A').format.columnWidth=1.5;
 s.getRange('B:B').format.columnWidth=ui.label;
 s.getRange(t("contenus.c_variable", {p0: last})).format.columnWidth=ui.money;
 s.getRange(t("contenus.b2_variable2", {p0: last})).format={font:{size:ui.sheetTitle},rowHeight:26};
 height(s,[1,3,5],ui.gap,last);
 notes(s,[4],last,ui.line);
 s.getRange(t("contenus.b6_variable6", {p0: last})).format.rowHeight=ui.header;
}
notes(syn,[4],'H',32);notes(hyp,[4],'G',34);notes(plan,[4],'L',32);notes(calc,[4],'L',38);notes(scope,[4],'E',32);notes(src,[4],'G',32);
// Summary: two narrow descriptive columns, equal monetary columns.
syn.getRange('B:B').format.columnWidth=22;syn.getRange('C:C').format.columnWidth=8;
syn.getRange('D:H').format.columnWidth=ui.money;height(syn,[6],56,'H');
for(const [c,fill] of [['D',phaseFill.build],['E',phaseFill.integration],['F',phaseFill.mco]])syn.getRange(`${c}7:${c}11`).format.fill=fill;
height(syn,[12,20],ui.gap,'H');height(syn,[14,16,18,21],0,'H');
totalChart.setPosition('B22','I36');
// Three editable spending tables; the Buy services remain grouped in one merged cell.
hyp.getRange('B7:B30').format.wrapText=true;
for(const r of [8,9,13,14,15,18,19,20,21,22,23,24])hyp.getRange(`C${r}:G${r}`).format.font.color=ink;
for(const a of ['C8:E9','C15','C18:E22','F13:G14','F18:G18','F20:G22','C28:C30'])hyp.getRange(a).format.font.color=ui.inputText;
height(hyp,[7,12,17],ui.hypHeader,'G');
height(hyp,[14,15],22,'G');height(hyp,[18],24,'G');height(hyp,[19,23],34,'G');height(hyp,[20,21,22,24],22,'G');
height(hyp,[10,36,42,44,46,48,50,52],ui.hypGap,'G');
notes(hyp,[26],'G',24);
height(hyp,[25],ui.line,'G');height(hyp,[28,29,30],23,'G');
notes(hyp,[31],'G',32);notes(hyp,[32,34,35],'G',30);notes(hyp,[33],'G',42);
height(hyp,[38,54],ui.hypHeader,'G');
hyp.getRange('B39:B41').format.wrapText=true;height(hyp,[39,40,41],ui.hypBody,'G');
notes(hyp,[43,45],'G',44);notes(hyp,[47,51],'G',32);notes(hyp,[49],'G',84);
height(hyp,[55],34,'G');height(hyp,[56],26,'G');height(hyp,[57],38,'G');height(hyp,[58],24,'G');height(hyp,[59,60],32,'G');notes(hyp,[61],'G',44);
height(hyp,[88],ui.gap,'G');height(hyp,[62,63],ui.hypBody,'G');height(hyp,[66],29,'G');
height(hyp,[65],34,'G');height(hyp,[67,68,69,70,71,72,74,75,76,77,78,80,81,82,84,85],24,'G');
height(hyp,[79,83],34,'G');
hyp.getRange('B65:B85').format.wrapText=true;notes(hyp,[86],'G',43);notes(hyp,[87],'G',61);
// Light boundaries preserve the three spending tables and Buy's grouped service cells.
const cellBorder={style:'thin',color:ui.border};
const inputBorder={preset:'outside',...cellBorder};
function grid(s,address){s.getRange(address).format.borders={preset:'all',...cellBorder};}
function outline(s,address){s.getRange(address).format.borders=inputBorder;}
grid(hyp,'B7:G9');grid(hyp,'B12:G15');grid(hyp,'B17:G24');grid(hyp,'B28:C30');
for(const c of ['F','G'])outline(hyp,`${c}18:${c}19`);
grid(hyp,'B38:G41');
grid(hyp,'B54:G60');
grid(hyp,'B62:G63');hyp.getRange('B63:G63').format={fill:pale,font:{bold:true}};
grid(hyp,'B65:G72');grid(hyp,'B74:G85');
// Annual schedule and calculations keep the original formulas and selector addresses.
for(const s of [plan,calc])s.getRange('C:L').format.columnWidth=ui.year;
height(plan,[6],ui.two);height(plan,[18],ui.gap);height(plan,[19,20,22,28],0);
height(plan,[21,23],ui.header);height(plan,[29],ui.gap);
height(plan,[24],24);height(plan,[25],36);
plan.getRange('C21:F21').format.font.color=ui.inputText;annualChart.setPosition('B30','M46');
for(let i=0;i<5;i++){
 const r=rowBase(i);height(calc,[r],ui.header);height(calc,[r+2,r+5],ui.two);
 calc.getRange(`B${r+1}:B${r+12}`).format.wrapText=true;
 calc.getRange(`C${r+1}:L${r+12}`).format.font.color=ink;
 height(calc,[r+13],ui.gap);height(calc,[r+14,r+15],0);
}
// Textual comparison and documentary references use only the height their text needs.
scope.getRange('B:B').format.columnWidth=28;scope.getRange('C:E').format.columnWidth=32;
height(scope,[6],ui.header,'E');height(scope,[7],ui.line,'E');height(scope,[8,9,10,11,12,13,15,16],ui.two,'E');
height(scope,[14],36,'E');
scope.getRange('B7:E16').format.verticalAlignment='top';
height(scope,[17],ui.gap,'E');height(scope,[18,20,22],0,'E');notes(scope,[19,21,23],'E',ui.line);
src.getRange('B7:B25').format.wrapText=true;height(src,[6],ui.header,'G');
height(src,[8,9],36,'G');
height(src,[19,21],ui.two,'G');height(src,[26],ui.gap,'G');height(src,[27],ui.header,'G');
// Minimum documentary heights; the native finalizer fits the current text and font.
refs.forEach((_,j)=>{const r=28+j*2;notes(src,[r],'G',ui.two);if(j<refs.length-1)height(src,[r+1],0,'G');});
// The same cell borders apply to every table. Narrative notes and spacers stay unruled.
grid(syn,'B6:H11');
grid(plan,'B6:G17');grid(plan,'B23:L27');outline(plan,'B21');outline(plan,'C21:F21');
for(const [r,fill] of [[24,phaseFill.build],[25,phaseFill.integration],[26,phaseFill.mco]])plan.getRange(`B${r}:L${r}`).format.fill=fill;
grid(scope,'B6:E16');
for(let i=0;i<5;i++){const r=rowBase(i);grid(calc,`B${r}:L${r+12}`);for(const [off,fill] of [[4,phaseFill.build],[5,phaseFill.integration],[10,phaseFill.mco]])calc.getRange(`B${r+off}:L${r+off}`).format.fill=fill;}
grid(src,'B6:G22');grid(src,'B23:C25');outline(src,'B27:G27');
for(const [r,fill] of [[7,phaseFill.build],[8,phaseFill.integration],[9,phaseFill.mco]])src.getRange(`B${r}:G${r}`).format.fill=fill;
refs.forEach((_,j)=>{const r=28+j*2;outline(src,'B'+r);outline(src,`C${r}:G${r}`);});
for(const ch of [totalChart,annualChart]){
 ch.titleTextStyle.fontSize=ui.chartTitle;
 ch.titleTextStyle.typeface=ui.font;
 ch.xAxis={axisType:'textAxis',textStyle:{typeface:ui.font,fontSize:ui.note}};
 ch.yAxis={numberFormatCode:t("contenus.0_0"),numberFormatSourceLinked:false,textStyle:{typeface:ui.font,fontSize:ui.note}};
}
annualChart.legend={position:'top',textStyle:{typeface:ui.font,fontSize:ui.note}};

// Final role-based pass: every sheet receives the same headers, sections, reading panels and totals.
for(const meta of visual.sheets){
 const s=wb.worksheets.getItem(meta.name),address=t("contenus.b4_variable4", {p0: meta.last});
 s.getRange(address).format={fill:ui.introFill,font:{name:ui.font,size:ui.note,color:ink},verticalAlignment:'center',wrapText:true,borders:{left:{style:'medium',color:ui.introRule}}};
 fitText(s,[address],26);
}
for(const meta of visual.headers){
 const s=wb.worksheets.getItem(meta.sheet);
 s.getRange(meta.address).format={fill:ink,font:{name:ui.font,size:ui.headerFont,bold:true,color:t("palette.ffffff")},verticalAlignment:'center',horizontalAlignment:'center',wrapText:true,borders:{insideVertical:{style:'thin',color:t("palette.ffffff")},bottom:{style:'thin',color:ui.sectionRule}}};
 const [,first,row,last]=meta.address.match(/([A-Z]+)(\d+):([A-Z]+)\d+/);
 fitText(s,Array.from({length:last.charCodeAt(0)-first.charCodeAt(0)+1},(_,i)=>`${String.fromCharCode(first.charCodeAt(0)+i)}${row}`),ui.header);
}
for(const meta of visual.sections){
 const s=wb.worksheets.getItem(meta.sheet);
 s.getRange(meta.address).format={fill:t("palette.ffffff"),font:{name:ui.font,bold:true,color:ink,size:ui.body},rowHeight:ui.hypSection,verticalAlignment:'bottom',wrapText:true,borders:{bottom:{style:'thin',color:ui.sectionRule}}};
 fitText(s,[meta.address],ui.hypSection);
}
for(const meta of visual.panels){
 const s=wb.worksheets.getItem(meta.sheet);
 s.getRange(meta.label).format={fill:pale,font:{name:ui.font,size:ui.note,bold:true,color:ink},verticalAlignment:'center',wrapText:true};
 s.getRange(meta.body).format={fill:t("palette.ffffff"),font:{name:ui.font,size:ui.note,bold:false,color:muted},verticalAlignment:'center',wrapText:true};
 for(const a of [meta.label,meta.body])s.getRange(a).format.borders={bottom:{style:'thin',color:ui.border}};
}
function total(s,address,major=true){s.getRange(address).format={fill:major?pale:ui.quietFill,font:{name:ui.font,bold:true,color:ink},borders:{top:{style:'thin',color:ui.sectionRule},bottom:{style:'thin',color:ui.border}}};}
for(const a of ['B24:G24','B58:G58','B63:G63','B81:G81','B83:G83'])total(hyp,a);
for(const a of ['B57:G57','B71:G71','B77:G77'])total(hyp,a,false);
total(plan,'B17:G17');total(plan,'B27:L27');
plan.getRange('B21').format={fill:pale,font:{size:ui.note,bold:true,color:ink}};
for(let i=0;i<5;i++){
 const r=rowBase(i);
 calc.getRange(`B${r+1}:L${r+3}`).format={fill:ui.quietFill,font:{size:ui.note,color:muted}};
 total(calc,`B${r+11}:L${r+11}`);total(calc,`B${r+12}:L${r+12}`,false);
 for(const off of Array.from({length:12},(_,i)=>i+1))fitText(calc,[`B${r+off}`],ui.two);
}
for(let r=7;r<=16;r++)fitText(scope,['B','C','D','E'].map(c=>c+r),r===7?ui.line:ui.two);
for(let r=7;r<=25;r++)fitText(src,[`B${r}`],ui.line);
refs.forEach((_,j)=>{
 const r=28+j*2;
 src.getRange(`B${r}`).format={fill:pale,font:{name:ui.font,size:ui.note,bold:true,color:ink},verticalAlignment:'top',wrapText:true};
 src.getRange(`C${r}:G${r}`).format={font:{name:ui.font,size:ui.note,bold:false,color:muted},verticalAlignment:'top',wrapText:true};
 fitText(src,[`B${r}`,`C${r}:G${r}`],ui.two);
});
for(const r of [26,31,32,33,34,35,43,45,47,49,51,61,86,87])fitText(hyp,[`B${r}:G${r}`],r===26?ui.line:ui.two);
// The native pass measures these wrapped texts, preserving widths and font sizes.
// This temporary manifest is a derivative of this generator, never an economic input.
if(!checkingModel)await fs.mkdir('tmp/investissement-10-ans',{recursive:true});

// First Hypothèses tooltip set: definitions on labels, evidence and limits on figures.
// Staging notes carry the registry into Excel. Native finalization replaces them
// with inactive hyperlink ScreenTips, whose popups stay within the monitor bounds.
const cellTooltips=new Map(),hypothesisTooltips=new Map();
function tooltip(s,address,body){
 const key=`${s.name}!${address}`;
 if(cellTooltips.has(key))throw new Error(t("messages.infobulle_dupliquee_variable", {p0: key}));
 if(body.length>ui.tooltip.maxCharacters)throw new Error(t("messages.infobulle_trop_longue_variable", {p0: key}));
 cellTooltips.set(key,{sheet:s.name,sheetId:s.sheetId,address,body});
}
function hypothesisTooltip(address,body){
 if(hypothesisTooltips.has(address))throw new Error(t("messages.tooltip_hypotheses_duplique_variable", {p0: address}));
 const text=hypUnits(body);hypothesisTooltips.set(address,text);tooltip(hyp,address,text);
}
for(const [address,body] of Object.entries({
 B8:t("contenus.cette_duree_correspond_a_la_construction_de_la_plateforme_generiqu"),
 B9:t("contenus.ce_budget_finance_la_realisation_initiale_du_core_system_generique"),
 B13:t("contenus.cette_duree_couvre_l_adaptation_de_la_solution_les_raccordements_l"),
 B14:t("contenus.ce_budget_couvre_les_travaux_initiaux_pour_faire_fonctionner_la_so"),
 B15:t("contenus.pour_les_options_make_le_scenario_suppose_que_la_continuite_d_une_"),
 B18:t("contenus.le_core_system_est_la_plateforme_generique_de_la_solution_pour_mak"),
 B19:t("contenus.cette_ligne_finance_l_entretien_et_les_evolutions_des_regles_exten"),
 B20:t("contenus.cette_ligne_couvre_les_capacites_d_execution_et_d_hebergement_ache"),
 B21:t("contenus.cette_ligne_couvre_la_plateforme_qui_transporte_transforme_ou_supe"),
 B22:t("contenus.cette_ligne_couvre_les_licences_supplementaires_identifiees_hors_o"),
 B23:t("contenus.cette_ligne_represente_le_prix_annuel_d_une_offre_editeur_vendue_c"),
 B24:t("contenus.ce_total_additionne_les_composantes_annuelles_a_pleine_capacite_au"),
 B28:t("contenus.hypothese_d_evolution_annuelle_des_prix_des_prestations_humaines_a"),
 B29:t("contenus.hypothese_d_evolution_des_licences_et_abonnements_logiciels_apres_"),
 B30:t("contenus.hypothese_d_evolution_des_achats_de_capacite_cloud_et_d_ipaas_a_l_")
}))hypothesisTooltip(address,body);
for(const c of ['C','D','E']){
 hypothesisTooltip(`${c}8`,t("contenus.le_scenario_retient_48_mois_pour_construire_une_premiere_version_c"));
 hypothesisTooltip(`${c}9`,t("contenus.estimation_des_jours_par_activite_valorises_aux_tarifs_de_cette_st"));
 hypothesisTooltip(`${c}13`,t("contenus.34_mois_est_la_moyenne_des_durees_microsoft_38_et_sap_30_cette_con"));
 hypothesisTooltip(`${c}14`,t("contenus.ancre_sap_apres_retrait_indicatif_de_finance_g58_reduite_du_gain_c"));
 hypothesisTooltip(`${c}18`,t("contenus.entretien_et_evolutions_du_core_generique_pilotage_compris_mai_003"));
 hypothesisTooltip(`${c}19`,t("contenus.entretien_des_adaptations_beaumanoir_flux_tests_support_expert_exp"));
 hypothesisTooltip(`${c}20`,t("contenus.72_k_an_provision_commune_make_pour_calcul_base_de_donnees_haute_d"));
 hypothesisTooltip(`${c}21`,t("contenus.36_k_an_provision_make_pour_runtime_de_flux_connecteurs_et_traces_"));
 hypothesisTooltip(`${c}22`,t("contenus.aucune_licence_supplementaire_distincte_provisionnee_pour_cette_op"));
}
for(const c of ['F','G']){
 hypothesisTooltip(`${c}8`,t("contenus.sans_objet_le_progiciel_de_cette_option_buy_existe_deja_le_projet_"));
 hypothesisTooltip(`${c}9`,t("contenus.sans_objet_aucun_budget_de_construction_du_progiciel_editeur_n_est"));
 hypothesisTooltip(`${c}15`,t("contenus.sans_objet_le_gain_de_continuite_est_une_hypothese_propre_aux_opti"));
}
for(const c of ['C','D','E'])hypothesisTooltip(`${c}23`,t("contenus.sans_objet_make_n_achete_pas_d_offre_annuelle_de_progiciel_groupee"));
hypothesisTooltip('C15',t("contenus.10_par_defaut_gain_de_continuite_d_equipe_suppose_sur_l_ancre_d_in"));
hypothesisTooltip('F13',t("contenus.38_mois_18_mois_de_pilote_20_mois_de_deploiement_dans_le_copil_5_p"));
hypothesisTooltip('G13',t("contenus.30_mois_18_mois_12_mois_dans_le_copil_5_p_7_les_autres_cinematique"));
hypothesisTooltip('F14',t("contenus.projection_microsoft_complements_flow_estimes_pilotage_preparation"));
hypothesisTooltip('G14',t("contenus.le_budget_de_reference_additionne_les_lots_delaware_les_complement"));
hypothesisTooltip('F18',t("contenus.services_client_microsoft_non_ventiles_entre_core_et_integration_e"));
hypothesisTooltip('G18',t("contenus.services_client_sap_groupes_1_05_m_an_de_mco_monitoring_et_tma_de_"));
for(const c of ['F','G'])hypothesisTooltip(`${c}20`,t("contenus.30_k_an_provision_de_capacite_supplementaire_pour_les_extensions_a"));
hypothesisTooltip('F21',t("contenus.36_k_an_provision_de_plateforme_de_flux_achetee_separement_pour_mi"));
hypothesisTooltip('G21',t("contenus.100_k_an_provision_sap_integration_suite_exclue_de_l_offre_chiffre"));
hypothesisTooltip('F22',t("contenus.24_k_an_provision_de_droits_power_platform_et_connecteurs_premium_"));
hypothesisTooltip('G22',t("contenus.aucune_licence_supplementaire_distincte_provisionnee_au_dela_de_l_"));
hypothesisTooltip('F23',t("contenus.premiere_annuite_microsoft_documentee_a_pleine_capacite_abonnement"));
hypothesisTooltip('G23',t("contenus.annuite_sap_de_reference_a_pleine_capacite_offre_groupee_rise_selo"));
hypothesisTooltip('C28',t("contenus.2_5_central_extrapolation_de_l_indice_syntec_2024_2025_2_48_qui_me"));
hypothesisTooltip('C29',t("contenus.3_central_convention_de_2_macro_1_point_pour_revisions_commerciale"));
hypothesisTooltip('C30',t("contenus.1_central_convention_prudente_pour_un_panier_cloud_constant_avec_b"));
// Explain calculated outputs without storing a second, stale copy of their simulated value.
for(const c of columns)hypothesisTooltip(c+'24',t("contenus.ce_total_est_la_somme_des_composantes_annuelles_ci_dessus_en_k_ht_"));
for(const c of ['D','E'])hypothesisTooltip(c+'15',t("contenus.ce_pourcentage_reprend_le_gain_de_continuite_saisi_une_seule_fois_"));
const summaryMeaning={
 B6:t("contenus.chaque_ligne_represente_une_solution_alternative_pour_couvrir_le_p"),
 C6:t("contenus.make_signifie_que_le_core_system_flow_est_construit_buy_signifie_q"),
 D6:t("contenus.cette_colonne_cumule_le_budget_de_construction_du_core_system_enga"),
 E6:t("contenus.cette_colonne_cumule_les_depenses_initiales_d_adaptation_de_raccor"),
 F6:t("contenus.cette_colonne_additionne_le_mco_et_le_run_reellement_engages_sur_l"),
 G6:t("contenus.le_total_en_m_ht_additionne_les_trois_postes_de_depense_de_la_solu"),
 H6:t("contenus.il_s_agit_du_nombre_d_annees_equivalentes_de_service_complet_apres")
};
for(const [a,b] of Object.entries(summaryMeaning))tooltip(syn,a,b);
for(let i=0;i<5;i++){
 const r=7+i,o=data.options[i];
 tooltip(syn,'B'+r,t("contenus.variable_est_l_une_des_cinq_options_comparees_variable", {p0: o.nom, p1: i<3?t("contenus.le_projet_construit_le_core_system_flow_puis_l_integre_chez_beauma"):t("contenus.le_projet_adapte_et_deploie_un_progiciel_existant_chez_beaumanoir")}));
 tooltip(syn,'C'+r,i<3?t("contenus.cette_option_make_finance_la_construction_du_core_system_son_integ"):t("contenus.cette_option_buy_achete_les_droits_et_services_du_progiciel_avec_l"));
 for(const c of ['D','E','F','G','H'])tooltip(syn,c+r,`${o.nom}. ${c==='D'&&i>=3?t("contenus.sans_objet_le_progiciel_existe_deja_le_budget_d_integration_financ"):summaryMeaning[c+'6']}`);
}
tooltip(plan,'B6',t("contenus.les_annees_1_a_10_partent_d_une_date_de_depart_commune_aux_cinq_op"));
for(let i=0;i<5;i++)tooltip(plan,columns[i]+'6',t("contenus.cette_colonne_presente_variable_les_autres_colonnes_sont_des_alter", {p0: data.options[i].nom}));
for(let y=1;y<=10;y++){
 const r=y+6;tooltip(plan,'B'+r,t("contenus.annee_variable_de_la_fenetre_commune_le_montant_reflete_les_phases", {p0: y}));
 for(let i=0;i<5;i++)tooltip(plan,columns[i]+r,t("contenus.variable_annee_variable_la_depense_en_m_ht_additionne_le_build_l_i", {p0: data.options[i].nom, p1: y}));
}
tooltip(plan,'B17',t("contenus.ce_total_additionne_les_dix_depenses_annuelles_de_chaque_solution_"));
for(const c of columns)tooltip(plan,c+'17',t("contenus.somme_des_annees_1_a_10_dans_cette_colonne_en_m_ht_cette_formule_g"));
tooltip(plan,'B21',t("contenus.le_selecteur_jaune_permet_d_examiner_les_trois_postes_d_une_seule_"));
tooltip(plan,'C21',t("contenus.choisissez_une_solution_dans_la_liste_les_depenses_du_tableau_deta"));
const detailMeaning={24:t("contenus.le_build_finance_la_construction_du_core_system_generique_pour_une"),25:t("contenus.l_integration_et_migration_finance_les_travaux_initiaux_necessaire"),26:t("contenus.le_mco_et_le_run_comprennent_les_services_et_achats_recurrents_le_"),27:t("contenus.ce_total_annuel_additionne_les_trois_postes_du_tableau_pour_la_sol")};
for(const [r,body] of Object.entries(detailMeaning)){
 tooltip(plan,'B'+r,body);
 for(let y=1;y<=10;y++)tooltip(plan,String.fromCharCode(66+y)+r,t("contenus.annee_variable_m_ht_variable_un_tiret_signifie_zero_sur_l_annee_pa", {p0: y, p1: body}));
}
for(let y=1;y<=10;y++)tooltip(plan,String.fromCharCode(66+y)+'23',t("contenus.annee_variable_de_la_fenetre_commune_les_montants_detailles_sont_e", {p0: y}));
const calculationMeaning=explanations.methodes_calcul.map(expandExplanation);
for(let i=0;i<5;i++){
 const r=rowBase(i),o=data.options[i];
 tooltip(calc,'B'+r,t("contenus.ce_bloc_calcule_les_depenses_de_variable_les_parametres_proviennen", {p0: o.nom}));
 for(let y=1;y<=10;y++)tooltip(calc,String.fromCharCode(66+y)+r,t("contenus.annee_variable_de_la_fenetre_commune_de_dix_ans_les_trois_premiere", {p0: y}));
 calculationMeaning.forEach((body,j)=>{
  tooltip(calc,'B'+(r+j+1),body);
  for(let y=1;y<=10;y++){
   let detail=body;
   if(i>=3&&[0,3].includes(j))detail=t("contenus.sans_objet_pour_cette_option_buy_le_projet_ne_construit_pas_le_pro");
   if(i<3&&j===7)detail=t("contenus.cette_option_make_ne_comporte_pas_d_offre_annuelle_de_progiciel_ve");
   tooltip(calc,String.fromCharCode(66+y)+(r+j+1),t("contenus.variable_annee_variable_variable", {p0: o.nom, p1: y, p2: detail}));
  }
 });
}
const scopeMeaning=explanations.definitions_perimetre.map(expandExplanation);
tooltip(scope,'B6',t("contenus.cette_colonne_decrit_les_fonctions_ou_frontieres_a_comparer_le_tab"));
for(const [c,name] of [['C',t("contenus.les_trois_options_make_flow")],['D',t("contenus.microsoft_k3")],['E',t("contenus.sap_omsa")]])tooltip(scope,c+'6',t("contenus.cette_colonne_resume_la_couverture_retenue_pour_variable_avec_les_", {p0: name}));
scopeMeaning.forEach((body,i)=>{
 const r=7+i;tooltip(scope,'B'+r,body);
 for(const c of ['C','D','E'])tooltip(scope,c+r,body);
});
const sourceMeaning={
 7:t("contenus.ce_montant_est_le_budget_de_reference_du_build_du_core_system_en_m"),
 8:t("contenus.pour_make_ce_montant_en_m_ht_est_le_chiffrage_par_activites_conser"),
 9:t("contenus.cette_base_annuelle_en_m_ht_couvre_les_services_de_maintenance_d_e"),
 10:t("contenus.cette_base_annuelle_en_m_ht_correspond_a_l_hebergement_achete_sepa"),
 11:t("contenus.cette_base_annuelle_en_m_ht_couvre_l_ipaas_achete_separement_il_s_"),
 12:t("contenus.cette_base_annuelle_en_m_ht_correspond_aux_licences_complementaire"),
 13:t("contenus.ce_nombre_indique_combien_d_annuites_a_pleine_capacite_sont_docume"),
 19:t("contenus.cette_ligne_isole_la_part_des_services_annuels_affectee_au_core_sy"),
 20:t("contenus.cette_duree_de_reference_du_build_est_exprimee_en_mois_la_valeur_u"),
 21:t("contenus.cette_duree_d_integration_buy_provient_de_la_cinematique_de_depart"),
 22:t("contenus.cette_indication_choisit_le_taux_d_indexation_de_l_ipaas_cloud_pou"),
 23:t("contenus.ce_taux_est_l_hypothese_de_depart_de_l_inflation_des_prestations_d"),
 24:t("contenus.ce_taux_est_l_hypothese_de_depart_de_l_inflation_des_licences_et_a"),
 25:t("contenus.ce_taux_est_l_hypothese_de_depart_de_l_evolution_des_achats_cloud_")
};
tooltip(src,'B6',t("contenus.les_montants_de_reference_de_cet_onglet_sont_en_m_ht_les_bases_ann"));
for(let i=0;i<5;i++)tooltip(src,columns[i]+'6',t("contenus.cette_colonne_rassemble_les_donnees_de_reference_de_variable_les_c", {p0: data.options[i].nom}));
for(let r=7;r<=25;r++){
 const body=sourceMeaning[r]||t("contenus.cette_ligne_presente_une_annuite_documentee_de_l_offre_editeur_a_p");
 tooltip(src,'B'+r,body);
 for(let i=0;i<5;i++){
  const c=columns[i],o=data.options[i];let detail=body;
  if(r>=14&&r<=18){
   detail=i<3?t("contenus.cette_option_make_ne_comporte_pas_d_offre_annuelle_de_progiciel_ve_2"):i===4?(r<=15?t("contenus.cette_annuite_sap_de_reference_reprend_une_annee_a_pleine_capacite"):t("contenus.aucune_autre_annuite_stabilisee_n_est_enregistree_ici_la_case_vide")):t("contenus.cette_reference_reprend_l_annuite_variable_de_l_offre_microsoft_a_", {p0: r-13});
  }else if(i>=3&&[7,20].includes(r))detail=t("contenus.sans_objet_le_progiciel_buy_existe_deja_le_projet_beaumanoir_ne_fi");
  else if(i>=3&&r===19)detail=t("contenus.la_part_core_buy_n_est_pas_ventilee_la_case_vide_ne_vaut_pas_zero_");
  else if(i<3&&r===21)detail=t("contenus.cette_ligne_est_reservee_aux_durees_buy_documentees_la_duree_make_");
  const value=src.getRange(c+r).values?.[0]?.[0];
  if((r>=14&&r<=21)||value!==null&&value!==undefined&&value!=='')tooltip(src,c+r,`${o.nom}. ${detail}`);
 }
}
src.getRange('F7:G7').setNumberFormat(t("formats.variable"));src.getRange('F20:G20').setNumberFormat(t("formats.variable"));
refs.forEach(([label],j)=>{
 const r=28+j*2;
 const context=j<12?t("contenus.cette_reference_explique_les_entrees_du_modele_leur_methode_ou_une"):j===16?t("contenus.ce_cas_illustre_un_deploiement_retail_et_ses_integrations_aucun_bu"):j>=25?t("contenus.cette_reference_precise_les_limites_de_comparaison_ou_de_methode_i"):t("contenus.ce_projet_ou_cette_etude_sert_de_controle_externe_d_ordre_de_grand");
 const body=`« ${label} ». ${context}`;
 tooltip(src,'B'+r,body);tooltip(src,'C'+r,body);
});
const extraHyp={
 39:t("contenus.ce_budget_en_k_ht_est_celui_utilise_dans_la_simulation_active_il_r"),
 40:t("contenus.ce_contrepoint_en_k_ht_vient_du_chiffrage_make_par_activites_conse"),
 41:t("contenus.cet_ecart_en_k_ht_est_la_difference_entre_le_budget_actif_et_le_ch"),
 55:t("contenus.cette_ligne_reprend_les_jours_et_le_prix_du_lot_2_delaware_le_prix"),
 56:t("contenus.cette_ligne_reprend_les_jours_et_le_prix_du_lot_3_delaware_le_retr"),
 57:t("contenus.cette_ligne_totalise_les_jours_finance_et_fp_a_retires_a_titre_ind"),
 58:t("contenus.cette_ancre_en_k_ht_est_le_budget_sap_diminue_du_retrait_indicatif"),
 59:t("contenus.ce_montant_en_k_ht_regroupe_les_complements_d_integration_estimes_"),
 60:t("contenus.ce_montant_en_k_ht_correspond_aux_lots_delaware_apres_le_retrait_i"),
 62:t("contenus.le_gain_en_k_ht_est_l_ancre_avant_bonus_multipliee_par_le_taux_de_"),
 63:t("contenus.ce_budget_en_k_ht_est_l_ancre_avant_bonus_diminuee_du_gain_de_cont"),
 65:t("contenus.cette_base_rapproche_le_prix_delaware_hors_retrait_finance_de_ses_"),
 67:t("contenus.ce_profil_couvre_l_integration_metier_et_la_configuration_les_jour"),
 68:t("contenus.ce_profil_couvre_l_integration_it_les_donnees_et_la_qualification_"),
 69:t("contenus.ce_profil_couvre_les_developpements_java_et_react_de_la_sensibilit"),
 70:t("contenus.cette_part_de_pilotage_est_deja_comprise_dans_les_jours_repartis_e"),
 71:t("contenus.ce_sous_total_additionne_les_parts_les_jours_et_les_couts_des_quat"),
 72:t("contenus.aucun_achat_d_outillage_additionnel_n_est_retenu_dans_ce_test_ce_z"),
 74:t("contenus.cette_ligne_valorise_les_jours_complementaires_de_configuration_au"),
 75:t("contenus.cette_ligne_valorise_les_jours_complementaires_d_integration_it_et"),
 76:t("contenus.cette_ligne_valorise_les_jours_complementaires_d_extensions_java_e"),
 77:t("contenus.ce_sous_total_additionne_les_jours_et_les_couts_des_complements_d_"),
 78:t("contenus.aucun_outillage_supplementaire_n_est_retenu_dans_ce_test_un_besoin"),
 79:t("contenus.cette_provision_de_pilotage_porte_uniquement_sur_les_complements_h"),
 80:t("contenus.cette_provision_en_k_ht_couvre_la_preparation_prevue_dans_l_etude_"),
 81:t("contenus.ce_contrepoint_esn_en_k_ht_additionne_les_profils_de_la_base_les_c"),
 82:t("contenus.f_montre_l_ecart_en_k_ht_entre_le_contrepoint_esn_et_l_ancre_make_"),
 83:t("contenus.f_presente_un_test_sap_buy_en_k_ht_avec_des_complements_revalorise"),
 84:t("contenus.cette_sensibilite_applique_le_tarif_journalier_bas_de_programme_a_"),
 85:t("contenus.cette_sensibilite_applique_le_tarif_journalier_haut_de_programme_a")
};
const extraCells={39:columns,40:['C','D','E'],41:['C','D','E'],55:columns,56:columns,57:['D','G'],58:['G'],59:['G'],60:['G'],62:['G'],63:['G'],65:['E','F','G'],67:columns,68:columns,69:columns,70:columns,71:['C','D','F'],72:['F'],74:['C','E','F'],75:['C','E','F'],76:['C','E','F'],77:['C','F'],78:['F'],79:['C','F'],80:['F'],81:['F'],82:['F','G'],83:['F','G'],84:['E','F'],85:['E','F']};
for(const [r,body] of Object.entries(extraHyp)){
 hypothesisTooltip('B'+r,body);for(const c of extraCells[r])hypothesisTooltip(c+r,body);
}
// All six sheets share one note definition and one native styling pass.
visual.notes=[...cellTooltips.values()].map(({sheet,address,body})=>({sheet,address,body}));
for(const entry of cellTooltips.values())wb.notes.add({id:`${entry.sheet}:${entry.address}`,target:{cell:{sheetName:entry.sheet,sheetId:entry.sheetId,address:entry.address}},authorId:'',createdAt:'',body:{plainText:entry.body}});
if(!checkingModel)await fs.writeFile('tmp/investissement-10-ans/layout.json',JSON.stringify(visual,null,2));

wb.recalculate();
if(checkingModel){
 const actual=syn.getRange('D7:G11').values;
 const fields=['build','integration','mco_run','total'];
 for(let i=0;i<5;i++)for(let j=0;j<4;j++)if(Math.abs(Number(actual[i][j])*1e6-expected.options[i].totaux_eur_ht[fields[j]])>0.05)throw new Error('ERR_MODEL_TOTAL');
 const formulas=[];
 for(const s of [syn,hyp,plan,scope,calc,src]){
  const limit=visual.sheets.find(v=>v.name===s.name);
  const cells=s.getRange(t("contenus.a1_variablevariable",{p0:limit.last,p1:limit.end})).formulas;
  cells.forEach((row,r)=>row.forEach((value,c)=>{if(value)formulas.push({sheet:s.name,address:`${String.fromCharCode(65+c)}${r+1}`,value});}));
 }
 console.log(JSON.stringify({sheets:visual.sheets.length,notes:visual.notes.length,totals:actual,captions:emittedText,tooltips:visual.notes,formulas}));
 process.exit(0);
}
console.log((await wb.inspect({kind:'region',sheetId:syn.name,range:'B6:H11',maxChars:2500,tableMaxRows:6,tableMaxCols:7})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!',options:{useRegex:true,maxResults:15},maxChars:2000})).ndjson);
if(!checkingModel)await fs.mkdir('tmp/investissement-10-ans',{recursive:true});
const out=await SpreadsheetFile.exportXlsx(wb);await out.save('tmp/investissement-10-ans/authored.xlsx');
for(const [s,range]of [[syn,'B2:H36'],[hyp,'B2:G9'],[hyp,'B11:G15'],[hyp,'B16:G24'],[hyp,'B27:G35'],[hyp,'B37:G51'],[hyp,'B53:G63'],[hyp,'B64:G87'],[plan,'B2:L46'],[calc,'B70:L82'],[src,'B2:G25'],[src,'B27:G86'],[scope,'B2:E23']]){
 try{const img=await wb.render({sheetName:s.name,range,scale:1.4,format:'png'});await fs.writeFile(`tmp/investissement-10-ans/${s.name}-${range.replace(':','-')}.png`,new Uint8Array(await img.arrayBuffer()));}catch(e){console.log(t("contenus.render"),s.name,e.message);}
}
console.log(t("contenus.excel_authored_native_verification_still_required"));
