import {GlossaryText} from './GlossaryText';
import {useState} from 'react';
import {ArrowUpRight} from 'lucide-react';
import {useStudy,type Data} from './context';
import {useReadingState,matchesReadingText} from './readerNavigation';
import {Disclosure,Drawer,Empty,Notice,SearchField,Section,SourceLink} from './components';

export function ComplexityGrid(){
 const {data}=useStudy();const G=data.content.complexity;const T=data.ui.complexity_grid;const M=G.method;
 const reader=useReadingState();const domain=reader.get('domain'),area=reader.get('area'),query=reader.get('grid_q');const [selected,setSelected]=useState<Data|null>(null);
 const axes=Object.keys(M.axes);const unique=(items:Data[])=>Array.from(new Map(items.map(i=>[i.id,i])).values());
 const domains=unique(G.rows.map((r:Data)=>r.hierarchie[1]));
 const areas=unique(G.rows.filter((r:Data)=>!domain||r.hierarchie[1].id===domain).map((r:Data)=>r.hierarchie[2]));
 const rows=G.rows.filter((r:Data)=>(!domain||r.hierarchie[1].id===domain)&&(!area||r.hierarchie[2].id===area)&&matchesReadingText(query,r.capacite.nom,r.capacite.id,r.hierarchie.map((h:Data)=>h.nom),r.fonctions.map((f:Data)=>f.resultat)));
 const groups=unique(rows.map((r:Data)=>r.hierarchie[2]));
 const shared=(r:Data)=>M.mecanismes_partages.filter((m:Data)=>m.capacite_responsable===r.capacite_id||m.usages.includes(r.capacite_id));
 const families=(r:Data)=>M.familles_reemploi_a_qualifier.filter((m:Data)=>m.capacites.includes(r.capacite_id));
 const plain=(s:string)=>s?.replace(/\[([^\]]+)\]\([^)]+\)/g,'$1');
 const marketGroups=(r:Data)=>{const grouped=new Map<string,Data>();for(const c of r.capacite.comparaisons){const key=c.source_url||[c.vendor,c.product,c.element_name].join('|');if(!grouped.has(key))grouped.set(key,{source:c,notes:[]});const note=[c.similarities||c.scope_summary,c.differences,c.evidence_limits].filter(Boolean).map(plain).filter((v,i,a)=>a.indexOf(v)===i).join(' ');const group=grouped.get(key)!;if(!group.notes.includes(note))group.notes.push(note);}return Array.from(grouped.values());};
 return <>
  <Section title={M.titre} description={T.intro}>
   <div className="grid-summary"><strong><GlossaryText>{G.rows[0].hierarchie[0].nom}</GlossaryText></strong><span>{domains.length+' '+T.subdomains}</span><span>{unique(G.rows.map((r:Data)=>r.hierarchie[2])).length+' '+T.areas}</span><span>{G.rows.length+' '+T.capabilities}</span><span>{G.rows.reduce((sum:number,r:Data)=>sum+r.fonctions.length,0)+' '+T.functions}</span></div>
   <Disclosure title={T.method}><p>{M.grain}</p><p>{M.lecture.agregation}</p><div className="complexity-scale">{axes.map(axis=><section key={axis}><h3>{M.axes[axis].titre}</h3><ol>{Object.entries(M.axes[axis].niveaux).map(([level,text])=><li key={level} value={Number(level)}>{text as string}</li>)}</ol></section>)}</div><p>{M.lecture.couts}</p><SourceLink path="source/methode-complexite.yaml"/></Disclosure>
   <div className="complexity-filters"><label>{T.subdomain}<select aria-label={T.subdomain} value={domain} onChange={e=>reader.set({domain:e.target.value,area:''})}><option value="">{T.all_subdomains}</option>{domains.map(d=><option key={d.id} value={d.id}>{d.nom}</option>)}</select></label><label>{T.area}<select aria-label={T.area} value={area} onChange={e=>reader.set({area:e.target.value})}><option value="">{T.all_areas}</option>{areas.map(a=><option key={a.id} value={a.id}>{a.nom}</option>)}</select></label><SearchField label={data.ui.reading.search_capability} value={query} onChange={grid_q=>reader.set({grid_q})}/>{(domain||area||query)&&<button className="text-button" onClick={()=>reader.set({domain:'',area:'',grid_q:''})}>{data.ui.reading.reset_filters}</button>}</div>
   <p className="small-prose">{rows.length+' '+T.results+' · '+M.lecture.unite}</p>
   {!rows.length&&<Empty/>}
   {groups.map(group=>{const items=rows.filter((r:Data)=>r.hierarchie[2].id===group.id);return <section className="complexity-area" key={group.id}>
    <header><p>{items[0].hierarchie[1].nom}</p><h3>{group.nom}</h3></header>
    <div className="table-scroll"><table className="complexity-table"><thead><tr><th>{T.capability_functions}</th>{axes.map(a=><th key={a}>{M.axes[a].titre}</th>)}</tr></thead><tbody>{items.map((r:Data)=><tr key={r.id}>
     <th scope="row"><button className="row-link" onClick={()=>setSelected(r)}><small>{r.capacite.id}</small>{r.capacite.nom}<ArrowUpRight size={14}/></button><small className="complexity-function-count">{r.fonctions.length+' · '+T.functions}</small></th>
     {axes.map(a=><td key={a}><button className={'complexity-level level-'+r.complexite[a].niveau} onClick={()=>setSelected(r)} aria-label={r.capacite.nom+' — '+M.axes[a].titre+' — '+T.details}>{r.complexite[a].niveau}</button></td>)}
    </tr>)}</tbody></table></div>
   </section>;})}
   <div className="source-row"><SourceLink path="source/grille-complexite.yaml">{T.grid_source}</SourceLink><SourceLink path={G.source}>{T.map_source}</SourceLink></div>
  </Section>
  {selected&&<Drawer title={selected.capacite.nom} onClose={()=>setSelected(null)} wide>
   <p className="eyebrow"><GlossaryText>{selected.hierarchie.map((h:Data)=>h.nom).join(' / ')}</GlossaryText></p><p className="scope-definition"><GlossaryText>{selected.capacite.definition}</GlossaryText></p>
   <h3>{T.functions}</h3><ul className="grid-functions">{selected.fonctions.map((f:Data)=><li key={f.id}><small>{f.id}</small><GlossaryText>{f.resultat}</GlossaryText></li>)}</ul>
   <h3>{T.axes}</h3>{axes.map(a=><section className="reading-block" key={a}><h4>{M.axes[a].titre+' · '+selected.complexite[a].niveau+'/5'}</h4><p><GlossaryText>{selected.complexite[a].justification}</GlossaryText></p><p className="small-prose">{M.axes[a].niveaux[selected.complexite[a].niveau]}</p></section>)}
   {M.qualifications_ciblees[selected.capacite_id]&&<Notice>{M.qualifications_ciblees[selected.capacite_id]}</Notice>}
   <h3>{T.boundaries}</h3><p><GlossaryText>{selected.frontiere}</GlossaryText></p><dl className="grid-boundaries">{Object.entries(M.frontieres).map(([key,text])=><div key={key}><dt>{T.boundary_labels[key]}</dt><dd>{text as string}</dd></div>)}</dl>
   <Disclosure title={T.source_scope}><p>{selected.capacite.perimetre}</p><SourceLink path={G.source}/></Disclosure>
   <Disclosure title={T.variants+' · '+selected.variantes.length}>{selected.variantes.length?selected.variantes.map((v:Data)=><section className="reading-block" key={v.id}><h4>{v.nom}</h4><p>{v.definition}</p><p className="small-prose">{v.perimetre}</p></section>):<p>{T.no_variants}</p>}</Disclosure>
   <Disclosure title={T.reuse}>{[...shared(selected),...families(selected)].length?[...shared(selected),...families(selected)].map((m:Data)=><section className="reading-block" key={m.id}><h4>{m.titre}</h4><p>{m.contrat||m.decision}</p></section>):<p>{T.no_shared}</p>}</Disclosure>
   <Disclosure title={T.market}><p>{T.market_limit}</p>{marketGroups(selected).map((g:Data,i:number)=><section className="reading-block" key={i}><h4>{g.source.vendor+' · '+(g.source.source_title||g.source.element_name||g.source.product)}</h4><p>{g.notes[0]}</p>{g.notes.length>1&&<Disclosure title={T.market_notes}><ul>{g.notes.slice(1).map((note:string,j:number)=><li key={j}>{note}</li>)}</ul></Disclosure>}{g.source.source_url&&<SourceLink path={g.source.source_url}>{g.source.source_title}</SourceLink>}</section>)}</Disclosure>
   <Disclosure title={T.calibration}><ul>{M.qualifications_communes.map((s:string)=><li key={s}>{s}</li>)}</ul><SourceLink path="source/recalibration-metier.yaml"/></Disclosure>
   <SourceLink path="source/grille-complexite.yaml">{T.grid_source}</SourceLink>
  </Drawer>}
 </>;
}
