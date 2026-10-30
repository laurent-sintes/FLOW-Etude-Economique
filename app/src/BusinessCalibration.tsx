import {TableViewport} from './TableViewport';
import {GlossaryText} from './GlossaryText';

import {useStudy,useFormat,type Data} from './context';
import {Section,Empty,Notice,Drawer,SourceLink,SearchField} from './components';
import {capabilityReadingHref,useReadingState,matchesReadingText} from './readerNavigation';

export function BudgetComparison(){
 const {data}=useStudy();const L=data.ui.labels;const {amount,annualAmount}=useFormat();
 return <Section title={data.ui.editorial.comparison_title} description={data.ui.editorial.comparison_note}><div className="table-scroll"><table className="calibration-changes"><thead><tr><th>{L.option}</th>{[L.build,L.integration,L.annual_estimate].map((title,i)=><th key={title}>{title}<small>{i===2?L.annual_money_unit:L.money_unit}</small></th>)}</tr></thead><tbody>{data.baseline.options.map(o=><tr key={o.stack}><th>{o.name}</th><td>{amount(o.obtention)}</td><td>{amount(o.integration)}</td><td>{annualAmount(Object.values(o.annual_base).reduce((a,b)=>a+b,0)+(o.editor_prices[0]||0))}</td></tr>)}</tbody></table></div><p className="small-prose">{data.content.buy_review.presentation.budget_note+' '}<a href="#perimetres?section=buy-coverage">{data.content.buy_review.presentation.budget_link}</a></p></Section>;
}

export function BusinessCalibration(){
 const {data}=useStudy(),B=data.content.business,L=B.labels,T=L.colonnes,R=data.ui.essential.core_results;
 const options=data.baseline.options.filter(o=>o.mode==='Make'),reader=useReadingState();
 const query=reader.get('q'),selectedId=reader.get('capability');
 const selected=B.rows.find((r:Data)=>r.capacite_id===selectedId||r.id===selectedId);
 const choose=(r:Data)=>reader.set({capability:r.capacite_id||r.id},true);
 const rows=B.rows.filter((r:Data)=>matchesReadingText(query,r.name,r.path,r.scenario));
 return <>
  <Section title={L.titre} description={L.note}>
   <p><GlossaryText>{R.make_note}</GlossaryText></p><a href="#evaluation-core">{R.family_link}</a>
   <SearchField label={data.ui.reading.search_capability} value={query} onChange={q=>reader.set({q})}/>
   <TableViewport title={L.titre} className="comparison-scroll" expandable><table className="business-matrix">
    <thead><tr><th>{T.capacite}</th>{options.map(o=><th key={o.stack}>{o.name}</th>)}</tr></thead>
    <tbody>{rows.map((r:Data)=><tr key={r.id}><th><button className="row-link" onClick={()=>choose(r)}><small>{r.path.join(' / ')}</small>{r.name}<small>{r.id}</small></button></th>{options.map(o=><td key={o.stack}><button onClick={()=>choose(r)}>{r.stacks[o.stack].retained_units.length?R.no_allocation:R.pending}</button></td>)}</tr>)}</tbody>
   </table></TableViewport>{!rows.length&&<Empty/>}
  </Section>
  {selected&&<Drawer title={selected.name} onClose={()=>reader.set({capability:''},true)} wide>
   <p className="eyebrow">{selected.path.join(' / ')}</p>
   {selected.capacite_id&&<a href={capabilityReadingHref('map',selected.capacite_id,location.hash)}>{data.ui.business_map.back_to_map}</a>}
   <p><GlossaryText>{selected.scenario}</GlossaryText></p><Notice quiet><GlossaryText>{selected.frontiere}</GlossaryText></Notice>
   <div className="business-options">{options.map(o=>{const a=selected.stacks[o.stack];return <Section key={o.stack} title={o.name}>
    <p><strong>{a.retained_units.length?R.no_allocation:R.pending}</strong></p>
    {a.retained_units.length>0&&<a href="#evaluation-core">{R.family_link}</a>}
    <h4>{T.couverture}</h4><p><GlossaryText>{a.coverage.apport}</GlossaryText></p><p><GlossaryText>{a.coverage.limites}</GlossaryText></p>
    <h4>{T.reste}</h4><p><GlossaryText>{a.work.travail}</GlossaryText></p>
    {(a.proofs||[]).map((proof:Data)=><SourceLink key={proof.id} path={proof.reference}>{proof.titre}</SourceLink>)}
   </Section>;})}</div>
  </Drawer>}
 </>;
}
