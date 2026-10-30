import {ArrowUpRight} from 'lucide-react';
import {GlossaryText} from './GlossaryText';
import {useStudy,type Data} from './context';
import {Disclosure,Drawer,Empty,Notice,SearchField,Section,SourceLink} from './components';
import {capabilityReadingHref,matchesReadingText,useReadingState} from './readerNavigation';

const unique=(items:Data[])=>Array.from(new Map(items.map(item=>[item.id,item])).values());
const buyOptions=['microsoft','sap'];

function Proofs({items}:{items:Data[]}){
 const {data}=useStudy();
 return <div className="business-map-proofs">{items.map(proof=><div key={proof.id||proof.reference}>
  <SourceLink path={proof.reference}>{proof.titre||data.ui.labels.source}</SourceLink>
  {proof.portee&&<p className="small-prose"><GlossaryText>{proof.portee}</GlossaryText></p>}
 </div>)}</div>;
}

function ThemeContext({theme,onCapability}:{theme:Data;onCapability:(id:string)=>void}){
 const {data}=useStudy();const U=data.ui.business_map,L=data.ui.labels;
 const rows=data.content.business_map.rows.filter((r:Data)=>theme.capabilities.includes(r.capacite_id));
 const prose=theme.content;
 return <section className="business-theme-context">
  <h3><GlossaryText>{theme.title}</GlossaryText></h3>
  <p><GlossaryText>{theme.rationale}</GlossaryText></p>
  {theme.neighbors?.length>0&&<div className="business-theme-neighbors"><strong>{data.ui.complexity_grid.boundaries}</strong><ul>{theme.neighbors.map((node:Data)=><li key={node.id}>{node.nom}</li>)}</ul></div>}
  {!rows.length&&<p className="small-prose">{U.theme_unmapped}</p>}
  <Disclosure title={U.scope_detail}>
   <p><GlossaryText>{prose.lecture.sens}</GlossaryText></p>
   <div className="business-theme-options">{['make',...buyOptions].map(slug=><article key={slug}>
    <h4>{slug==='make'?data.glossary.notions.options_make.libelle:data.glossary.options[slug].libelle}</h4>
    <p><GlossaryText>{prose[slug]}</GlossaryText></p>
   </article>)}</div>
   {['exemple','impact','verification'].map((key,i)=><section key={key}>
    <h4>{L[['scope_example','scope_impact','scope_check'][i]]}</h4>
    <p><GlossaryText>{prose.lecture[key]}</GlossaryText></p>
   </section>)}
   <SourceLink path={prose.lecture.source||theme.source}>{L.source}</SourceLink>
  </Disclosure>
  {rows.length>0&&<div className="business-theme-links" aria-label={U.related_capabilities}>
   {rows.map((r:Data)=><button className="text-button" key={r.capacite_id} onClick={()=>onCapability(r.capacite_id)}>{r.capacite.nom}<ArrowUpRight size={13}/></button>)}
  </div>}
 </section>;
}

function BuyDetail({review,slug}:{review:Data;slug:string}){
 const {data}=useStudy();const U=data.ui.business_map;
 return <section className="business-buy-detail">
  <h3>{data.glossary.options[slug].libelle}</h3>
  <p className="business-map-status">{U.buy_statuses[review.statut]}</p>
  <h4>{U.product}</h4><p><GlossaryText>{review.coverage.apport}</GlossaryText></p>
  <h4>{U.limits}</h4><p><GlossaryText>{review.coverage.limites}</GlossaryText></p>
  <h4>{U.hypothesis}</h4><p><GlossaryText>{review.decision}</GlossaryText></p>
  <Proofs items={review.proofs||[]}/>
  {review.exceptions.length>0&&<div className="business-target-list"><h4>{U.targets}</h4>{review.exceptions.map((e:Data)=><article key={e.id}>
   <h4>{e.titre}</h4><p><GlossaryText>{e.decision}</GlossaryText></p>
   <p className="small-prose"><GlossaryText>{e.financement}</GlossaryText></p>
   <Proofs items={e.proofs||[]}/>
  </article>)}</div>}
 </section>;
}

export function CapabilityDetail({row,view,onView,onClose}:{row:Data;view:string;onView:(view:string)=>void;onClose:()=>void}){
 const {data}=useStudy();const U=data.ui.business_map,T=data.ui.complexity_grid,M=data.content.complexity.method;
 const map=data.content.business_map;const axes=Object.keys(M.axes);
 const relatedThemes=map.themes.filter((t:Data)=>row.themes.includes(t.id));
 const shared=M.mecanismes_partages.filter((m:Data)=>m.capacite_responsable===row.capacite_id||m.usages.includes(row.capacite_id));
 const families=M.familles_reemploi_a_qualifier.filter((m:Data)=>m.capacites.includes(row.capacite_id));
 const market=new Map<string,Data>();
 for(const item of row.capacite.comparaisons){
  const key=item.source_url||[item.vendor,item.product,item.element_name].join('|');
  const text=[item.similarities||item.scope_summary,item.differences,item.evidence_limits].filter(Boolean).map((s:string)=>s.replace(/\[([^\]]+)\]\([^)]+\)/g,'$1')).join(' ');
  if(!market.has(key))market.set(key,{source:item,notes:[]});
  if(!market.get(key)!.notes.includes(text))market.get(key)!.notes.push(text);
 }
 return <Drawer title={row.capacite.nom} onClose={onClose} wide>
  <p className="eyebrow">{row.hierarchie.map((h:Data)=>h.nom).join(' / ')}</p>
  <p className="scope-definition"><GlossaryText>{row.capacite.definition}</GlossaryText></p>
  <div className="business-map-views" role="group" aria-label={U.navigation}>{Object.entries(U.views).map(([key,label])=><button className={view===key?'active':''} aria-pressed={view===key} key={key} onClick={()=>onView(key)}>{String(label)}</button>)}</div>
  <h3>{T.functions}</h3><p className="small-prose">{U.proposed}</p>
  <ul className="grid-functions">{row.fonctions.map((f:Data)=><li key={f.id}><small>{f.id}</small><GlossaryText>{f.resultat}</GlossaryText></li>)}</ul>
  <h3>{T.boundaries}</h3><p><GlossaryText>{row.frontiere}</GlossaryText></p>
  <SourceLink path="source/grille-complexite.yaml">{T.grid_source}</SourceLink>
  {view==='complexity'?<>
   <h3>{T.axes}</h3>{axes.map(axis=><section className="reading-block" key={axis}>
    <h4>{M.axes[axis].titre+' · '+row.complexite[axis].niveau+'/5'}</h4>
    <p><GlossaryText>{row.complexite[axis].justification}</GlossaryText></p>
    <p className="small-prose">{M.axes[axis].niveaux[row.complexite[axis].niveau]}</p>
   </section>)}
   <p>{M.lecture.couts}</p>
   {M.qualifications_ciblees[row.capacite_id]&&<Notice>{M.qualifications_ciblees[row.capacite_id]}</Notice>}
  </>:<>
   {view==='coverage'&&<section className="business-make-detail"><h3>{data.glossary.notions.options_make.libelle}</h3><p>{U.make_note}</p>
    <Disclosure title={U.make_contributions}>{data.baseline.options.filter(o=>o.mode==='Make').map(o=>{
     const coverage=row.work.stacks[o.stack].coverage;return <section key={o.stack}>
      <h4>{o.name}</h4><p><GlossaryText>{coverage.apport}</GlossaryText></p><p className="small-prose"><GlossaryText>{coverage.limites}</GlossaryText></p>
      <Proofs items={row.work.stacks[o.stack].proofs||coverage.sources.map((id:string)=>({id,...data.content.business.sources[id]}))}/>
     </section>;
    })}</Disclosure>
   </section>}
   <div className="business-assessment-context"><h4>{U.offer}</h4><p><GlossaryText>{data.content.buy_review.presentation.offer_note||U.offer_note}</GlossaryText></p><h4>{U.financing}</h4><p><GlossaryText>{data.content.buy_review.presentation.funding_note||U.financing_note}</GlossaryText></p></div>
   <div className="business-buy-options">{buyOptions.filter(slug=>view!=='gaps'||row.buy[slug].exceptions.length>0).map(slug=><BuyDetail key={slug} slug={slug} review={row.buy[slug]}/>)}</div>
   {view==='gaps'&&buyOptions.every(slug=>row.buy[slug].exceptions.length===0)&&<p>{U.no_target}</p>}
  </>}
  <div className="reading-next"><a href={capabilityReadingHref('work',row.capacite_id,location.hash)}>{U.work_link}<span>→</span></a></div>
  <Disclosure title={T.source_scope}><p><GlossaryText>{row.capacite.perimetre}</GlossaryText></p><SourceLink path={map.source.path}>{U.map_source}</SourceLink></Disclosure>
  <Disclosure title={T.variants+' · '+row.variantes.length}>{row.variantes.length?row.variantes.map((v:Data)=><section key={v.id}><h4>{v.nom}</h4><p>{v.definition}</p><p className="small-prose">{v.perimetre}</p></section>):<p>{T.no_variants}</p>}</Disclosure>
  <Disclosure title={T.reuse}>{[...shared,...families].length?[...shared,...families].map((m:Data)=><section key={m.id}><h4>{m.titre}</h4><p>{m.contrat||m.decision}</p></section>):<p>{T.no_shared}</p>}</Disclosure>
  <Disclosure title={T.market}><p>{T.market_limit}</p>{Array.from(market.values()).map((item:Data,i:number)=><section key={i}><h4>{item.source.vendor+' · '+(item.source.source_title||item.source.element_name||item.source.product)}</h4>{item.notes.map((note:string,j:number)=><p key={j}>{note}</p>)}{item.source.source_url&&<SourceLink path={item.source.source_url}>{item.source.source_title}</SourceLink>}</section>)}</Disclosure>
  <Disclosure title={U.scenarios} meta={row.scenarios.length}><p>{U.scenarios_note}</p>{row.scenarios.length?<ul>{row.scenarios.map((s:Data)=><li key={s.id}><a href={s.route}>{s.title}</a></li>)}</ul>:<p>{U.no_scenario}</p>}</Disclosure>
  {relatedThemes.length>0&&<Disclosure title={U.boundary_links}>{relatedThemes.map((t:Data)=><section key={t.id}><h4>{t.title}</h4><p>{t.rationale}</p><a href={'#perimetres?section=coverage&theme='+encodeURIComponent(t.id)}>{U.scope_detail}</a></section>)}</Disclosure>}
 </Drawer>;
}

export function BusinessMap(){
 const {data}=useStudy();const map=data.content.business_map,U=data.ui.business_map,T=data.ui.complexity_grid,M=data.content.complexity.method;
 const reader=useReadingState();const domain=reader.get('domain'),area=reader.get('area'),query=reader.get('q'),themeId=reader.get('theme');
 const view=Object.hasOwn(U.views,reader.get('view'))?reader.get('view'):'coverage';
 const theme=map.themes.find((t:Data)=>t.id===themeId),selectedId=reader.get('capability');
 const selected=map.rows.find((r:Data)=>r.capacite_id===selectedId||r.id===selectedId);
 const domains=unique(map.rows.map((r:Data)=>r.hierarchie[1]));
 const areas=unique(map.rows.filter((r:Data)=>!domain||r.hierarchie[1].id===domain).map((r:Data)=>r.hierarchie[2]));
 const rows=map.rows.filter((r:Data)=>(!domain||r.hierarchie[1].id===domain)&&(!area||r.hierarchie[2].id===area)&&(!theme||theme.capabilities.includes(r.capacite_id))&&(view!=='gaps'||buyOptions.some(slug=>r.buy[slug].exceptions.length>0))&&matchesReadingText(query,r.capacite.nom,r.capacite_id,r.id,r.hierarchie.map((h:Data)=>h.nom),r.fonctions.map((f:Data)=>f.resultat)));
 const groups=unique(rows.map((r:Data)=>r.hierarchie[2]));const axes=Object.keys(M.axes);
 const choose=(id:string)=>reader.set({capability:id},true);
 const chooseView=(view:string)=>reader.set({view},true);
 return <>
  <Section title={U.title} description={U.intro}>
   <div className="grid-summary"><strong><GlossaryText>{map.source.domain.nom}</GlossaryText></strong><span>{domains.length+' '+T.subdomains}</span><span>{unique(map.rows.map((r:Data)=>r.hierarchie[2])).length+' '+T.areas}</span><span>{map.rows.length+' '+T.capabilities}</span></div>
   <div className="business-map-views" role="group" aria-label={U.navigation}>{Object.entries(U.views).map(([key,label])=><button key={key} className={view===key?'active':''} aria-pressed={view===key} onClick={()=>chooseView(key)}>{String(label)}</button>)}</div>
   <p className="small-prose"><GlossaryText>{U.view_notes[view]}</GlossaryText></p>
   <div className="complexity-filters business-map-filters">
    <label>{T.subdomain}<select value={domain} onChange={e=>reader.set({domain:e.target.value,area:'',capability:''})}><option value="">{T.all_subdomains}</option>{domains.map(d=><option key={d.id} value={d.id}>{d.nom}</option>)}</select></label>
    <label>{T.area}<select value={area} onChange={e=>reader.set({area:e.target.value,capability:''})}><option value="">{T.all_areas}</option>{areas.map(a=><option key={a.id} value={a.id}>{a.nom}</option>)}</select></label>
    <SearchField label={data.ui.reading.search_capability} value={query} onChange={q=>reader.set({q,capability:''})}/>
    <label>{U.theme}<select value={themeId} onChange={e=>reader.set({theme:e.target.value,domain:'',area:'',q:'',capability:''})}><option value="">{U.all_themes}</option>{map.themes.map((t:Data)=><option key={t.id} value={t.id}>{t.title}</option>)}</select></label>
    {(domain||area||query||themeId)&&<button className="text-button" onClick={()=>reader.set({domain:'',area:'',q:'',theme:'',capability:''})}>{data.ui.reading.reset_filters}</button>}
   </div>
   {theme&&<ThemeContext theme={theme} onCapability={choose}/>}
   {view==='complexity'&&<Disclosure title={T.method}><p>{M.grain}</p><p>{M.lecture.agregation}</p><div className="complexity-scale">{axes.map(axis=><section key={axis}><h3>{M.axes[axis].titre}</h3><ol>{Object.entries(M.axes[axis].niveaux).map(([level,text])=><li key={level} value={Number(level)}>{String(text)}</li>)}</ol></section>)}</div><p>{M.lecture.couts}</p><SourceLink path="source/methode-complexite.yaml"/></Disclosure>}
   <p className="small-prose" role="status">{rows.length+' / '+map.rows.length+' '+T.results}</p>
   {!rows.length&&(!theme||theme.capabilities.length>0)&&<Empty/>}
   {groups.map(group=>{const items=rows.filter((r:Data)=>r.hierarchie[2].id===group.id);return <section className="complexity-area business-map-area" key={group.id}>
    <header><p>{items[0].hierarchie[1].nom}</p><h3>{group.nom}</h3></header>
    <div className="table-scroll"><table className="business-map-table"><thead><tr><th>{U.capability}</th>{view==='complexity'?axes.map(axis=><th key={axis}>{M.axes[axis].titre}</th>):<>{view==='coverage'&&<th>{data.glossary.notions.options_make.libelle}</th>}{buyOptions.map(slug=><th key={slug}>{data.glossary.options[slug].libelle}</th>)}</>}</tr></thead><tbody>
     {items.map((r:Data)=><tr key={r.capacite_id}>
      <th scope="row"><button className="row-link" onClick={()=>choose(r.capacite_id)}><small>{r.capacite_id}</small>{r.capacite.nom}<ArrowUpRight size={14}/></button><small>{r.fonctions.length+' · '+T.functions}</small></th>
      {view==='complexity'?axes.map(axis=><td key={axis}><button className={'complexity-level level-'+r.complexite[axis].niveau} onClick={()=>choose(r.capacite_id)} aria-label={r.capacite.nom+' — '+M.axes[axis].titre+' — '+T.details}>{r.complexite[axis].niveau}</button></td>):<>
       {view==='coverage'&&<td><button className="business-map-cell" onClick={()=>choose(r.capacite_id)}>{U.make_state}</button></td>}
       {buyOptions.map(slug=><td key={slug}><button className="business-map-cell" onClick={()=>choose(r.capacite_id)}>{view==='gaps'?(r.buy[slug].exceptions.length?r.buy[slug].exceptions.map((e:Data)=>e.titre).join(' · '):U.no_target):U.buy_statuses[r.buy[slug].statut]}{view==='coverage'&&r.buy[slug].exceptions.length>0&&<small>{r.buy[slug].exceptions.map((e:Data)=>e.titre).join(' · ')}</small>}</button></td>)}
      </>}
     </tr>)}
    </tbody></table></div>
   </section>;})}
   <div className="source-row"><SourceLink path={map.source.path}>{U.map_source}</SourceLink><SourceLink path="source/grille-complexite.yaml">{T.grid_source}</SourceLink>{map.source.version&&<span className="small-prose">{U.source_version+' · '+map.source.version}</span>}</div>
  </Section>
  {selected?<CapabilityDetail row={selected} view={view} onView={chooseView} onClose={()=>reader.set({capability:''},true)}/>:selectedId&&<Notice><p>{U.invalid_capability}</p><button className="text-button" onClick={()=>reader.set({capability:''},true)}>{data.ui.labels.close}</button></Notice>}
 </>;
}
