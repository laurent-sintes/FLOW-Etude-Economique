import {useFormat,type Data} from './context';
import {SourceLink} from './components';
function jump(id:string){const el=document.getElementById(id);el?.scrollIntoView({block:'start'});el?.focus({preventScroll:true});}
export function IntegrationUnits({grid}:{grid:Data}){
 const {n,amount}=useFormat(),L=grid.labels,options=Object.keys(L.option_names);
 const measures=(p:Data)=>p.measures.map((m:Data)=>m.label+' : '+(m.unit==='EUR'?amount(m.low):n(m.low,1))+(m.low===m.high?'':' '+L.range_to+' '+(m.unit==='EUR'?amount(m.high):n(m.high,1)))+(m.unit==='EUR'?'':' '+m.unit)).join(' · ');
 const refs=(o:Data)=><ul className="integration-package-links">{o.reconciliation.package_refs.map((id:string)=><li key={id}><button type="button" className="text-button" onClick={()=>jump('integration-package-'+id)}>{grid.packages[id].label}</button></li>)}</ul>;
 return <section className="gross-integration-units"><h3>{L.title}</h3><p>{L.intro}</p>
 <div className="gross-comparison-scroll" role="region" aria-label={L.matrix} tabIndex={0}><table className="core-method-table integration-coverage-table"><thead><tr><th scope="col">{L.work}</th>{options.map(id=><th scope="col" key={id}>{L.option_names[id]}</th>)}</tr></thead><tbody>{grid.units.map((u:Data)=><tr key={u.id}><th scope="row"><button className="text-button" type="button" onClick={()=>{const el=document.getElementById('integration-unit-'+u.id) as HTMLDetailsElement|null;if(el)el.open=true;jump('integration-unit-'+u.id);}}>{u.activity_ref+' · '+u.label}</button></th>{options.map(id=>{const o=u.options[id];return <td key={id}><strong className={'integration-status status-'+o.inclusion}>{L.status_labels[o.inclusion]}</strong>{refs(o)}</td>;})}</tr>)}</tbody></table></div>
 <p>{L.shared}</p><h4>{L.remaining}</h4><div className="integration-open-options">{options.map(id=><section key={id}><h5>{L.option_names[id]}</h5><p>{L.option_findings[id]}</p></section>)}</div>
 {grid.units.map((u:Data)=><details className="gross-detail" key={u.id} id={'integration-unit-'+u.id} tabIndex={-1}><summary>{u.activity_ref+' · '+u.label}</summary>
 <p><strong>{L.delivery}</strong> : {u.deliverable}</p><p><strong>{L.counting}</strong> : {u.counting_rule}</p>
 <p>{u.quantity===null?L.quantity:n(u.quantity,0)} · {u.count_unit}</p>{u.quantity_basis&&<p>{u.quantity_basis}</p>}
 <h4>{L.acceptance}</h4><ul>{u.acceptance.map((a:string)=><li key={a}>{a}</li>)}</ul>
 <p><strong>{L.drivers}</strong> : {u.drivers}</p><p><strong>{L.boundary}</strong> : {u.boundary}</p>
 <h4>{L.options}</h4>{options.map(id=>{const o=u.options[id];return <section className="integration-option-proof" key={id}><h5>{L.option_names[id]}</h5><strong className={'integration-status status-'+o.inclusion}>{L.status_labels[o.inclusion]}</strong><p><strong>{L.covered}</strong> : {o.reconciliation.covered}</p>{refs(o)}<p><strong>{L.remaining}</strong> : {o.reconciliation.remaining}</p><p>{L.effort+' : '}{o.estimate.total_jh===null?L.unknown:n(o.estimate.total_jh,1)+' JH'}</p></section>;})}
 </details>)}
 <h4>{L.observations}</h4><p>{L.observation_note}</p>{Object.entries(grid.packages).map(([id,value])=>{const p=value as Data;return <article className="integration-package" key={id} id={'integration-package-'+id} tabIndex={-1}><h5>{L.option_names[p.option]+' · '+p.label}</h5><p><strong>{measures(p)}</strong></p><p>{p.note}</p>{p.kind==='source'?<SourceLink path={grid.sources[p.source_ref].path}>{p.location}</SourceLink>:<p>{p.location}</p>}</article>})}
 <p>{L.formula}</p></section>;
}
