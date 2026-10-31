import {useEffect,useRef,useState} from 'react';
import {useStudy,type Data} from './context';
import {SourceLink} from './components';
import {fileHref} from './transport';
import {isModelDataReference} from './documentVisibility';
import {MethodText} from './MethodDocument';
import {dossierHref} from './dossierNavigation';
import './marketComparison.css';
import {GapInstruction} from './GapInstruction';
import {BudgetReviewOverview,BudgetReviewCase,BudgetReserveRegister,BudgetReserveCase} from './BudgetSupplements';

function Evidence({ids,comparison,compact=false}:{ids:string[];comparison:Data;compact?:boolean}){
 const T=comparison.reading;
 return <div className="comparison-evidence">{ids.map(id=>{const s=comparison.sources.find((x:Data)=>x.id===id);if(!s)return null;
  const available=!isModelDataReference(s.source_ref)&&(s.source_ref.startsWith('https:')||fileHref(s.source_ref));
  return <article key={id}><h5>{available?<SourceLink path={s.source_ref}>{s.label}</SourceLink>:s.label}</h5>{!compact&&<p>{s.observation}</p>}<small>{s.location}</small></article>;
 })}{!compact&&<p className="reading-note">{T.proof_limit}</p>}</div>;
}
export function MarketComparison({comparison:C,focus}:{comparison:Data;focus?:string}){
 const {data}=useStudy(),T=C.reading;
 const [search,setSearch]=useState(''),[group,setGroup]=useState('all');
 const detail=useRef<HTMLElement>(null),previousCell=useRef('');
 const [areaId,productId]=(focus||'').split('~');
 const selected=C.rows.find((r:Data)=>r.id===areaId),product=C.products.find((p:Data)=>p.id===productId);
 const cell=selected?.cells.find((c:Data)=>c.product_ref===productId);
 const instructionGap=C.gaps.find((g:Data)=>g.id+'-detail'===focus&&g.instruction);
 const budget=C.budget_review,review=budget?.reviews.find((r:Data)=>r.gap_ref===focus),reserve=budget?.additions.find((a:Data)=>a.id===focus),register=focus==='budgets';
 const products=C.products.filter((p:Data)=>group==='all'||(group==='buy'?['microsoft','sap'].includes(p.id):!['microsoft','sap'].includes(p.id)));
 const rows=C.rows.filter((r:Data)=>(r.name+' '+r.target+' '+r.capabilities.map((c:Data)=>c.bc_ref+' '+c.name).join(' ')).toLocaleLowerCase().includes(search.toLocaleLowerCase()));
 const gaps=selected&&cell?C.gaps.filter((g:Data)=>cell.gap_refs.includes(g.id)):C.gaps;
 useEffect(()=>{if(instructionGap||review||reserve||register){detail.current?.focus({preventScroll:true});window.scrollTo(0,0);}else if(selected&&cell){previousCell.current=document.querySelector<HTMLAnchorElement>('.comparison-cell[aria-current]')?.hash||'';detail.current?.focus({preventScroll:true});detail.current?.scrollIntoView({block:'start',behavior:'auto'});}else if(previousCell.current){[...document.querySelectorAll<HTMLAnchorElement>('.comparison-cell')].find(a=>a.hash===previousCell.current)?.focus();previousCell.current='';}},[focus,Boolean(C)]);
 const href=(area:string,pid:string)=>dossierHref('etude-marche','comparison','comparison','view',area+'~'+pid);
 const qualification=(cap:string,pid:string)=>dossierHref('etude-marche','qualification','comparison','view',cap+'~'+pid);
 const unitName=(id:string)=>data.content.core_evaluation.flatMap((r:Data)=>r.units||[]).find((u:Data)=>u.id===id)?.label||id;
 if(review||reserve||register)return <section ref={detail} className="comparison-detail budget-review-page" tabIndex={-1}><a className="text-button" href="#etude-marche">{budget.reading.back}</a>{review?<BudgetReviewCase model={budget} review={review}/>:reserve?<BudgetReserveCase model={budget} reserve={reserve}/>:<BudgetReserveRegister model={budget}/>}</section>;
 if(instructionGap)return <section ref={detail} className="comparison-detail gap-instruction-page" tabIndex={-1}><a className="text-button" href="#etude-marche">{T.instruction_back}</a><GapInstruction instruction={instructionGap.instruction} reading={T} unitName={unitName}/></section>;
 return <div className="market-comparison">
  <p className="core-method-lead"><MethodText>{T.intro}</MethodText></p>
  <aside className="comparison-completeness"><h2>{T.financial}</h2><p><MethodText>{T.limits}</MethodText></p><dl><div><dt>{T.adopted}</dt><dd>{new Intl.NumberFormat('fr-FR').format(C.summary.adopted_java_spring_jh)} <small>{T.unit}</small></dd></div><div><dt>{T.extra}</dt><dd>{T.not_estimated}</dd></div></dl></aside>
  <BudgetReviewOverview model={budget}/>
  <p>{T.scope}</p><p className="comparison-context"><strong>{T.date} : </strong>{C.date} · {C.context.historical_offers}</p>
  <div className="comparison-legend">{Object.entries(T.status_labels).map(([key,label])=><span className={'comparison-status '+key} key={key}>{String(label)}</span>)}</div>
  <div className="comparison-filters"><label>{T.search}<input type="search" value={search} onChange={event=>setSearch(event.target.value)}/></label><label>{T.products}<select value={group} onChange={event=>setGroup(event.target.value)}>{['all','oss','buy'].map(key=><option key={key} value={key}>{T[key]}</option>)}</select></label><p aria-live="polite">{rows.length} {T.results}</p></div>
  {rows.length?<div className="comparison-table-scroll" tabIndex={0} role="region" aria-label={T.title}><table className="comparison-table"><caption>{T.select}</caption><thead><tr><th scope="col">{T.business_area}</th>{products.map((p:Data)=><th scope="col" key={p.id}>{p.label}</th>)}</tr></thead><tbody>{rows.map((r:Data)=><tr key={r.id} data-area={r.id}><th scope="row">{r.name}<small>{r.capabilities.map((c:Data)=>c.bc_ref).join(' · ')}</small></th>{products.map((p:Data)=>{const c=r.cells.find((x:Data)=>x.product_ref===p.id);return <td key={p.id}><a aria-label={r.name+' · '+p.label+' · '+T.select} href={href(r.id,p.id)} className="comparison-cell" aria-current={selected?.id===r.id&&product?.id===p.id?'true':undefined}><span className={'comparison-status '+c.reading_status}>{T.status_labels[c.reading_status]}</span><span>{c.summary}</span></a></td>;})}</tr>)}</tbody></table></div>:<p role="status">{T.empty}</p>}
  {selected&&cell&&product&&<section ref={detail} tabIndex={-1} className="comparison-detail" aria-labelledby="comparison-detail-title">
   <p className="comparison-selected"><span className={'comparison-status '+cell.reading_status}>{T.status_labels[cell.reading_status]}</span> · {product.label}</p><h2 id="comparison-detail-title">{selected.name}</h2>
   <h3>{T.target}</h3><p>{selected.target}</p><p><strong>{T.commercial} : </strong>{T.commercial_labels[cell.commercial_status]}</p><p className="comparison-limit">{T.coverage_unknown}</p>
   <div className="comparison-product"><h3>{T.composition}</h3><p>{product.components.join(' · ')}</p><p><strong>{T.version} : </strong>{product.version}</p></div>
   <h3>{T.needs}</h3><ul className="comparison-capabilities">{selected.capabilities.map((c:Data)=><li key={c.id}>{c.included?<a href={qualification(c.id,product.id)}>{c.bc_ref} · {c.name}</a>:<span>{c.bc_ref} · {c.name} · {T.status_labels.hors_perimetre}</span>}<ul>{c.needs.map((n:Data)=><li key={n.id}>{n.resultat}</li>)}</ul></li>)}</ul>
   <h3>{T.next}</h3><p className="comparison-scenario">{selected.next_qualification}</p><h3>{T.sources}</h3><Evidence ids={cell.evidence_refs} comparison={C}/>
   {selected.crosswalk_refs.length>0&&<><h3>{T.crosswalk}</h3><p>{T.mapping_note}</p>{C.rfi_crosswalk.filter((x:Data)=>selected.crosswalk_refs.includes(x.id)).map((x:Data)=><article className="comparison-crosswalk" key={x.id}><p><strong>{x.bc_ref} · </strong>{x.rfi_location}</p><p>{x.scope_note}</p><small>{T.unreviewed}</small></article>)}</>}
   <a className="text-button" href="#etude-marche" onClick={()=>{setGroup('all');setSearch('');}}>{T.all}</a>
  </section>}
  <section className="comparison-gaps"><h2>{T.gaps}</h2><p>{T.gaps_intro}</p>{!gaps.length&&<p>{T.no_gaps}</p>}{gaps.map((g:Data)=><article key={g.id} className="comparison-gap" id={'comparison-gap-'+g.id}><header><span>{g.id}</span><h3>{g.title}</h3></header>{<a className="text-button" href={dossierHref('etude-marche','comparison','comparison','view',g.id)}>{T.instruction_open}</a>}<div className="comparison-consequences"><div><h4>{T.make}</h4><p>{budget.reviews.find((r:Data)=>r.gap_ref===g.id)?.already_funded||g.make_consequence}</p></div><div><h4>{T.buy_consequence}</h4><p>{g.buy_consequence}</p></div></div><div className="comparison-scenario"><h4>{T.scenario}</h4><p>{g.acceptance_scenario}</p></div><p className="comparison-limit"><strong>{T.extra} : </strong>{T.not_estimated}</p>
   {g.funding_candidates.length>0&&<div className="comparison-funding"><h4>{T.funding}</h4><p>{T.funding_limit}</p><ul>{[...new Set(g.funding_candidates.map((m:Data)=>m.owner))].map(owner=><li key={String(owner)}>{unitName(String(owner))}</li>)}</ul></div>}
   <Evidence ids={g.evidence_refs} comparison={C} compact/>
  </article>)}</section>
  <section className="comparison-chain"><h2>{T.method}</h2><ol>{T.method_steps.map((s:string)=><li key={s}>{s}</li>)}</ol><p>{C.context.meaning}</p></section>
 </div>;
}
