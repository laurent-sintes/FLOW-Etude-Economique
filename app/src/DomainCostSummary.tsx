import {useFormat,type Data} from './context';
import './domainCosts.css';

export function DomainCostSummary({reading:R}:{reading:Data}){
 const {n}=useFormat();if(!R)return null;const L=R.labels;
 return <section className="domain-cost-summary" aria-label={L.title}>
  <h3>{L.title}</h3><p>{L.intro}</p>
  <div className="domain-cost-scroll" role="region" aria-label={L.title} tabIndex={0}>
   <table className="core-method-table" role="table"><thead><tr><th scope="col">{L.domain}</th><th scope="col">{L.effort}</th><th scope="col">{L.cost}</th></tr></thead>
    <tbody>{R.buckets.map((b:Data)=><tr key={b.id} data-domain={b.id}><th scope="row">{b.label}</th><td data-label={L.effort}>{b.measures.jh.known===null?L.pending:n(b.measures.jh.known,0)}</td><td data-label={L.cost}>{b.measures.cost_eur_ht.known===null?L.pending:n(b.measures.cost_eur_ht.known/1000,0)}</td></tr>)}</tbody>
    <tfoot><tr><th scope="row">{L.total}</th><td data-label={L.effort}>{n(R.measures.jh.total,0)}</td><td data-label={L.cost}>{n(R.measures.cost_eur_ht.total/1000,0)}</td></tr></tfoot>
   </table>
  </div>
  {!R.domain_totals_complete&&<p className="domain-cost-pending"><strong>{L.known_note}</strong> {L.shared_note}</p>}
  <p className="domain-cost-phases">{L.phases_note}</p><p className="domain-cost-phases">{L.rounding_note}</p>
 </section>;
}
