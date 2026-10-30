import {useState} from 'react';
import {useStudy,type Data} from './context';
import {MethodText} from './MethodDocument';
import {MarketSourceLink,MarketSourceList} from './MarketSources';

export function MarketInstruction({reading}:{reading:Data}){
 const {data}=useStudy(),T=data.ui.essential.market_study.qualification;
 const I=reading.instruction;
 const first=I.qualifications[0];
 const [product,setProduct]=useState(first?.product_ref||I.products[0].id);
 const [capability,setCapability]=useState(first?.capability_ref||I.capabilities[0].capability_ref);
 const native=(id:string)=>data.content.complexity.rows.find((row:Data)=>row.capacite_id===id);
 const detailedCapabilities=new Set(I.qualifications.filter((row:Data)=>row.product_ref===product).map((row:Data)=>row.capability_ref));
 const chooseProduct=(value:string)=>{setProduct(value);const firstRecord=I.qualifications.find((row:Data)=>row.product_ref===value);if(firstRecord)setCapability(firstRecord.capability_ref);};
 const pair=I.rows.find((row:Data)=>row.product_ref===product&&row.capability_ref===capability);
 const detail=I.qualifications.filter((row:Data)=>row.product_ref===product&&row.capability_ref===capability);
 const current=native(capability);
 const observation=reading.product_observations[product];
 const name=(id:string)=>{const row=native(id);return row?`${row.id} · ${row.name||row.capacite?.nom}`:id;};
 const needName=(id:string)=>{const need=current?.fonctions.find((row:Data)=>row.id===id);return need?`${id} · ${need.resultat}`:id;};
 return <div className="market-qualification-reading">
  <h3>{T.title}</h3><p><MethodText>{T.intro}</MethodText></p>
  <div className="market-qualification-selectors">
   <label>{T.product}<select value={product} onChange={event=>chooseProduct(event.target.value)}>{I.products.map((row:Data)=><option key={row.id} value={row.id}>{row.label}</option>)}</select></label>
   <label>{T.capability}<select value={capability} onChange={event=>setCapability(event.target.value)}>{[true,false].map(detailed=>{const rows=I.capabilities.filter((row:Data)=>detailedCapabilities.has(row.capability_ref)===detailed);return rows.length>0&&<optgroup key={String(detailed)} label={detailed?T.analysed_capabilities:T.other_capabilities}>{rows.map((row:Data)=><option key={row.capability_ref} value={row.capability_ref}>{name(row.capability_ref)}</option>)}</optgroup>;})}</select></label>
  </div>
  <p className="market-qualification-status"><strong>{I.status_labels[pair.status]}</strong> · {T.product_date} {observation.date}</p>
  <p className="market-qualification-path">{(current?.path||current?.hierarchie?.slice(1).map((item:Data)=>item.nom))?.join(' › ')}</p>
  <div className="market-qualification-needs"><h4>{T.needs}</h4><ul>{current?.fonctions.map((need:Data)=><li key={need.id}>{need.resultat}</li>)}</ul></div>
  {detail.length>0?<div className="market-qualification-records">{detail.map((record:Data)=><article key={record.id} data-qualification={record.id}>
   <h4>{record.function_label}</h4>
   <dl className="market-reference-context">
    <div><dt>{T.classification}</dt><dd>{T.classifications[record.classification]}</dd></div>
    <div><dt>{T.status}</dt><dd>{T.statuses[record.status]}</dd></div>
    <div><dt>{T.related_needs}</dt><dd><ul>{record.need_refs.map((id:string)=><li key={id}>{needName(id)}</li>)}</ul></dd></div>
    <div><dt>{T.review}</dt><dd>{record.review?`${record.review.date} · ${record.review.reviewer} · ${T.decisions[record.review.decision]}`:T.no_review}</dd></div>
   </dl>
   <h5>{T.evidence}</h5>{record.evidence_refs.map((proof:Data,index:number)=><p className="market-qualification-proof" key={index}><MarketSourceLink path={proof.source_ref} label={T.source}>{proof.location}</MarketSourceLink></p>)}
   {record.differences.length>0&&<><h5>{T.differences}</h5><ul>{record.differences.map((text:string)=><li key={text}><MethodText>{text}</MethodText></li>)}</ul></>}
   <h5>{T.unknowns}</h5>{record.unknowns.length>0?<ul>{record.unknowns.map((text:string)=><li key={text}><MethodText>{text}</MethodText></li>)}</ul>:<p>{T.no_unknowns}</p>}
  </article>)}</div>:<p className="market-reference-limit">{T.no_detail[pair.status]}</p>}
  {pair.axis_refs.length>0&&<div className="market-qualification-axes"><h4>{T.axes_title}</h4><p>{T.axes_note}</p>{pair.axis_refs.map((id:string)=>{
   const axis=data.content.market_method.axes.find((row:Data)=>row.id===id),row=observation.observations[id];
   return <article key={id}><h5>{axis.titre}</h5><p><MethodText>{row.fonctionnalite}</MethodText></p><p><strong>{T.limit} : </strong><MethodText>{row.limite}</MethodText></p><MarketSourceList paths={row.preuves} label={T.source}/></article>;
  })}</div>}
  <p className="market-qualification-open"><strong>{T.pending} : </strong>{pair.pending_need_refs.map(needName).join(' · ')||T.none_pending}</p>
 </div>;
}
