import './workload.css';
import {createContext,useContext,useEffect,useState,type ReactNode} from 'react';
import {Info,Hammer,ShoppingCart,type LucideIcon} from 'lucide-react';
import {useStudy,useFormat,request,type Data,type Option,type Projection} from './context';
import {isModelDataReference} from './documentVisibility';
import {Drawer,SourceLink} from './components';
import {MethodText} from './MethodDocument';
import {EconomicContext,EconomicNext} from './EconomicJourney';
import {MarketSourceLink,MarketSourceList} from './MarketSources';
import './essential.css';
import './marketProducts.css';

export type Proof={title:string;text:string;source?:string;value?:string};
const EvidenceContext=createContext<(proof:Proof)=>void>(()=>{});
export const useEvidence=()=>useContext(EvidenceContext);
export function EvidenceProvider({open,children}:{open:(proof:Proof)=>void;children:ReactNode}){return <EvidenceContext.Provider value={open}>{children}</EvidenceContext.Provider>;}

export function ProofDialog({proof,onClose}:{proof:Proof;onClose:()=>void}){
 const {data}=useStudy(),C=data.ui.essential.economic_context;
 const source=proof.source&&!isModelDataReference(proof.source)?proof.source:undefined;
 return <Drawer title={proof.title} onClose={onClose}>
  {proof.value&&<p className="essential-proof-value">{proof.value}</p>}
  <p><MethodText>{proof.text}</MethodText></p>
  {source&&<div className="essential-proof-source"><SourceLink path={source}>{data.ui.essential.full_source}</SourceLink></div>}
  <section className="economic-proof-path"><h3>{C.proof_title}</h3><p>{C.proof_note}</p><ul>{C.proof_links.map((link:Data)=><li key={link.href}><a href={link.href} onClick={onClose}>{link.label}</a></li>)}</ul></section>
 </Drawer>;
}

export function EvidenceButton({proof,label}:{proof:Proof;label?:string}){const open=useEvidence();const {data}=useStudy();return <button className="essential-evidence" type="button" onClick={()=>open(proof)} aria-label={label||data.ui.essential.explain+' · '+proof.title} title={label||data.ui.essential.explain}><Info size={16}/></button>;}

export function HorizonPicker({value,onChange}:{value:number;onChange:(value:number)=>void}){const {data}=useStudy();return <div className="essential-horizons" role="group" aria-label={data.ui.labels.horizon}>{data.ui.horizons.map((year:number)=><button key={year} type="button" className={value===year?'active':''} aria-pressed={value===year} onClick={()=>onChange(year)}>{year} {data.ui.labels.year}</button>)}</div>;}

const strategyIcons:Record<string,LucideIcon>={Make:Hammer,Buy:ShoppingCart};
export function HorizonFacts({option,horizon}:{option:Option;horizon:number}){
 const {data}=useStudy(),{amount,n}=useFormat(),E=data.ui.essential,C=E.economic_context;
 const row=option.horizons.find(item=>item.years===horizon)!;
 return <dl className="economic-horizon-facts">
  <div><dt>{E.service_years}</dt><dd>{n(row.service_years,1)} {E.years}</dd></div>
  <div><dt>{C.service_start}</dt><dd>{n(option.service_start_month,1)}</dd></div>
  <div><dt>{E.remaining}</dt><dd>{amount(row.remaining)}</dd></div>
 </dl>;
}

export function Comparison({projection,horizon}:{projection:Projection;horizon:number}){
 const {data}=useStudy(),{amount}=useFormat(),E=data.ui.essential,C=E.economic_context;
 const h=(o:Option)=>o.horizons.find(item=>item.years===horizon)!;
 const phases=[{key:'build',label:E.costs.build},{key:'integration',label:E.costs.integration},{key:'mco_run',label:E.costs.services}];
 return <section className="essential-comparison" id="economic-simulation-results" tabIndex={-1} aria-labelledby="economic-results-heading">
  <div className="essential-section-top"><h2 id="economic-results-heading" tabIndex={-1}>{E.comparison_title} · {horizon} {E.years}</h2></div>
  <div className="essential-option-list">{projection.options.map(o=>{const row=h(o),reference=h(data.baseline.options.find(item=>item.stack===o.stack)!),delta=row.totals.total-reference.totals.total,ModeIcon=strategyIcons[o.mode];return <article key={o.stack} className="essential-option" data-option={o.stack}>
   <div className="essential-option-main"><div><strong>{o.name}</strong><small className={'essential-mode essential-mode-'+o.mode.toLowerCase()}><ModeIcon aria-hidden="true" size={14}/>{o.mode}</small></div><div className="essential-option-total"><strong>{amount(row.totals.total)}</strong><EvidenceButton proof={{title:E.proofs.total.title+' · '+o.name,value:amount(row.totals.total),text:E.proofs.total.text,source:E.proofs.total.source}}/></div></div>
   <div className="economic-reference-delta"><span>{C.reference_amount} <strong>{amount(reference.totals.total)}</strong></span><span>{C.delta} <strong>{delta>0?'+':''}{amount(delta)}</strong></span></div>
   <HorizonFacts option={o} horizon={horizon}/>
   <dl className="economic-budget-parts">{phases.map(phase=><div key={phase.key}><dt>{phase.label}</dt><dd>{amount(row.totals[phase.key as keyof typeof row.totals])}</dd></div>)}</dl>
  </article>;})}</div>
  <p className="essential-caveat">{C.remaining_note}</p>
 </section>;
}

export function AnnualProjection({projection,stack,onStackChange,onClose,showOptionPicker=true}:{projection:Projection;stack:string;onStackChange:(stack:string)=>void;onClose?:()=>void;showOptionPicker?:boolean}){
 const {data}=useStudy(),{amount}=useFormat(),E=data.ui.essential,S=E.simulation;
 const current=projection.options.find(o=>o.stack===stack)||projection.options[0];
 let cumulative=0;
 return <section className="essential-annual"><div className="essential-section-top"><div className="essential-annual-heading"><h2>{S.annual_title}</h2><EvidenceButton proof={E.proofs.calendar}/></div>{onClose&&<button className="text-button" onClick={onClose}>{S.back}</button>}</div>
  <p>{S.annual_note}</p>{showOptionPicker&&<label>{S.choose}<select value={current.stack} onChange={e=>onStackChange(e.target.value)}>{projection.options.map(o=><option key={o.stack} value={o.stack}>{o.name}</option>)}</select></label>}
  <div className="essential-annual-scroll"><table className="essential-annual-table"><thead><tr><th scope="col">{S.year}</th><th scope="col">{S.annual_spend}</th><th scope="col">{S.annual_cumulative}</th></tr></thead><tbody>{current.annual.map(year=>{cumulative=Math.round((cumulative+year.total)*100)/100;return <tr key={year.annee}><th scope="row">{S.year} {year.annee}</th><td>{amount(year.total)}</td><td>{amount(cumulative)}</td></tr>;})}</tbody></table></div>
 </section>;
}

function phaseAmount(option:Option,key:string){return key==='obtention'?option.obtention:key==='integration'?option.integration:Math.round(Object.values(option.annual_responsibilities).reduce((total,value)=>total+value,0)*100)/100;}

export function ComparePage(){
 const {data}=useStudy(),{amount,annualAmount}=useFormat(),E=data.ui.essential,parts=data.ui.composable.rows as Data[];
 const options=data.baseline.options;
 return <div className="essential-page essential-structure"><EconomicContext page="comparer"/><p className="essential-structure-scope">{E.structure.scope}</p>{E.structure.phases.map((phase:Data)=>{
  const max=Math.max(...options.map(o=>phaseAmount(o,phase.key)),1);
  const legend=phase.key==='services'?parts.filter(p=>options.some(o=>o.annual_responsibilities[p.key]>0)):[];
  return <section className="essential-structure-phase" key={phase.key}><div className="essential-structure-heading"><div><h2>{phase.title}</h2><small>{phase.unit}</small></div><EvidenceButton proof={phase.proof}/></div><p className="economic-phase-note"><MethodText>{phase.note}</MethodText></p><div className="essential-structure-rows">{options.map(o=>{
   const value=phaseAmount(o,phase.key),ModeIcon=strategyIcons[o.mode],format=phase.key==='services'?annualAmount:amount;
   const segments=phase.key==='services'?legend.map(p=>({key:p.key,label:p.annual_label||p.label,color:p.color,value:o.annual_responsibilities[p.key]||0})).filter(p=>p.value>0):[{key:phase.key,label:phase.title,color:phase.color,value}];
   return <div className="essential-structure-row" key={o.stack}><div className="essential-structure-option"><strong>{o.name}</strong><span className={'essential-mode essential-mode-'+o.mode.toLowerCase()}><ModeIcon size={14} aria-hidden="true"/>{o.mode}</span></div><div className="essential-structure-bar" role="img" aria-label={segments.map(p=>p.label+' : '+format(p.value)).join(' · ')}><div style={{width:100*value/max+'%'}}>{segments.map(p=><span key={p.key} style={{width:100*p.value/value+'%',background:p.color}} title={p.label+' · '+format(p.value)}/>)}</div></div><strong className="essential-structure-amount">{format(value)}</strong></div>;
  })}</div>{legend.length>0&&<div className="essential-structure-legend">{legend.map(p=><span key={p.key}><i style={{background:p.color}}/>{p.annual_label||p.label}</span>)}</div>}</section>;
 })}<EconomicNext page="comparer"/></div>;
}

export function ProjectionPage(){
 const {data,session,setSession}=useStudy(),{amount,money}=useFormat(),E=data.ui.essential,P=E.projection;
 const [stack,setStack]=useState(data.baseline.options[0].stack);
 const options=data.baseline.options,chosen=options.find(o=>o.stack===stack)||options[0];
 const yearMax=Math.max(...chosen.annual.map(row=>row.total),1);
 const horizonValue=(o:Option)=>o.horizons.find(h=>h.years===session.horizon)!.totals.total;
 const horizonMax=Math.max(...options.map(horizonValue),1);
 return <div className="essential-page essential-projection"><EconomicContext page="se-projeter"/><div className="essential-toolbar"><HorizonPicker value={session.horizon} onChange={horizon=>setSession(s=>({...s,horizon}))}/><span>{E.reference}</span></div>
  <section className="essential-projection-panel"><div className="essential-section-top"><h2>{P.horizon_title} · {session.horizon} {E.years}</h2><EvidenceButton proof={E.proofs.total}/></div><p>{P.horizon_note}</p><div className="essential-projection-bars">{options.map(o=><div key={o.stack} className="economic-projection-option"><div className="essential-projection-bar-row"><strong>{o.name}</strong><div role="img" aria-label={o.name+' · '+amount(horizonValue(o))}><span style={{width:100*horizonValue(o)/horizonMax+'%',background:data.ui.option_colors[o.stack]}}/></div><b>{amount(horizonValue(o))}</b></div><HorizonFacts option={o} horizon={session.horizon}/></div>)}</div><p className="essential-caveat">{E.economic_context.remaining_note}</p></section>
  <section className="essential-projection-panel"><div className="essential-section-top"><h2>{P.chart_title}</h2><EvidenceButton proof={E.proofs.calendar}/></div><p>{E.economic_context.schedule_note}</p><label className="essential-select">{P.selected_option}<select value={chosen.stack} onChange={e=>setStack(e.target.value)}>{options.map(o=><option key={o.stack} value={o.stack}>{o.name}</option>)}</select></label><small className="essential-chart-unit">{P.chart_unit}</small><div className="essential-chart-scroll"><svg viewBox="0 0 760 220" role="img" aria-label={P.chart_title+' · '+chosen.name}>{[0,0.5,1].map(f=><g key={f}><line x1="60" x2="745" y1={180-f*150} y2={180-f*150} className="chart-grid"/><text x="54" y={184-f*150} textAnchor="end">{money(yearMax*f)}</text></g>)}{chosen.annual.map((row,index)=>{const x=70+index*45,height=row.total/yearMax*150;return <g key={row.annee}><rect x={x} y={180-height} width="27" height={height} rx="3" fill={data.ui.option_colors[chosen.stack]}><title>{P.year+' '+row.annee+' · '+amount(row.total)}</title></rect><text x={x+13.5} y="205" textAnchor="middle">{row.annee}</text></g>;})}</svg></div></section>
  <AnnualProjection projection={data.baseline} stack={chosen.stack} onStackChange={setStack} showOptionPicker={false}/><EconomicNext page="se-projeter"/>
 </div>;
}

function marketItems(value:unknown):string[]{return Array.isArray(value)?value.map(String):value?[String(value)]:[];}

function MarketProofList({paths,label}:{paths:string[];label:string}){
 return <MarketSourceList paths={paths} label={label}/>;
}

function MarketSingularitySection({frame,profile,labels}:{frame:Data;profile:Data;labels:Data}){
 const M=labels,sectors=['retail','ecommerce','wholesale'];
 return <section className="essential-market-singularity"><h3>{M.singularity_title}</h3><p>{frame.methode}</p><p className="essential-market-note">{frame.prudence}</p><SourceLink path={frame.preuve_ref}>{M.singularity_study}</SourceLink>
  <div className="essential-market-singularity-grid">
   <article><h4>{M.singularity_atout} · {profile.atout.titre}</h4><p>{profile.atout.constat}</p><p><strong>{M.singularity_comparison} :</strong> {profile.atout.comparaison}</p><p><strong>{M.singularity_limit} :</strong> {profile.atout.limite}</p><MarketProofList paths={profile.atout.preuves} label={M.source}/></article>
   <article><h4>{M.singularity_extension}</h4><p><strong>{M.singularity_beyond} :</strong> {profile.extension.au_dela_flow}</p><p><strong>{M.singularity_complements} :</strong> {profile.extension.complements_flow}</p><p><strong>{M.singularity_limit} :</strong> {profile.extension.limite}</p><MarketProofList paths={profile.extension.preuves} label={M.source}/></article>
   <article><h4>{M.singularity_integration}</h4><p>{profile.integration.mecanismes}</p><p><strong>{M.singularity_limit} :</strong> {profile.integration.limite}</p><MarketProofList paths={profile.integration.preuves} label={M.source}/></article>
   <article><h4>{M.singularity_load}</h4><p>{profile.charge.mecanismes}</p><p><strong>{M.singularity_observed} :</strong> {profile.charge.repere_observe??M.singularity_no_measure}</p><p><strong>{M.singularity_limit} :</strong> {profile.charge.limite}</p><MarketProofList paths={profile.charge.preuves} label={M.source}/></article>
  </div>
  <h4>{M.singularity_sectors}</h4><div className="essential-market-sector-grid">{sectors.map(sector=>{const item=profile.commerce[sector];return <article key={sector}><h5>{M.singularity_sector_labels[sector]}</h5><span>{M.singularity_scope_labels[item.statut]??item.statut}</span><p>{item.constat}</p><p><strong>{M.singularity_limit} :</strong> {item.limite}</p><MarketProofList paths={item.preuves} label={M.source}/></article>;})}</div>
 </section>;
}

function MarketOssCodeDetails({study,labels}:{study:Data;labels:Data}){
 const {n}=useFormat(),M=labels,calculation=study.calcul_cocomo;
 const components=calculation?.selections?Object.entries(calculation.selections).map(([name,variant])=>({name,variant:String(variant),measure:study.mesure.composants[name][String(variant)] as Data,jh:calculation.jh_par_composant[name]})):[];
 return <div className="essential-market-code-study"><h4>{M.cocomo_details}</h4>
  <section><h5>{M.scope}</h5><p><strong>{M.scope_object} :</strong> <MethodText>{study.perimetre.objet}</MethodText></p><p>{M.scope_covered} : {n(study.perimetre.bc_total-study.perimetre.bc_exclus.length,0)} · {M.scope_excluded_count} : {n(study.perimetre.bc_exclus.length,0)}</p><p><MethodText>{study.perimetre.exclus}</MethodText></p><p><MethodText>{study.perimetre.assiette_effort}</MethodText></p></section>
  {study.architecture&&<section><h5>{M.architecture}</h5><div className="essential-market-architecture-grid">{study.architecture.technologies?.map((item:Data)=><article key={item.id}><h6>{item.titre}</h6><p><MethodText>{item.description}</MethodText></p>{item.preuve_ref&&<MarketSourceLink path={item.preuve_ref} label={M.source}/>}</article>)}{study.architecture.points_chauds?.map((item:Data)=><article key={item.id}><h6>{item.titre}</h6><p><MethodText>{item.description}</MethodText></p>{item.preuve_ref&&<MarketSourceLink path={item.preuve_ref} label={M.source}/>}</article>)}</div></section>}
  <section><h5>{M.components}</h5><p className="essential-market-note"><MethodText>{M.components_note}</MethodText></p><div className="essential-market-table-scroll" tabIndex={0} role="region" aria-label={M.components}><table><thead><tr><th scope="col">{M.component}</th><th scope="col">{M.variant}</th><th scope="col">{M.files_unit}</th><th scope="col">{M.pncloc_unit}</th><th scope="col">{M.jh_unit}</th></tr></thead><tbody>{components.map(row=><tr key={row.name}><th scope="row">{M.component_labels[row.name]??row.name}</th><td>{M.variant_labels[row.variant]??row.variant}</td><td className="number">{n(row.measure.fichiers,0)}</td><td className="number">{n(row.measure.pncloc,0)}</td><td className="number">{n(row.jh,0)}</td></tr>)}</tbody>{calculation&&<tfoot><tr><th scope="row" colSpan={3}>{M.total_retenu}</th><td className="number">{n(calculation.pncloc_total,0)}</td><td className="number">{n(calculation.jh,0)}</td></tr></tfoot>}</table></div><p><MethodText>{study.mesure.limites}</MethodText></p>{study.mesure.script_ref&&<MarketSourceLink path={study.mesure.script_ref} label={M.source}/>}</section>
  <section><h5>{M.calculation}</h5><p><MethodText>{M.calculation_note}</MethodText></p><p className="essential-market-formula">{M.formula}</p>{calculation&&<div className="essential-market-conversion"><div><span>{M.person_months}</span><strong>{n(calculation.mois_personne,1)} {M.person_month_unit}</strong></div><span aria-hidden="true">→</span><div><span>{M.jh_calculated}</span><strong>{n(calculation.jh,0)} {M.jh_unit}</strong></div></div>}</section>
  <section><h5>{M.method}</h5><p><MethodText>{study.methode.nom}</MethodText></p><dl className="essential-market-method"><div><dt>{M.coefficient}</dt><dd>{n(study.methode.coefficient_a,2)}</dd></div><div><dt>{M.exponent}</dt><dd>{n(study.methode.exposant_nominal,4)}</dd></div><div><dt>{M.hours_month}</dt><dd>{n(study.methode.heures_mois_personne,0)}</dd></div><div><dt>{M.hours_day}</dt><dd>{n(study.methode.heures_jh,0)}</dd></div></dl><p><MethodText>{study.methode.limites}</MethodText></p>{study.methode.source_ref&&<MarketSourceLink path={study.methode.source_ref} label={M.source}/>}</section>
  <section><h5>{M.versions}</h5><div className="essential-market-versions">{study.mesure.versions.map((version:Data)=><article key={version.id}><strong>{M.component_labels[version.id]??version.id} · {version.version}</strong><span>{M.commit} : <code>{version.commit}</code></span><SourceLink path={version.url}>{M.repository}</SourceLink></article>)}</div></section>
 </div>;
}

export function MarketProductDrawer({onClose}:{onClose:()=>void}){
 const {data}=useStudy(),{n,amount}=useFormat(),M=data.ui.essential.market_oss;
 const [study,setStudy]=useState<Data|null>(null),[error,setError]=useState(false),[reload,setReload]=useState(0),[selected,setSelected]=useState('erpnext');
 useEffect(()=>{let current=true;setStudy(null);setError(false);
  request<Data>('/api/market-build?model_version='+encodeURIComponent(data.model_version))
   .then(response=>{if(current){if(response.etude_oss&&response.cadre_comparaison&&response.fiches_produit)setStudy(response);else setError(true);}})
   .catch(()=>{if(current)setError(true);});
  return()=>{current=false;};
 },[data.model_version,reload]);
 const order=['erpnext','odoo-community','tryton','axelor-open-suite','microsoft','sap'],products=study?order.map(id=>study.fiches_produit[id]).filter(Boolean):[];
 const product=products.find(item=>item.id===selected)??products[0];
 const tabKey=(event:React.KeyboardEvent<HTMLButtonElement>,index:number)=>{
  const count=products.length;let next=index;
  if(event.key==='ArrowRight')next=(index+1)%count;
  else if(event.key==='ArrowLeft')next=(index-1+count)%count;
  else if(event.key==='Home')next=0;
  else if(event.key==='End')next=count-1;
  else return;
  event.preventDefault();setSelected(products[next].id);
  const tabs=event.currentTarget.parentElement?.querySelectorAll<HTMLButtonElement>('[role="tab"]');tabs?.[next]?.focus();
 };
 return <Drawer title={M.title} onClose={onClose} wide><div className="essential-market">
  {!study&&(error?<div role="alert" className="essential-market-state"><p>{M.error}</p><button type="button" className="secondary" onClick={()=>setReload(value=>value+1)}>{M.retry}</button></div>:<p role="status" className="essential-market-state">{M.loading}</p>)}
  {study&&product&&<>
   <p className="essential-market-introduction">{study.cadre_comparaison.introduction}</p>
   <div className="essential-market-tabs" role="tablist" aria-label={M.product_tabs}>{products.map((item,index)=><button key={item.id} id={'market-tab-'+item.id} type="button" role="tab" aria-selected={product.id===item.id} aria-controls={'market-panel-'+item.id} tabIndex={product.id===item.id?0:-1} onClick={()=>setSelected(item.id)} onKeyDown={event=>tabKey(event,index)}>{item.nom}</button>)}</div>
   <div id={'market-panel-'+product.id} role="tabpanel" aria-labelledby={'market-tab-'+product.id} tabIndex={0} className="essential-market-panel">
    <header className="essential-market-header"><div><p className="essential-market-eyebrow">{M.product_fiche}</p><h3>{product.nom}</h3></div><dl><div><dt>{M.family}</dt><dd>{M.family_labels[product.famille]??product.famille}</dd></div><div><dt>{M.status}</dt><dd>{M.product_status_labels[product.statut]??product.statut}</dd></div><div><dt>{M.version_edition}</dt><dd>{product.version_edition}</dd></div><div><dt>{M.observation}</dt><dd><time dateTime={product.date_observation}>{product.date_observation}</time></dd></div></dl></header>
    {product.preuve_ref&&<SourceLink path={product.preuve_ref}>{M.product_source}</SourceLink>}
    <section><h3>{M.composition}</h3><div className="essential-market-composition"><div><h4>{M.products_included}</h4><ul>{marketItems(product.composition.produits).map((item,index)=><li key={index}>{item}</li>)}</ul></div><div><h4>{M.technologies}</h4><p>{product.composition.technologies}</p></div></div>{product.composition.preuve_ref&&<MarketSourceLink path={product.composition.preuve_ref} label={M.source}/>}</section>
    {study.cadre_comparaison.singularites?.produits?.[product.id]&&<MarketSingularitySection frame={study.cadre_comparaison.singularites} profile={study.cadre_comparaison.singularites.produits[product.id]} labels={M}/>}
    <section><h3>{M.deployment_references}</h3><p className="essential-market-note">{M.deployment_note}</p>{Array.isArray(product.references_deploiement)?<div className="essential-market-deployments">{product.references_deploiement.map((reference:Data)=><article key={reference.id}><h4>{reference.organisation}</h4><dl><div><dt>{M.deployment_size}</dt><dd>{reference.taille_organisation}</dd></div><div><dt>{M.deployment_entity}</dt><dd>{reference.entite_equipee}</dd></div><div><dt>{M.deployment_use}</dt><dd>{reference.usage_atteste}</dd></div><div><dt>{M.deployment_edition}</dt><dd>{reference.edition_deploiement??M.deployment_unknown}</dd></div><div><dt>{M.deployment_year}</dt><dd>{reference.annee_preuve??M.deployment_undated}</dd></div><div><dt>{M.deployment_recency}</dt><dd>{M.deployment_recency_labels[reference.actualite]??reference.actualite}</dd></div><div><dt>{M.deployment_limit}</dt><dd>{reference.limite_flow}</dd></div></dl><MarketSourceList paths={reference.preuves} label={M.source}/></article>)}</div>:<p className="essential-market-note">{M.deployment_unstudied}</p>}</section>
    <section><h3>{M.code}</h3><p>{M.code_visibility_labels[product.code.observabilite]??product.code.observabilite}</p><div className="essential-market-code-summary">{typeof product.code.pncloc==='number'&&<div><span>{M.pncloc_unit}</span><strong>{n(product.code.pncloc,0)}</strong></div>}{typeof product.code.effort_jh==='number'&&<div><span>{M.diagnostic}</span><strong>{n(product.code.effort_jh,0)} {M.jh_unit}</strong></div>}{product.code.pncloc==null&&product.code.effort_jh==null&&<p>{M.code_unmeasured}</p>}</div><p className="essential-market-note">{product.code.limite}</p>{product.id==='erpnext'&&<MarketOssCodeDetails study={study.etude_oss} labels={M}/>}</section>
    <section><h3>{M.price}</h3><p className="essential-market-note"><MethodText>{product.famille==='proprietaire'?M.buy_price_scope:M.price_scope}</MethodText></p><dl className="essential-market-prices"><div><dt>{M.observed_price}</dt><dd>{typeof product.prix_observe_eur_ht==='number'?amount(product.prix_observe_eur_ht):M.price_unreported}</dd></div><div><dt>{M.flow_price}</dt><dd>{typeof product.prix_retraite_flow_eur_2026==='number'?amount(product.prix_retraite_flow_eur_2026,data.ui.labels.normalized_money_unit):M.price_unreported}</dd></div></dl>{product.famille==='proprietaire'&&<SourceLink path={M.buy_price_source_ref}>{M.buy_price_source}</SourceLink>}</section>
    <section><h3>{M.comparison}</h3><div className="essential-market-axes">{study.cadre_comparaison.axes.map((axis:Data)=>{const item=product.evaluations[axis.id];return <article key={axis.id} aria-labelledby={'market-product-axis-'+axis.id}><header><h4 id={'market-product-axis-'+axis.id}>{axis.titre}</h4><small>{axis.bc_refs?.join(' · ')}</small></header><div className="essential-market-axis"><p><strong>{M.flow_target} :</strong> <MethodText>{axis.cible_flow}</MethodText></p>{item?<><p><strong>{M.product_function} :</strong> <MethodText>{item.fonctionnalite}</MethodText></p><p><strong>{M.offer_status} :</strong> {M.offer_status_labels[item.statut_offre]??item.statut_offre}</p><p><strong>{M.offer} :</strong> <MethodText>{item.offre}</MethodText></p><p><strong>{M.product_limit} :</strong> <MethodText>{item.limite}</MethodText></p><p><strong>{M.flow_parity} :</strong> {M.parity_labels[item.parite_flow]??item.parite_flow}</p>{item.preuves?.length>0&&<MarketSourceList paths={item.preuves} label={M.source}/>}</>:<p>{M.undocumented}</p>}{axis.essai&&<p className="essential-market-test"><strong>{M.test} :</strong> <MethodText>{axis.essai}</MethodText></p>}</div></article>;})}</div></section>
   </div>
   <section className="essential-market-candidates"><h3>{M.candidates}</h3><p>{M.candidates_note}</p><div className="essential-market-candidate-list">{study.candidats_a_etudier.map((candidate:Data)=><article key={candidate.id}><div><h4>{candidate.nom}</h4><span>{M.candidate_priority_labels[candidate.priorite]??candidate.priorite}</span></div><small>{M.candidate_category_labels[candidate.categorie]??candidate.categorie}</small><p>{candidate.motif}</p>{candidate.preuve_ref&&<MarketSourceLink path={candidate.preuve_ref} label={M.source}/>}</article>)}</div></section>
   {product.id==='erpnext'&&<section><h3>{M.conclusion}</h3><p>{study.etude_oss.lecture.conclusion}</p><h4>{M.limits}</h4><p>{study.etude_oss.lecture.limites}</p></section>}
  </>}
 </div></Drawer>;
}

export {ModelPage} from './ModelPage';
