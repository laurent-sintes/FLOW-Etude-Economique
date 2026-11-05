import {useFormat,type Data} from './context';
import {MethodText} from './MethodDocument';
import {SourceLink} from './components';
import './mdmOssAssessment.css';

function MdmEngineering({assessment:E,labels:L,jh}:{assessment:Data,labels:Data,jh:string}){
 const {n}=useFormat();
 const effort=(value:number)=>n(value,0)+' '+jh;
 const adopted=E.status==='adopted';
 const gap=E.gap_jh===0?L.equal_retained:effort(Math.abs(E.gap_jh))+' '+(adopted?L.above_previous:E.gap_jh>0?L.above_retained:L.below_retained);
 return <section className="mdm-oss-details" aria-label={L.title} data-mdm-engineering>
  <h4>{L.title}</h4><p>{E.assumption}</p>
  <div className="mdm-oss-figures">
   <div><span>{adopted?L.adopted:L.central}</span><strong data-mdm-engineering-central>{effort(E.central_jh)}</strong><small>{gap}</small></div>
   <div><span>{L.extended}</span><strong data-mdm-engineering-extended>{effort(E.extended_jh)}</strong></div>
  </div>
  <ul>{E.groups.map((group:Data)=><li key={group.id}>{group.label+' · '}<strong>{effort(group.jh)}</strong></li>)}
   <li>{L.families+' · '}<strong>{effort(E.family_jh)}</strong></li>
   <li>{L.qualification+' · '}<strong>{effort(E.qualification_jh)}</strong></li>
  </ul>
  <p>{E.decision_gate}</p>
  <details className="mdm-oss-details"><summary>{L.components}</summary><p>{E.activity_basis}</p>
   {E.groups.map((group:Data)=><section key={group.id}><h5>{group.label}</h5>
    {group.components.map((row:Data)=><details className="mdm-oss-details" key={row.id}>
     <summary>{row.label+' · '+effort(row.jh)}</summary>
     <dl className="mdm-engineering-detail">
      {['build','adapt','reuse','acceptance'].map(key=><div key={key}><dt>{L[key]}</dt><dd>{row[key]}</dd></div>)}
     </dl>
     <p>{Object.entries(row.activities).map(([key,value])=>L[key]+' · '+effort(value as number)).join(' / ')}</p>
     <ul>{row.funding.map((item:Data)=><li key={item.id}>{item.label+' · '+item.funding_owner}</li>)}</ul>
    </details>)}
   </section>)}
  </details>
  <details className="mdm-oss-details"><summary>{L.variants}</summary><ul>{E.variants.map((variant:Data)=><li key={variant.id}><strong>{variant.label+' · +'+effort(variant.jh)}</strong><p>{variant.change}</p></li>)}</ul></details>
  <details className="mdm-oss-details"><summary>{L.unknowns}</summary><ul>{E.unknowns.map((unknown:string)=><li key={unknown}>{unknown}</li>)}</ul></details>
  <p><SourceLink path={E.report_ref}>{L.proof}</SourceLink></p>
 </section>;
}

export function MdmOssAssessment({assessment:A}:{assessment?:Data}){
 const {n}=useFormat();if(!A)return null;const L=A.labels,anchor=A.products.find((p:Data)=>p.id===A.anchor);
 const review=A.unidata_review;
 const gap=anchor.gap_jh<0?L.comparison_low:anchor.gap_jh>0?L.comparison_high:L.comparison_equal;
 const sizes=(value:number)=>n(value/1000,3);
 return <section className="mdm-oss-assessment" data-mdm-oss-assessment={A.status} aria-label={L.title}>
  <header><strong className="mdm-oss-status">{L.status}</strong><h3>{L.title}</h3><p>{L.intro}</p></header>
  <div className="mdm-oss-figures"><div><span>{L.retained}</span><strong data-mdm-retained>{n(A.retained.jh,0)+' '+L.jh}</strong></div><div><span>{L.candidate}</span><strong data-mdm-anchor>{n(anchor.jh,0)+' '+L.jh}</strong><small>{anchor.label+' · '+anchor.repositories[0].date+' · '+n(Math.abs(anchor.gap_pct),0)+' % '+gap}</small></div></div>
  <p><strong>{L.unchanged}</strong></p><p><MethodText>{L.boundary}</MethodText></p>
  <MdmEngineering assessment={A.engineering} labels={L.engineering} jh={L.jh}/>
  <section className="mdm-oss-details" aria-label={L.refinement_title} data-mdm-unidata-scope>
   <h4>{L.refinement_title}</h4>
   <dl className="mdm-oss-size mdm-oss-scope-totals">
    <div><dt>{L.refinement_initial}</dt><dd>{n(review.initial.jh,0)+' '+L.jh}</dd></div>
    <div><dt>{L.refinement_selected}</dt><dd>{n(anchor.jh,0)+' '+L.jh}</dd></div>
    <div><dt>{L.refinement_removed}</dt><dd>{n(review.removed_units,0)+' '+L.logical_units}</dd></div>
   </dl>
   <ul>{review.exclusions.map((row:Data)=><li key={row.id}><strong>{row.label}</strong>{' · '+n(row.units,0)+' '+L.logical_units}<p>{row.boundary} {row.preserved}</p></li>)}</ul>
   <details className="mdm-oss-details"><summary>{L.refinement_retained}</summary>
    <ul>{review.retained.map((row:Data)=><li key={row.label}><strong>{row.label}</strong><p>{row.detail}</p></li>)}</ul>
   </details>
   <h5>{L.refinement_open}</h5>
   <ul>{review.open_questions.map((row:Data)=><li key={row.label}><strong>{row.label}</strong><p>{row.detail}</p></li>)}</ul>
   <p><SourceLink path={review.report_ref}>{L.refinement_proof}</SourceLink></p>
  </section>
  <div className="mdm-oss-results" role="region" aria-label={L.reference} tabIndex={0}>
   <table className="eco-table" role="table"><thead><tr>{[L.reference,L.size,L.effort,L.cost,L.months].map((label:string)=><th key={label} scope="col">{label}</th>)}</tr></thead><tbody>{A.products.map((p:Data)=><tr key={p.id} data-mdm-reference={p.id}><th scope="row">{p.label}</th><td data-label={L.size}>{n(p.ksloc,3)}</td><td data-label={L.effort}><strong>{n(p.jh,0)}</strong></td><td data-label={L.cost}>{n(p.cost_eur_ht/1000,0)}</td><td data-label={L.months}>{n(p.months,1)}</td></tr>)}</tbody></table>
  </div>
  <p>{L.activity_scope}</p><p>{L.candidate_note}</p>
  <details className="mdm-oss-details"><summary>{L.components}</summary><p>{L.prototype_note}</p>
   {A.products.map((p:Data)=><article key={p.id}><h4>{p.label}</h4><p>{p.scope}</p><small>{p.technology+' · '+p.license}</small>
    <dl className="mdm-oss-size"><div><dt>{L.files}</dt><dd>{n(p.file_count,0)}</dd></div><div><dt>{L.native+' · '+L.size}</dt><dd>{sizes(p.measured_units)}</dd></div><div><dt>{L.additional+' · '+L.size}</dt><dd>{sizes(p.additional_units)}</dd></div><div><dt>{L.family_count+' · '+L.size}</dt><dd>{sizes(p.family_units)}</dd></div></dl>
    <ul>{p.repositories.map((repo:Data)=><li key={repo.id}><a href={repo.url} target="_blank" rel="noreferrer">{L.frozen_source+' · '+repo.id}</a><small>{' · '+repo.commit.slice(0,12)+' · '+repo.date}</small></li>)}</ul>
    <h5>{L.sensitivity}</h5><p>{p.sensitivity.map((s:Data)=>n(s.weight,1)+' → '+n(s.jh,0)+' '+L.jh).join(' · ')}</p>
   </article>)}<p>{L.sensitivity_note}</p>
  </details>
  <details className="mdm-oss-details"><summary>{L.mapping}</summary><p>{L.evidence_note}</p><ul>{A.coverage.map((row:Data)=><li key={row.id}><strong>{row.label}</strong><small>{' · '+L.groups[row.group]+' · '+L.qualifications[row.qualification]}</small></li>)}</ul></details>
  <details className="mdm-oss-details"><summary>{L.assumptions}</summary><ul>{A.assumptions.map((s:string)=><li key={s}>{s}</li>)}</ul><h4>{L.unknowns}</h4><ul>{A.unknowns.map((s:string)=><li key={s}>{s}</li>)}</ul></details>
  <p><SourceLink path={A.report_ref}>{L.proof}</SourceLink></p>
 </section>;
}
