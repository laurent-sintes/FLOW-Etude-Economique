import {useEffect,useState} from 'react';
import {useStudy,useFormat,request,type Data} from './context';
import {Drawer,SourceLink} from './components';
import {MethodText} from './MethodDocument';
import {MarketSourceLink,MarketSourceList} from './MarketSources';

export function MarketReferenceDrawer({view,onClose}:{view:'projects'|'services';onClose:()=>void}){
 const {data}=useStudy(),{money,n}=useFormat(),T=data.ui.essential.market_study.references;
 const [references,setReferences]=useState<Data|null>(null),[error,setError]=useState(false),[reload,setReload]=useState(0);
 useEffect(()=>{
  let current=true;setReferences(null);setError(false);
  request<Data>('/api/market-references?model_version='+encodeURIComponent(data.model_version))
   .then(result=>{if(current){if(Array.isArray(result.projects)&&Array.isArray(result.services))setReferences(result);else setError(true);}})
   .catch(()=>{if(current)setError(true);});
  return()=>{current=false;};
 },[data.model_version,reload]);
 const interval=(low:number|null|undefined,high:number|null|undefined,currency:string,normalized=false)=>{
  if(typeof low!=='number')return T.unknown;
  const number=(value:number)=>currency==='EUR'?money(value):n(value,0);
  const unit=normalized?data.ui.labels.normalized_money_unit:currency==='EUR'?data.ui.labels.currency_unit:currency;
  return `${number(low)}${typeof high==='number'&&high!==low?' – '+number(high):''} ${unit}`;
 };
 const evidence=(row:Data)=>{
  const localized=new Set(row.proofs.map((proof:Data)=>proof.source));
  return <div className="market-reference-sources">{row.proofs.map((proof:Data,index:number)=><p key={`${proof.source}-${index}`}><MarketSourceLink path={proof.source} label={T.source}>{proof.localisation}</MarketSourceLink></p>)}<MarketSourceList paths={row.sources.filter((source:string)=>!localized.has(source))} label={T.source}/><SourceLink path={row.source_ref}>{T.registry}</SourceLink></div>;
 };
 return <Drawer title={view==='projects'?T.project_drawer_title:T.services_drawer_title} onClose={onClose} wide>
  <div className="market-reference-reading">
   {!references&&(error?<div role="alert"><p>{T.error}</p><button type="button" className="secondary" onClick={()=>setReload(value=>value+1)}>{T.retry}</button></div>:<p role="status">{T.loading}</p>)}
   {references&&<>
    <p className="market-reference-intro"><MethodText>{view==='projects'?T.project_intro:T.services_intro}</MethodText></p>
    <aside className="core-method-callout"><p><MethodText>{view==='projects'?references.transposition:references.operations_note}</MethodText></p></aside>
    {view==='projects'&&<div className="market-reference-normalization"><p><MethodText>{references.normalization}</MethodText></p><SourceLink path={references.monetary_sources_ref}>{T.monetary_sources}</SourceLink></div>}
    <div className="market-reference-list">{references[view].map((row:Data)=><article key={row.id} aria-labelledby={'market-reference-'+row.id}>
     <header><h3 id={'market-reference-'+row.id}>{row.name}</h3><p>{row.platform} · {row.country}</p></header>
     {view==='projects'?<>
      <p><strong>{T.scope} :</strong> <MethodText>{row.scope}</MethodText></p>
      <div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={row.name}><table className="core-method-table market-reference-price-table"><thead><tr><th scope="col">{T.original}</th><th scope="col">{T.normalized}</th><th scope="col">{T.transposed}</th></tr></thead><tbody><tr><td>{interval(row.price.min,row.price.max,row.price.devise)}</td><td>{interval(row.normalized?.min_eur,row.normalized?.max_eur,'EUR',true)}</td><td>{interval(row.transposed.cout_central_eur_2026,row.transposed.cout_central_eur_2026,'EUR',true)}</td></tr></tbody></table></div>
      <dl className="market-reference-context"><div><dt>{T.date}</dt><dd>{row.price.date_prix||T.unknown}</dd></div><div><dt>{T.status}</dt><dd>{data.ui.reading.price_kinds[row.price.statut]}</dd></div><div><dt>{T.included}</dt><dd><MethodText>{row.included}</MethodText></dd></div><div><dt>{T.excluded}</dt><dd><MethodText>{row.excluded}</MethodText></dd></div><div><dt>{T.evidence}</dt><dd><MethodText>{row.price_evidence}</MethodText></dd></div></dl>
      <p><strong>{T.lesson} :</strong> <MethodText>{row.lesson}</MethodText></p><p className="market-reference-limit"><strong>{T.limit} :</strong> <MethodText>{row.transposed.limite}</MethodText></p>
     </>:<>
      <p className="market-reference-status">{row.status}</p><p><MethodText>{row.scope}</MethodText></p>
      {row.observations.length>0?<div className="market-service-observations">{row.observations.map((observation:Data,index:number)=><section key={index} aria-labelledby={`market-observation-${row.id}-${index}`}><h4 id={`market-observation-${row.id}-${index}`}>{observation.libelle}</h4><dl className="market-reference-context"><div><dt>{T.amount}</dt><dd className="market-reference-amount">{interval(observation.min,observation.max,observation.devise)}</dd></div><div><dt>{T.period}</dt><dd>{observation.periode}</dd></div><div><dt>{T.scope}</dt><dd><MethodText>{observation.assiette}</MethodText></dd></div><div><dt>{T.evidence}</dt><dd><MethodText>{observation.evidence}</MethodText></dd></div></dl><MarketSourceLink path={observation.source} label={T.source}>{observation.localisation}</MarketSourceLink></section>)}</div>:<p className="market-reference-limit">{T.no_observations}</p>}
     </>}
     {evidence(row)}
    </article>)}</div>
   </>}
  </div>
 </Drawer>;
}
