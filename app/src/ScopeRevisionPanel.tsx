import {useStudy,useFormat,type Data} from './context';
import './scopeRevision.css';

export function ScopeRevisionPanel({detail=false}:{detail?:boolean}){
 const {data}=useStudy(),{n}=useFormat(),R=data.content.delivery_organisation.scope_revision,L=data.ui.essential.scope_revision;
 if(!R)return null;
 const amount=(x:Data)=>n(x.jh,0)+' '+L.jh+' · '+n(x.cost_eur_ht/1000,0)+' '+L.cost;
 return <section className="scope-revision" id="scope-review" data-scope-revision={R.id}>
  <h2>{L.proposal}</h2><p>{L.proposal_note}</p>
  <h3>{L.lots_title}</h3><div className="scope-revision-impacts scope-revision-lots">{R.lots.map((lot:Data)=><article key={lot.id} data-scope-lot={lot.id}><h4>{L.lots[lot.id].title}</h4><strong>{amount(lot)}</strong><p>{L.lots[lot.id].description}</p></article>)}</div>
  <dl className="scope-revision-figures">{[[L.reference,R.reference],[L.target,R.proposed],[L.delta,R.delta]].map(([label,row])=><div key={label as string}><dt>{label}</dt><dd>{amount(row as Data)}</dd></div>)}</dl>
  <div className="scope-revision-scroll" role="region" tabIndex={0} aria-label={L.group}><table className="eco-table"><thead><tr>{[L.group,L.effort,L.cost_column].map((l:string)=><th scope="col" key={l}>{l}</th>)}</tr></thead><tbody>{R.groups.map((g:Data)=><tr key={g.id}><th scope="row">{g.label}</th><td>{n(g.jh,0)+' '+L.jh}</td><td>{n(g.cost_eur_ht/1000,0)+' '+L.cost}</td></tr>)}</tbody></table></div>
  <p><strong>{L.core_reference+' : '+amount(R.core_reference)}</strong><br/>{L.core_target+' : '+amount(R.core_proposed)}</p><p className="scope-revision-boundary">{L.proposal_period}</p>
  {!detail&&<p><a href={'#unites-travail?focus='+encodeURIComponent(R.work_unit_ref)+'&view=reference-estimate'}>{L.open_detail} →</a></p>}<h3>{L.method}</h3><ul>{R.assumptions.map((s:string)=><li key={s}>{s}</li>)}</ul>
  {detail&&<><h3>{L.replacement}</h3><p>{L.replacement_note}</p><ul>{R.prior_work.map((w:Data)=><li key={w.id}>{w.id+' · '+w.label+' · '+n(w.jh,0)+' '+L.jh+' → '+w.target_packages.join(', ')}</li>)}</ul><h3>{L.detail}</h3>{R.groups.map((g:Data)=><section className="scope-revision-packages" key={g.id}><h4>{g.label}</h4>{R.packages.filter((p:Data)=>p.group===g.id).map((p:Data)=><article key={p.id}><header><strong>{p.id+' · '+p.label}</strong><span>{n(p.jh,0)+' '+L.jh}</span></header><p>{p.deliverable}</p><p><strong>{L.acceptance+' · '}</strong>{p.acceptance}</p><ul className="work-capabilities">{p.capability_refs.map((c:string)=><li key={c}>{R.hierarchy.flatMap((d:Data)=>d.subdomains.flatMap((s:Data)=>s.capabilities)).find((x:Data)=>x.id===c)?.label||c}</li>)}</ul></article>)}</section>)}
   <h3>{L.roles}</h3><p>{L.role_note}</p>{R.groups.map((g:Data)=><div className="scope-revision-scroll" key={g.id} role="region" tabIndex={0} aria-label={g.label}><h4>{g.label}</h4><table className="eco-table"><thead><tr>{[L.role,L.jh,L.rate,L.cost_column].map((l:string)=><th key={l} scope="col">{l}</th>)}</tr></thead><tbody>{g.roles.map((r:Data)=><tr key={r.id}><th scope="row">{r.label}</th><td>{n(r.net_jh,0)}</td><td>{n(r.rate_eur_jh,0)}</td><td>{n(r.labour_eur_ht/1000,0)}</td></tr>)}</tbody></table></div>)}</>}
  <h3>{L.impacts}</h3><div className="scope-revision-impacts">{R.impacts.map((i:Data)=><article key={i.id} data-impact={i.id}><header><span>{L.phase_labels[i.phase]}</span><strong>{L.status_labels[i.status]}</strong></header><h4>{i.area}</h4><p>{i.effect}</p>{i.extra_jh!==null&&<p><strong>{n(i.extra_jh,0)+' '+L.jh+' · '+n(i.extra_eur_ht/1000,0)+' '+L.cost}</strong></p>}</article>)}</div>
  <h3>{L.unknowns}</h3><ul>{R.unknowns.map((u:Data)=><li key={u.id}>{u.label+' · '+L.pending}</li>)}</ul>
  <h3>{L.sources}</h3><ul>{R.evidence_refs.map((r:Data)=><li key={r.url}><a href={r.url} target="_blank" rel="noreferrer">{r.label}</a><p>{r.use}</p></li>)}</ul>
 </section>;
}
