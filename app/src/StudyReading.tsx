import {Fragment} from 'react';
import {FundingTable} from './ComposableCosts';
import {TableViewport} from './TableViewport';
import {GlossaryText} from './GlossaryText';
import {useStudy,useFormat,type Data} from './context';
import {Disclosure,Drawer,OptionTabs,Section,SourceLink} from './components';

export function ScopeDetails({row,onClose}:{row:Data;onClose:()=>void}){
 const {data}=useStudy();const L=data.ui.labels;const d=row.lecture;
 return <Drawer title={row.fonction} onClose={onClose} wide><p className="scope-definition"><GlossaryText>{d.sens}</GlossaryText></p><div className="scope-options">{data.ui.columns.scope.slice(1).map((c:Data)=><article key={c.key}><h3>{c.label||data.glossary.options[c.option].libelle}</h3><p><GlossaryText>{row[c.key]}</GlossaryText></p></article>)}</div>{[['exemple','scope_example'],['impact','scope_impact'],['verification','scope_check']].map(([key,label])=><section className="reading-block" key={key}><h3>{L[label]}</h3><p><GlossaryText>{d[key]}</GlossaryText></p></section>)}<div className="source-row"><SourceLink path={d.source}>{L.source}</SourceLink>{d.sources_produit?.map((url:string,i:number)=><SourceLink key={url} path={url}>{L.source+' '+(i+1)}</SourceLink>)}</div></Drawer>;
}

export function MarketSynthesis(){
 const {data}=useStudy();const {money}=useFormat();const market=data.content.market;
 const S=market.synthese_decision;const build=market.reperes_build_core;const ranges=market.reperes_exploratoires_marche;
 const sap=ranges.grands_programmes_sap_publics.plage_arrondie_m_eur_2026;
 const dynamics=ranges.contrepoints_dynamics;
 const cards=[{id:'sap',lo:sap.min*1e6,hi:sap.max*1e6},{id:'dynamics',lo:dynamics.minimum_eur_2026,hi:dynamics.maximum_eur_2026}];
 return <Section title={S.titre} className="market-synthesis">
  <p className="market-conclusion">{S.conclusion}</p>
  <div className="reading-block"><h3>{build.titre}</h3><p>{build.introduction}</p><div className="table-scroll"><table><thead><tr><th>{build.colonnes.composant}</th><th>{build.colonnes.taille}</th><th>{build.colonnes.portee}</th></tr></thead><tbody>{build.lignes.map((row:Data)=><tr key={row.composant}><th scope="row">{row.composant}</th><td>{row.mesure}</td><td>{row.portee}</td></tr>)}</tbody></table></div><p>{build.conclusion}</p><SourceLink path={build.source.path}>{build.source.label}</SourceLink></div>
  <div className="market-cost-lessons">{S.enseignements_postes.map((item:Data)=><article key={item.poste}><h3>{market.presentation_references.postes[item.poste]}</h3><p>{item.texte}</p></article>)}</div>
  <h3>{market.presentation_references.reperes_integration}</h3>
  <div className="market-benchmarks">{cards.map(c=><article key={c.id}>
   <h3>{S[c.id].titre}</h3><div className="market-range">{money(c.lo)+' – '+money(c.hi)}<span>{data.ui.labels.normalized_money_unit}</span></div>
   <p>{S[c.id].lecture}</p><p className="market-consequence">{S[c.id].consequence}</p>
  </article>)}</div>
  <Disclosure title={S.methode.titre}><h3>{S.cadre.titre}</h3><ol className="market-framework">{S.cadre.points.map((p:Data,i:number)=><li key={i}><h4>{p.titre}</h4><p>{p.texte}</p></li>)}</ol><p>{data.ui.reading.independence}</p><h3>{S.dispersion.titre}</h3><p>{S.dispersion.texte}</p><p className="market-formula">{S.methode.formule}</p><p>{S.methode.texte}</p></Disclosure>
  <div className="source-row">{S.preuves.map((s:Data)=><SourceLink key={s.path} path={s.path}>{s.titre}</SourceLink>)}</div>
 </Section>;
}

export function EconomicCosts(){
 const {data}=useStudy();const R=data.content.reading.economique;const {annualAmount}=useFormat();const options=data.baseline.options;
 const cell=(slug:string,id:string)=>data.content.stacks[slug].economic_reading.buckets[id];
 return <Section title={R.detail_annuel} description={R.regle} className="economic-reading">
  <FundingTable options={options} values={o=>o.annual_responsibilities} annual/>
  <TableViewport title={R.detail_annuel} className="comparison-scroll"><table className="responsibility-table annual-cost-table">
   <thead><tr><th>{R.objet}</th>{options.map(o=><th key={o.stack}>{o.name}<small>{data.ui.labels.annual_money_unit}</small></th>)}</tr></thead>
   <tbody>{R.buckets.map((b:Data)=>{
    const ids=[...new Set<string>(options.flatMap(o=>cell(o.stack,b.id).items.map((i:Data)=>i.id)))];
    return <Fragment key={b.id}><tr className="annual-responsibility-total"><th scope="row">{b.titre}<p><GlossaryText>{b.explication}</GlossaryText></p></th>{options.map(o=><td key={o.stack}><strong className="reading-amount">{cell(o.stack,b.id).total===0?<span className="reading-status">{R.zero}</span>:annualAmount(cell(o.stack,b.id).total)}</strong></td>)}</tr>
     {ids.map(id=>{const items=options.map(o=>cell(o.stack,b.id).items.find((i:Data)=>i.id===id));const names=[...new Set<string>(items.filter(Boolean).map(i=>i.nom))];return <tr className="annual-cost-item" key={id}><th scope="row">{names.join(' / ')}</th>{options.map((o,i)=><td key={o.stack}>{items[i]?<SourceLink path={items[i].source}>{annualAmount(items[i].montant)}</SourceLink>:<span title={R.zero} aria-label={R.zero}>—</span>}</td>)}</tr>;})}
    </Fragment>;
   })}<tr className="sum-row"><th scope="row">{R.total_annuel}<small>{data.ui.labels.annual_money_unit}</small></th>{options.map(o=><td key={o.stack}><strong className="reading-amount">{annualAmount(data.content.stacks[o.stack].economic_reading.total)}</strong></td>)}</tr></tbody>
  </table></TableViewport>
  <div className="section-source"><SourceLink path="source/lecture-comparative.yaml">{data.ui.labels.method}</SourceLink></div>
 </Section>;
}

export function Architecture({stack,onSelect,title}:{stack:string;onSelect?:(s:string)=>void;title?:string}){
 const {data}=useStudy();const c=data.content.stacks[stack];const R=data.content.reading.architecture;const L=data.ui.labels;
 return <Section title={title||R.titre} description={R.introduction}>{onSelect&&<OptionTabs selected={stack} onSelect={onSelect}/>}<div className="architecture-layers">{c.architecture.map((layer:Data)=><section className={'architecture-layer layer-'+layer.id} key={layer.id}><header><h3>{layer.titre}</h3><p>{layer.role}</p></header><div className="architecture-groups">{layer.groups.length===0?<p className="empty-layer">{R.empty}</p>:layer.groups.map((g:Data)=><div key={g.id}><h4>{g.titre}</h4><div className="architecture-components">{g.items.map((item:Data)=><article key={item.id}><Disclosure title={item.nom} meta={R.fondements[item.fondement]}><p>{item.description}</p>{item.facet&&<p className="facet-note">{R.facette}</p>}<dl><dt>{L.product}</dt><dd>{item.edition||item.nom}</dd><dt>{L.license}</dt><dd>{item.licence}</dd><dt>{L.price_scope}</dt><dd>{item.tarification.precision}</dd><dt>{L.limits}</dt><dd>{item.limites}</dd></dl><div className="source-row">{item.sources.map((id:string)=>c.model.sources[id]&&<SourceLink key={id} path={c.model.sources[id].reference}>{c.model.sources[id].titre||id}</SourceLink>)}</div></Disclosure></article>)}</div></div>)}</div></section>)}</div></Section>;
}

export function EconomicResponsibilities(){
 const {data}=useStudy();const R=data.content.reading.economique;const groups=[{id:'make',name:data.glossary.notions.options_make.libelle},...['sap','microsoft'].map(id=>({id,name:data.glossary.options[id].libelle}))];
 const rows=[{title:R.initial_socle.titre,values:R.initial_socle},{title:R.initial_integration.titre,values:R.initial_integration},{title:R.annuel,values:R.lecture}];
 return <Section title={R.titre} description={R.introduction}><div className="table-scroll"><table className="responsibility-prose"><thead><tr><th>{R.objet}</th>{groups.map(g=><th key={g.id}>{g.name}</th>)}</tr></thead><tbody>{rows.map(r=><tr key={r.title}><th>{r.title}</th>{groups.map(g=><td key={g.id}><GlossaryText>{r.values[g.id]}</GlossaryText></td>)}</tr>)}</tbody></table></div><div className="section-source"><SourceLink path="source/lecture-comparative.yaml"/></div></Section>;
}
