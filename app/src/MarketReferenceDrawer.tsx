import {useEffect,useState} from 'react';
import {useStudy,useFormat,request,type Data} from './context';
import {Drawer,SourceLink} from './components';
import {MethodText} from './MethodDocument';
import {MarketSourceLink,MarketSourceList} from './MarketSources';
import {isModelDataReference} from './documentVisibility';
import {useDossierFocus} from './Dossier';

export function MarketReferences({view,evidenceOnly=false,focus}:{view:'projects'|'services';evidenceOnly?:boolean;focus?:string}){
 const {data}=useStudy(),{money,n}=useFormat(),T=data.ui.essential.market_study.references;
 const [references,setReferences]=useState<Data|null>(null),[error,setError]=useState(false),[reload,setReload]=useState(0);
 useEffect(()=>{
  let current=true;setReferences(null);setError(false);
  request<Data>('/api/market-references?model_version='+encodeURIComponent(data.model_version))
   .then(result=>{if(current){if(Array.isArray(result.projects)&&Array.isArray(result.services))setReferences(result);else setError(true);}})
   .catch(()=>{if(current)setError(true);});
  return()=>{current=false;};
 },[data.model_version,reload]);
 useDossierFocus(references&&focus?focus:undefined);
 const interval=(low:number|null|undefined,high:number|null|undefined,currency:string,normalized=false)=>{
  if(typeof low!=='number')return T.unknown;
  const number=(value:number)=>currency==='EUR'?money(value):n(value,0);
  const unit=normalized?data.ui.labels.normalized_money_unit:currency==='EUR'?data.ui.labels.currency_unit:currency;
  return `${number(low)}${typeof high==='number'&&high!==low?' – '+number(high):''} ${unit}`;
 };
 const evidence=(row:Data)=>{
  const proofs=row.proofs.filter((proof:Data)=>!isModelDataReference(proof.source));
  const localized=new Set(proofs.map((proof:Data)=>proof.source));
  const sources=row.sources.filter((source:string)=>!localized.has(source)&&!isModelDataReference(source));
  if(!proofs.length&&!sources.length&&isModelDataReference(row.source_ref))return null;
  return <div className="market-reference-sources">{proofs.map((proof:Data,index:number)=><p key={`${proof.source}-${index}`}><MarketSourceLink path={proof.source} label={T.source}>{proof.localisation}</MarketSourceLink></p>)}<MarketSourceList paths={sources} label={T.source}/><SourceLink path={row.source_ref}>{T.registry}</SourceLink></div>;
 };
 const selected=references?.[view].find((row:Data)=>'market-reference-'+row.id===focus);
 const link=(row:Data)=>'#preetude-projets?view='+view+'&focus=market-reference-'+row.id;
 const normalization=references&&view==='projects'&&<section className="market-reference-normalization"><h3>{T.normalization_title}</h3><p className="core-method-formula"><MethodText>{references.normalization}</MethodText></p><p><MethodText>{references.normalization_context}</MethodText></p>
     <div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={T.normalization_detail}><table className="core-method-table market-reference-conversions"><caption>{T.normalization_detail}</caption><thead><tr>{[T.conversion_reference,T.index,T.start_period,T.start_index,T.end_index,T.exchange,T.conversion_note].map((label:string)=><th scope="col" key={label}>{label}</th>)}</tr></thead><tbody>{references.projects.filter((row:Data)=>!selected||row.id===selected.id).map((row:Data)=><tr key={row.id}><th scope="row">{row.name}</th><td>{row.normalized?.indice||T.unknown}</td><td>{row.normalized?.periode_depart||T.unknown}</td><td>{typeof row.normalized?.valeur_depart==='number'?n(row.normalized.valeur_depart,4):T.unknown}</td><td>{typeof row.normalized?.valeur_2026==='number'?n(row.normalized.valeur_2026,4):T.unknown}</td><td>{typeof row.normalized?.devise_par_eur==='number'?n(row.normalized.devise_par_eur,4):T.unknown}</td><td>{row.normalized?.reserve?<MethodText>{row.normalized.reserve}</MethodText>:null}</td></tr>)}</tbody></table></div>
     <h4>{T.normalization_sources_title}</h4><div className="market-monetary-sources">{Object.entries(references.monetary_sources).map(([key,value])=>{const row=value as Data;return <article key={key}><h5>{T.monetary_labels[key]}</h5><dl>{Object.entries(row).filter(([field])=>field in T.monetary_fields).map(([field,value])=><div key={field}><dt>{T.monetary_fields[field]}</dt><dd>{typeof value==='number'?n(value,4):String(value)}</dd></div>)}</dl>{row.limite&&<p>{row.limite}</p>}<MarketSourceList paths={Object.entries(row).filter(([field])=>field.startsWith('url')).map(([,value])=>String(value))} label={T.source}/></article>;})}</div>
     <p><MethodText>{T.review_scope}</MethodText></p><SourceLink path={references.review_source}>{T.review_link}</SourceLink>
    </section>;
 return <div className="market-reference-reading">
   {!references&&(error?<div role="alert"><p>{T.error}</p><button type="button" className="secondary" onClick={()=>setReload(value=>value+1)}>{T.retry}</button></div>:<p role="status">{T.loading}</p>)}
   {references&&<>
    {(!evidenceOnly||view==='services')&&<p className="market-reference-intro"><MethodText>{view==='projects'?T.project_intro:T.services_intro}</MethodText></p>}
    {!evidenceOnly&&<aside className="core-method-callout"><p><MethodText>{view==='projects'?references.transposition:references.operations_note}</MethodText></p></aside>}
    {evidenceOnly&&!selected&&<section className="prestudy-reference-summary"><h2>{view==='projects'?T.summary_projects:T.summary_services}</h2>
     {view==='projects'?<div className="core-method-table-scroll"><table className="core-method-table prestudy-reference-table"><thead><tr>{[T.project_reference,T.price_context,T.project_scope].map((label:string)=><th key={label} scope="col">{label}</th>)}</tr></thead><tbody>{references.projects.map((row:Data)=><tr key={row.id}><th scope="row"><a href={link(row)}>{row.name}</a><small>{row.platform} · {row.country}</small></th><td><strong>{interval(row.price.min,row.price.max,row.price.devise)}</strong><small>{row.price.date_prix||T.unknown} · {data.ui.reading.price_kinds[row.price.statut]}</small><small>{T.normalized} : {interval(row.normalized?.min_eur,row.normalized?.max_eur,'EUR',true)}</small></td><td><MethodText>{row.scope}</MethodText><a className="text-button" href={link(row)}>{T.details}</a></td></tr>)}</tbody></table></div>:<>
      <div className="prestudy-service-summary">{references.services.filter((row:Data)=>row.observations.length).map((row:Data)=><article key={row.id}><h3><a href={link(row)}>{row.name}</a></h3>{row.observations.map((observation:Data,index:number)=><section key={index}><h4>{observation.libelle}</h4><p><strong>{interval(observation.min,observation.max,observation.devise)}</strong> · {observation.periode}</p><p><MethodText>{observation.assiette}</MethodText></p></section>)}<a className="text-button" href={link(row)}>{T.details}</a></article>)}</div>
      <section className="prestudy-contextual"><h3>{T.contextual}</h3><ul>{references.services.filter((row:Data)=>!row.observations.length).map((row:Data)=><li key={row.id}><a href={link(row)}>{row.name}</a></li>)}</ul></section>
     </>}
     {view==='projects'&&<a className="text-button" href="#preetude-couts?view=indices">{T.normalization_link}</a>}
    </section>}
    {evidenceOnly&&selected&&<a className="text-button" href={'#preetude-projets?view='+view}>{T.back_summary}</a>}
    <div className="market-reference-list">{references[view].filter((row:Data)=>!evidenceOnly||row.id===selected?.id).map((row:Data)=><article key={row.id} aria-labelledby={'market-reference-'+row.id}>
     <header><h3 id={'market-reference-'+row.id} tabIndex={-1}>{row.name}</h3><p>{row.platform} · {row.country}</p></header>
     <dl className="market-reference-comparison"><div><dt>{T.similarities}</dt><dd><MethodText>{row.similarities}</MethodText></dd></div><div><dt>{T.differences}</dt><dd><MethodText>{row.differences}</MethodText></dd></div><div className="market-reference-takeaway"><dt>{T.lesson}</dt><dd><MethodText>{row.lesson}</MethodText></dd></div></dl>
     {view==='projects'?<>
      <h4 className="market-reference-price-heading">{T.price_details}</h4>
      <div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={row.name}><table className="core-method-table market-reference-price-table"><thead><tr><th scope="col">{T.original}</th><th scope="col">{T.normalized}</th>{!evidenceOnly&&<th scope="col">{T.transposed}</th>}</tr></thead><tbody><tr><td>{interval(row.price.min,row.price.max,row.price.devise)}</td><td>{interval(row.normalized?.min_eur,row.normalized?.max_eur,'EUR',true)}</td>{!evidenceOnly&&<td>{interval(row.transposed.cout_central_eur_2026,row.transposed.cout_central_eur_2026,'EUR',true)}</td>}</tr></tbody></table></div>
      <dl className="market-reference-context"><div><dt>{T.scope}</dt><dd><MethodText>{row.scope}</MethodText></dd></div><div><dt>{T.date}</dt><dd>{row.price.date_prix||T.unknown}</dd></div><div><dt>{T.status}</dt><dd>{data.ui.reading.price_kinds[row.price.statut]}</dd></div><div><dt>{T.included}</dt><dd><MethodText>{row.included}</MethodText></dd></div><div><dt>{T.excluded}</dt><dd><MethodText>{row.excluded}</MethodText></dd></div><div><dt>{T.evidence}</dt><dd><MethodText>{row.price_evidence}</MethodText></dd></div></dl>
      {row.price.reserve&&<p className="market-reference-limit"><strong>{T.price_reserve} : </strong><MethodText>{row.price.reserve}</MethodText></p>}
      {!evidenceOnly&&<p className="market-reference-limit"><strong>{T.limit} :</strong> <MethodText>{row.transposed.limite}</MethodText></p>}
     </>:<>
      <p className="market-reference-status">{row.status}</p><p><MethodText>{row.scope}</MethodText></p>
      {row.observations.length>0?<div className="market-service-observations">{row.observations.map((observation:Data,index:number)=><section key={index} aria-labelledby={`market-observation-${row.id}-${index}`}><h4 id={`market-observation-${row.id}-${index}`}>{observation.libelle}</h4><dl className="market-reference-context"><div><dt>{T.amount}</dt><dd className="market-reference-amount">{interval(observation.min,observation.max,observation.devise)}</dd></div><div><dt>{T.period}</dt><dd>{observation.periode}</dd></div><div><dt>{T.scope}</dt><dd><MethodText>{observation.assiette}</MethodText></dd></div><div><dt>{T.evidence}</dt><dd><MethodText>{observation.evidence}</MethodText></dd></div></dl><MarketSourceLink path={observation.source} label={T.source}>{observation.localisation}</MarketSourceLink></section>)}</div>:<p className="market-reference-limit">{T.no_observations}</p>}
     </>}
     <p className="market-reference-review">{T.review_date} : {row.review_date}</p>{evidence(row)}
    </article>)}</div>
    {(!evidenceOnly||selected)&&normalization}
    {evidenceOnly&&selected&&<a className="text-button" href={'#preetude-projets?view='+view}>{T.back_summary}</a>}
   </>}
  </div>;
}

export function MarketReferenceDrawer({view,onClose}:{view:'projects'|'services';onClose:()=>void}){
 const {data}=useStudy(),T=data.ui.essential.market_study.references;
 return <Drawer title={view==='projects'?T.project_drawer_title:T.services_drawer_title} onClose={onClose} wide><MarketReferences view={view}/></Drawer>;
}
