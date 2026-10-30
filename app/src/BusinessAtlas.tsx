import {useEffect,useRef,type ReactNode} from 'react';
import {ArrowLeft,ArrowUpRight,ChevronRight,X} from 'lucide-react';
import {useStudy,useFormat,type Data} from './context';
import {Disclosure,Drawer,Empty,Notice,SearchField,SourceLink} from './components';
import {GlossaryText} from './GlossaryText';
import {CapabilityDetail} from './BusinessMap';
import {capabilityReadingHref,matchesReadingText,useReadingState} from './readerNavigation';
import './businessAtlas.css';



function WorkProof({row,metrics,onClose}:{row:Data;metrics:Data;onClose:()=>void}){
 const {data}=useStudy();
 const U=data.content.journey.atlas,R=data.ui.essential.core_results;
 return <Drawer title={row.name} onClose={onClose} wide>
  <p className="eyebrow">{row.path.join(' / ')}</p>
  <p><GlossaryText>{row.scenario}</GlossaryText></p>
  <p className="small-prose">{U.detail.raw_note}</p>
  <div className="atlas-work-proofs">{data.baseline.options.filter(o=>o.mode==='Make').map(option=>{
   const work=row.stacks[option.stack],metric=metrics[option.stack];
   return <section key={option.stack}>
    <h3>{option.name}</h3>
    <p>{metric.retained_units?.length?R.no_allocation:R.pending}</p>
    {metric.retained_units?.length>0&&<a href="#evaluation-core">{R.family_link}</a>}
    <p><GlossaryText>{work.work.travail}</GlossaryText></p>
    <div className="source-row"><SourceLink path={'source/recalibration-metier.yaml#lots/'+work.travaux_ref}>{U.detail.work_source}</SourceLink>{(work.proofs||[]).map((proof:Data)=><SourceLink key={proof.id} path={proof.reference}>{proof.titre}</SourceLink>)}</div>
   </section>;
  })}</div>
  <h3>{U.detail.boundaries}</h3><p><GlossaryText>{row.frontiere}</GlossaryText></p>
  {row.reuse?.length>0&&<><p>{U.detail.no_allocation}</p><ul>{row.reuse.map((reuse:Data)=><li key={reuse.proprietaire}>{reuse.proprietaire+' · '+reuse.contrat}</li>)}</ul></>}
  <div className="source-row"><SourceLink path="source/recalibration-metier.yaml">{U.detail.costs_source}</SourceLink><SourceLink path="source/calibration-couts.yaml">{U.detail.method_source}</SourceLink></div>
 </Drawer>;
}

/** One stable business layout; values are projections prepared by the adapter. */
export function BusinessAtlas({mode,compact=false,architecture}:{mode:'scope'|'build';compact?:boolean;architecture?:ReactNode}){
 const {data}=useStudy(),{n,amount}=useFormat(),reader=useReadingState();
 const U=data.content.journey.atlas,metrics=data.content.journey.metrics,model=metrics.map;
 const business=data.content.business_map,rows=business.rows as Data[];
 const make=data.baseline.options.filter(o=>o.mode==='Make');
 const stack=make.some(o=>o.stack===reader.get('stack'))?reader.get('stack'):make[0].stack;
 const offer=Object.hasOwn(U.offers,reader.get('offer'))?reader.get('offer'):['microsoft','sap'].includes(reader.get('stack'))?reader.get('stack'):'make';
 const axes=Object.keys(U.axes),axis=axes.includes(reader.get('axis'))?reader.get('axis'):axes[0];
 const legacyComplexity=mode==='scope'&&!compact&&reader.get('view')==='complexity';
 const metric=mode==='build'?(Object.hasOwn(U.layers,reader.get('metric'))?reader.get('metric'):reader.get('view')==='complexity'?'complexity':'jh'):legacyComplexity?'complexity':'scope';
 const query=compact?'':reader.get('q'),themeId=reader.get('theme',compact?'':'finance-conception');
 const theme=business.themes.find((t:Data)=>t.id===themeId),focus=U.focus[themeId];
 const selectedId=compact?'':reader.get('capability'),selected=rows.find(r=>r.capacite_id===selectedId||r.id===selectedId);
 const domain=compact?undefined:model.areas.find((area:Data)=>area.id===(reader.get('domain')||selected?.hierarchie[1].id));
 const area=model.business_areas.find((node:Data)=>node.id===reader.get('area')&&node.parent===domain?.id);
 const nodes=(domain?model.business_areas.filter((node:Data)=>node.parent===domain.id):model.areas) as Data[];
 const gaps=mode==='scope'&&!compact&&reader.get('view')==='gaps';
 const identity=query.trim().toLocaleLowerCase();
 const exactMatch=rows.find(row=>[row.capacite_id,row.id].some(id=>String(id).toLocaleLowerCase()===identity));
 const candidates=rows.filter(row=>(!domain||row.hierarchie[1].id===domain.id)&&(!area||row.hierarchie[2].id===area.id)&&(!gaps||(offer==='make'?['microsoft','sap']: [offer]).some(slug=>row.buy[slug].exceptions.length>0))&&(exactMatch?row===exactMatch:matchesReadingText(query,row.capacite.nom,row.capacite_id,row.id,row.hierarchie.map((h:Data)=>h.nom),row.fonctions.map((f:Data)=>f.resultat))));
 const showCapabilities=Boolean(domain||query||gaps),proof=compact?'':reader.get('atlas_proof');
 const detailRef=useRef<HTMLElement>(null);
 useEffect(()=>{
  if(!selectedId||!detailRef.current)return;
  const frame=requestAnimationFrame(()=>{detailRef.current?.focus({preventScroll:true});detailRef.current?.scrollIntoView({block:'nearest'});});
  return()=>cancelAnimationFrame(frame);
 },[selectedId]);
 const choose=(row:Data)=>reader.set({capability:row.capacite_id,domain:row.hierarchie[1].id,area:row.hierarchie[2].id,atlas_proof:''},true);
 const openProof=(id:string)=>reader.set({atlas_proof:id},true);
 const closeProof=()=>reader.set({atlas_proof:''},true);
 const nodeValue=(node:Data)=>metric==='cost'?node.stacks[stack].prestations_eur_ht:node.stacks[stack].raw_jh.central;
 const max=Math.max(1,...nodes.map(nodeValue));
 const label=(node:Data)=>{
  if(compact)return '';
  if(metric==='complexity')return node.complexity[axis].high+' / '+node.capabilities.length+' '+U.high_complexity;
  if(mode==='build')return node.stacks[stack].retained_units?.length?data.ui.essential.core_results.no_allocation:data.ui.essential.core_results.pending;
  if(offer==='make')return '';
  const count=rows.filter(row=>node.capabilities.includes(row.capacite_id)&&row.buy[offer].exceptions.length>0).length;
  return count?count+' / '+node.capabilities.length+' '+U.open_points:U.reviews;
 };
 const related=(node:Data)=>mode==='scope'&&!compact&&Boolean(theme?.capabilities.some((id:string)=>node.capabilities.includes(id)));
 const clear=()=>reader.set({domain:'',area:'',capability:'',q:'',view:'',atlas_proof:''},true);
 const proofData=U.proofs[proof];
 return <section className={'business-atlas'+(compact?' is-compact':'')}>
  {!compact&&<div className="atlas-title"><h2>{U.title}</h2><SourceLink path={business.source.path}>{U.source}</SourceLink></div>}
  {mode==='scope'&&!compact&&<>
   <div className="atlas-switches" role="group" aria-label={U.offer_label}>{Object.entries(U.offers).map(([key,text])=><button key={key} className={offer===key?'active':''} aria-pressed={offer===key} onClick={()=>reader.set({offer:key},true)}>{String(text)}</button>)}</div>
   <div className="atlas-focus-list" role="group" aria-label={U.focus_label}>{Object.entries(U.focus).map(([id,item])=><button className={themeId===id?'active':''} aria-pressed={themeId===id} key={id} onClick={()=>reader.set({theme:id},true)}>{(item as Data).label}</button>)}</div>
  </>}
   {mode==='scope'&&!compact&&theme&&<section className="atlas-insight"><h3><GlossaryText>{focus?.title||theme.title}</GlossaryText></h3><p><GlossaryText>{focus?.text||theme.rationale}</GlossaryText></p>{focus?<button className="source-link" onClick={()=>openProof(focus.proof)}>{U.proof_action}<ArrowUpRight size={13}/></button>:<SourceLink path={theme.source}>{U.proof_action}</SourceLink>}</section>}
  {mode==='build'&&<p className="atlas-note"><strong>{U.stack_label+' · '+make.find(o=>o.stack===stack)!.name}</strong></p>}{mode==='scope'&&!compact&&offer==='make'&&<p className="atlas-note">{U.target}</p>}{!compact&&<p className="atlas-note">{U.map_action}</p>}
  {mode==='build'&&<div className="atlas-switches" role="group" aria-label={U.navigation}>{Object.entries(U.layers).filter(([key])=>key!=='architecture'||architecture).map(([key,text])=><button key={key} className={metric===key?'active':''} aria-pressed={metric===key} onClick={()=>reader.set({metric:key,view:''},true)}>{String(text)}</button>)}</div>}
  {metric==='complexity'&&<div className="atlas-axis"><label>{U.axis}<select aria-label={U.axis} value={axis} onChange={event=>reader.set({axis:event.target.value},true)}>{axes.map(key=><option key={key} value={key}>{U.axes[key]}</option>)}</select></label>{legacyComplexity&&<button className="text-button" onClick={()=>reader.set({view:''},true)}>{U.return_coverage}</button>}</div>}
  {gaps&&<div className="atlas-filter-note"><p>{U.gaps_note}</p><button className="text-button" onClick={()=>reader.set({view:''},true)}>{U.return_all}</button></div>}
  {metric==='architecture'?architecture:<>
   {!compact&&<div className="atlas-search"><SearchField label={U.search} value={query} onChange={q=>reader.set({q})}/>{(query||domain||gaps)&&<button className="text-button" onClick={clear}>{U.reset}</button>}</div>}
   <div className="atlas-map">
    <header className="atlas-map-heading"><div><strong>{business.source.domain.nom}</strong><span>{domain?domain.name:model.areas.length+' '+U.subdomains+' · '+rows.length+' '+U.capabilities}</span></div>{domain&&<button className="text-button" onClick={()=>reader.set({domain:'',area:'',capability:''},true)}><ArrowLeft size={15}/>{U.all_areas}</button>}</header>
    <div className="atlas-grid">{nodes.map((node,index)=>{
     const matches=candidates.filter(row=>node.capabilities.includes(row.capacite_id)).length;
     return <button className={'atlas-node tone-'+index%3+(related(node)?' is-related':'')+(area?.id===node.id?' is-selected':'')+(query&&!matches?' is-unmatched':'')} key={node.id} onClick={()=>compact?location.hash='#perimetres?domain='+encodeURIComponent(node.id):reader.set(domain?{area:area?.id===node.id?'':node.id,capability:''}:{domain:node.id,area:'',capability:''},true)} aria-pressed={domain?area?.id===node.id:undefined}>
      <span className="atlas-node-name">{node.name}<ChevronRight size={16}/></span>
      {label(node)&&<span className={'atlas-node-value'+(mode==='build'&&metric!=='complexity'?' is-numeric':'')}>{label(node)}</span>}
      {mode==='build'&&metric!=='complexity'&&<span className="atlas-meter" aria-hidden="true"><i style={{width:nodeValue(node)/max*100+'%'}}/></span>}
      <span className="atlas-node-meta">{node.capabilities.length+' '+U.capabilities}{query&&<span>{matches+' '+U.matched}</span>}{related(node)&&<span className="atlas-related-dot" title={U.related}/>}</span>
     </button>;
    })}</div>
   </div>
   {domain&&<div className="atlas-breadcrumb"><p><GlossaryText>{domain.definition}</GlossaryText></p>{area&&<button className="text-button" onClick={()=>reader.set({area:'',capability:''},true)}><ArrowLeft size={14}/>{U.all_business_areas}</button>}</div>}
   {mode==='scope'&&!compact&&<div className="atlas-neighbors" aria-label={U.neighbors_title}>{U.neighbors.map((neighbor:Data)=><button key={neighbor.id} className={neighbor.id==='finance'&&offer==='sap'?'has-scope-difference':''} onClick={()=>openProof(neighbor.proof)}><strong>{neighbor.title}</strong><span>{neighbor.notes?.[offer]||neighbor.note}</span><ArrowUpRight size={15}/></button>)}</div>}
   {mode==='build'&&<div className="atlas-transverse"><div><strong>{U.transverse}</strong><span>{U.transverse_note}</span></div><button className="text-button" onClick={()=>openProof('transverse')}>{data.ui.essential.core_results.pending}<ArrowUpRight size={15}/></button></div>}
   {!compact&&<p className="atlas-note">{metric==='complexity'||mode==='build'?U.notes[metric]:U.scope_note}</p>}
   {query&&<p className="atlas-note">{U.filter_note}</p>}

   {showCapabilities&&<section className="atlas-capabilities"><div className="atlas-capabilities-heading"><h3>{area?.name||domain?.name||U.all_capabilities}</h3><span role="status">{candidates.length+' '+U.search_results}</span></div>{!candidates.length?<Empty/>:<div className="atlas-capability-list">{candidates.map(row=><button key={row.capacite_id} className={selected?.capacite_id===row.capacite_id?'active':''} aria-pressed={selected?.capacite_id===row.capacite_id} onClick={()=>choose(row)}><span>{row.capacite.nom}</span><small>{row.capacite_id}</small>{mode==='scope'&&offer!=='make'&&<small>{data.ui.business_map.buy_statuses[row.buy[offer].statut]}</small>}</button>)}</div>}</section>}
   {selected&&<section ref={detailRef} tabIndex={-1} className="atlas-capability-detail" id="atlas-capability">
    <header><div><p className="eyebrow">{selected.hierarchie.map((h:Data)=>h.nom).join(' / ')+' · '+selected.id}</p><h3>{selected.capacite.nom}</h3></div><button className="icon-button" aria-label={U.detail.close} onClick={()=>reader.set({capability:'',atlas_proof:''},true)}><X size={18}/></button></header>
    <p><GlossaryText>{selected.capacite.definition}</GlossaryText></p>
    {mode==='build'?<div className="atlas-capability-stacks">{make.map(option=>{const value=model.capabilities[selected.capacite_id].stacks[option.stack];return <article key={option.stack}><h4>{option.name}</h4><strong>{value.retained_units?.length?data.ui.essential.core_results.no_allocation:data.ui.essential.core_results.pending}</strong>{value.retained_units?.length>0&&<a href="#evaluation-core">{data.ui.essential.core_results.family_link}</a>}</article>;})}</div>:<div className="atlas-capability-stacks"><article><h4>{U.offers.make}</h4><strong>{data.ui.business_map.make_state}</strong></article>{['microsoft','sap'].map(slug=><article key={slug}><h4>{U.offers[slug]}</h4><strong>{data.ui.business_map.buy_statuses[selected.buy[slug].statut]}</strong></article>)}</div>}
    {metric==='complexity'&&<><h4>{U.detail.complexities}</h4><div className="atlas-complexity-facts">{axes.map(key=><article key={key}><strong>{U.axes[key]+' · '+selected.complexite[key].niveau+'/5'}</strong><span className="atlas-level" aria-hidden="true">{[1,2,3,4,5].map(level=><i key={level} className={level<=selected.complexite[key].niveau?'on':''}/>)}</span><p>{selected.complexite[key].justification}</p></article>)}</div></>}
    <p className="small-prose"><strong>{U.detail.boundaries+' · '}</strong><GlossaryText>{selected.frontiere}</GlossaryText></p>
    <div className="atlas-detail-actions"><button className="source-link" onClick={()=>openProof('capability')}>{U.detail.functions}<ArrowUpRight size={13}/></button>{mode==='build'?<><button className="source-link" onClick={()=>openProof('work')}>{U.detail.work}<ArrowUpRight size={13}/></button><a href={capabilityReadingHref('map',selected.capacite_id,location.hash)}>{data.ui.business_map.back_to_map}<ArrowUpRight size={13}/></a></>:<a href={capabilityReadingHref('work',selected.capacite_id,location.hash)}>{data.ui.business_map.work_link}<ArrowUpRight size={13}/></a>}</div>
    {selected.scenarios.length>0&&<Disclosure title={U.detail.scenarios} meta={selected.scenarios.length}><p>{data.ui.business_map.scenarios_note}</p><ul>{selected.scenarios.map((scenario:Data)=><li key={scenario.id}><a href={scenario.route}>{scenario.title}</a></li>)}</ul></Disclosure>}
   </section>}
   {selectedId&&!selected&&<Notice>{data.ui.business_map.invalid_capability}</Notice>}
   {mode==='scope'&&!compact&&<Disclosure title={U.other_themes}><div className="atlas-other-themes">{business.themes.filter((item:Data)=>!Object.hasOwn(U.focus,item.id)).map((item:Data)=><button className="text-button" key={item.id} onClick={()=>reader.set({theme:item.id},true)}>{item.title}</button>)}</div></Disclosure>}
  </>}
  {proof==='capability'&&selected&&<CapabilityDetail row={selected} view={reader.get('proof_view',metric==='complexity'?'complexity':'coverage')} onView={view=>reader.set({proof_view:view})} onClose={closeProof}/>}
  {proof==='work'&&selected&&<WorkProof row={selected.work} metrics={model.capabilities[selected.capacite_id].stacks} onClose={closeProof}/>}
  {proof==='transverse'&&<WorkProof row={business.transverse} metrics={metrics.transverse} onClose={closeProof}/>}
  {proofData&&<Drawer title={proofData.title} onClose={closeProof}>{proofData.paragraphs.map((text:string,index:number)=><p key={index}><GlossaryText>{text}</GlossaryText></p>)}<div className="atlas-proof-sources">{proofData.sources.map((source:Data)=><SourceLink key={source.path} path={source.path}>{source.label}</SourceLink>)}</div></Drawer>}
 </section>;
}
