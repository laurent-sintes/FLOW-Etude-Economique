import type {Data} from './context';
import {MethodText} from './MethodDocument';
import {SourceLink} from './components';
import {fileHref} from './transport';
import {isModelDataReference} from './documentVisibility';

const href=(id:string)=>'#etude-marche?focus='+encodeURIComponent(id);
const number=(v:number)=>new Intl.NumberFormat('fr-FR').format(v);

export function BudgetReviewOverview({model:M}:{model:Data}){
 const T=M.reading,S=M.summary;
 return <section className="budget-review-summary" aria-labelledby="budget-review-title"><h2 id="budget-review-title">{T.title}</h2><p>{T.intro}</p><dl className="budget-review-metrics"><div><dt>{T.progress}</dt><dd>{S.reviewed_gaps} / {S.identified_gaps}</dd></div><div><dt>{T.open}</dt><dd>{S.unpriced_reserves}</dd></div><div><dt>{T.total}</dt><dd>{T.unknown}</dd></div></dl><p className="reading-note">{T.progress_note}</p><nav className="budget-review-links" aria-label={T.title}>{M.reviews.map((r:Data)=><a key={r.gap_ref} href={href(r.gap_ref)}><strong>{r.gap_ref}</strong><span>{r.title}</span></a>)}</nav><a className="text-button" href={href('budgets')}>{T.register_open}</a></section>;
}

function ReserveTable({model:M,ids}:{model:Data;ids?:string[]}){
 const T=M.reading,items=M.additions.filter((a:Data)=>!ids||ids.includes(a.id));
 return <div className="comparison-table-scroll" tabIndex={0} role="region" aria-label={T.budget}><table className="budget-reserve-table"><thead><tr><th scope="col">{T.id}</th><th scope="col">{T.option}</th><th scope="col">{T.phase}</th><th scope="col">{T.status}</th><th scope="col">{T.amount}</th></tr></thead><tbody>{items.map((a:Data)=><tr key={a.id} data-reserve={a.id}><th scope="row"><a href={href(a.id)}>{a.id}</a><small>{a.title}</small></th><td>{M.option_labels[a.stack]}</td><td>{T.phases[a.phase_ref]}</td><td>{T.statuses[a.status]}</td><td>{T.unknown}</td></tr>)}</tbody></table></div>;
}

export function BudgetReserveRegister({model:M}:{model:Data}){
 const T=M.reading;
 return <article className="budget-reserve-register"><h2>{T.budget}</h2><p>{T.budget_note}</p><p className="comparison-limit"><strong>{T.none_priced}</strong></p><ReserveTable model={M}/><p>{T.amount_note}</p></article>;
}

export function BudgetReserveCase({model:M,reserve:A}:{model:Data;reserve:Data}){
 const T=M.reading;
 return <article className="budget-reserve-case" data-reserve-id={A.id}><p className="comparison-context"><code>{A.id}</code> · {M.option_labels[A.stack]} · {T.phases[A.phase_ref]}</p><h2>{A.title}</h2><p><strong>{T.statuses[A.status]}</strong></p><p>{A.residual_scope}</p><p className="comparison-limit"><strong>{T.amount} : {T.unknown}</strong></p><h3>{T.funding}</h3><ul className="budget-existing-funding">{A.existing_funding_refs.map((f:Data)=><li key={f.source_ref+f.keys.join('/')}>{f.label}</li>)}</ul><h3>{T.proof}</h3><p>{A.proof_to_price}</p><h3>{T.excluded}</h3><p>{A.excluded_scope}</p><p className="reading-note">{T.amount_note}</p><nav aria-label={T.progress}>{A.gap_refs.map((id:string)=><p key={id}><a href={href(id)}>{id} · {M.reviews.find((r:Data)=>r.gap_ref===id).title}</a></p>)}</nav><a className="text-button" href={href('budgets')}>{T.register_open}</a></article>;
}

export function BudgetReviewCase({model:M,review:R}:{model:Data;review:Data}){
 const T=M.reading;
 return <article className="budget-gap-review" data-gap={R.gap_ref}>
  <p className="comparison-context">{M.date} · {R.gap_ref}</p><h2>{R.title}</h2><p className="core-method-lead"><MethodText>{R.conclusion}</MethodText></p>
  <div className="budget-review-findings"><section><h3>{T.funding}</h3><p>{R.already_funded}</p></section><section><h3>{T.residual}</h3><p>{R.residual}</p></section></div>
  <section><h3>{T.criteria}</h3><div className="comparison-table-scroll" tabIndex={0} role="region" aria-label={T.criteria}><table className="gap-instruction-table"><thead><tr><th scope="col">{T.criterion}</th><th scope="col">{T.observation}</th><th scope="col">{T.remaining}</th></tr></thead><tbody>{R.criteria.map((c:Data)=><tr key={c.id}><th scope="row">{c.title}<small>{c.need_refs.join(' · ')}</small></th><td><p>{c.observation}</p><ul>{c.funding.map((f:Data)=><li key={f.id}>{f.label}<small>{f.owner_label}</small></li>)}</ul></td><td>{c.remaining}</td></tr>)}</tbody></table></div></section>
  <section className="budget-review-baselines"><h3>{T.baselines}</h3><p className="reading-note">{T.baseline_note}</p>{R.baselines.map((b:Data)=><article key={b.calculation_ref}><h4>{b.label}</h4><p><strong>{number(b.adopted_jh)} {T.jh}</strong> · <code>{b.calculation_ref}</code></p>{b.family_labels.length>0&&<p>{T.family} : {b.family_labels.join(' · ')}</p>}{b.allocations.length>0&&<ul>{b.allocations.map((a:Data)=><li key={a.id}>{a.label} · {number(a.jh)} {T.jh}</li>)}</ul>}{b.selected_cfp!==null&&<p>{T.existing_count} : {number(b.selected_cfp)} {T.cfp}</p>}{b.schemas.length>0&&<><h5>{T.schemas}</h5><ul>{b.schemas.map((s:Data)=><li key={s.name}><code>{s.name}</code><small>{s.fields.join(' · ')}</small></li>)}</ul></>}</article>)}</section>
  <section><h3>{T.checks}</h3><p className="reading-note">{T.checks_note}</p><ol>{R.acceptance_checks.map((s:string)=><li key={s}>{s}</li>)}</ol>{R.gap_ref==='G02'&&<a href={href('G02-detail')}>{T.experiment_link}</a>}</section>
  <section><h3>{T.products}</h3><div className="budget-product-actions">{R.product_findings.map((p:Data)=><article key={p.id}><h4>{p.label}</h4><p>{p.action}</p></article>)}</div></section>
  <section><h3>{T.integration}</h3><ul>{R.integration_activities.map((a:Data)=><li key={a.id}><code>{a.id}</code> · {a.label}</li>)}</ul><h3>{T.maintenance}</h3><ul>{R.maintenance_activities.map((a:Data)=><li key={a.id}><code>{a.id}</code> · {a.label}</li>)}</ul></section>
  <section><h3>{T.budget}</h3><p>{T.budget_note}</p><ReserveTable model={M} ids={R.addition_refs}/>{R.non_budget_treatments.map((a:Data)=><p className="reading-note" key={a.stack+a.phase_ref}>{M.option_labels[a.stack]} · {T.phases[a.phase_ref]} : {a.reason}</p>)}<p>{T.amount_note}</p></section>
  <section className="comparison-evidence"><h3>{T.source}</h3>{R.sources.map((s:Data)=>{const available=!isModelDataReference(s.source_ref)&&(s.source_ref.startsWith('https:')||fileHref(s.source_ref));return <article key={s.id}><h4>{available?<SourceLink path={s.source_ref}>{s.label}</SourceLink>:s.label}</h4><small>{s.location}</small><p>{s.observation}</p></article>;})}</section>
 </article>;
}
