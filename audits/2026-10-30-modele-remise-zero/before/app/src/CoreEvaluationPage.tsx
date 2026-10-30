import {useState} from 'react';
import {SourceLink} from './components';
import {useStudy,useFormat,type Data} from './context';
import {MethodText} from './MethodDocument';
import './coreEvaluation.css';

export function CoreEvaluationResults({status}:{status?:Data}){
 const {data}=useStudy(),{amount,n}=useFormat(),R=data.ui.essential.core_results;
 const rows=data.content.core_evaluation as Data[];
 const make=rows.filter(row=>row.mode==='Make'),notice=status||R.status;
 return <div className="core-evaluation-results">
   <p><MethodText>{R.make_note}</MethodText></p>
   <aside className="core-method-notice"><h3>{notice.title}</h3><p><MethodText>{notice.text}</MethodText></p></aside>
   <div className="table-scroll" tabIndex={0} role="region" aria-label={R.make_title}><table className="core-evaluation-table" data-evaluation="core"><thead><tr><th scope="col">{R.option}</th><th scope="col">{R.central}</th><th scope="col">{R.uncertainty}</th><th scope="col">{R.cost}</th></tr></thead><tbody>{make.map(row=><tr key={row.stack} data-option={row.stack}><th scope="row">{row.name}</th><td className="number">{n(row.ranges_jh.central,0)} {R.jh_unit}</td><td className="number">−{n(row.uncertainty_pct.down,1)} {R.percent_unit} / +{n(row.uncertainty_pct.up,1)} {R.percent_unit}</td><td className="number"><strong>{amount(row.build_eur_ht)}</strong></td></tr>)}</tbody></table></div>
   <p className="core-evaluation-qualification"><MethodText>{R.qualification}</MethodText></p><SourceLink path="source/recalibration-metier.yaml#methode">{R.source}</SourceLink>
   <SourceLink path="source/evaluation-core.yaml">{R.qualification_source}</SourceLink>
 </div>;
}

export function CoreEvaluationPage(){
 const {data}=useStudy(),R=data.ui.essential.core_results;
 const buy=(data.content.core_evaluation as Data[]).filter(row=>row.mode==='Buy');
 return <div className="essential-page core-evaluation-page">
  <section><h2>{R.make_title}</h2><CoreEvaluationResults/></section>
  <section className="core-method-note"><h2>{R.buy_title}</h2><p>{R.buy_note}</p><p>{buy.map(row=>row.name).join(' · ')}</p></section>
  <a className="text-button essential-structure-next" href="#comparer">{R.next} →</a>
 </div>;
}

export function CoreEvaluationTrace({options,editorial}:{options:Data[];editorial:Data}){
 const {data}=useStudy(),{n,amount}=useFormat(),L=editorial.labels,S=editorial.sections.core;
 const make=options.filter(option=>option.core),[stack,setStack]=useState(make[0].stack),[capacity,setCapacity]=useState(make[0].core.features[0].id);
 const current=make.find(option=>option.stack===stack)||make[0],core=current.core;
 const feature=core.features.find((row:Data)=>row.id===capacity)||core.features[0];
 const natureName=(key:string)=>key==='frontend'?data.ui.essential.framework.ia_frontend:data.ui.natures[key];
 return <div className="economic-trace core-work-trace" aria-labelledby="core-work-trace-title">
  <h3 id="core-work-trace-title">{S.title}</h3><p><MethodText>{S.lead}</MethodText></p>
  <label className="economic-trace-select">{L.choose_option}<select value={current.stack} onChange={event=>setStack(event.target.value)}>{make.map(option=><option key={option.stack} value={option.stack}>{option.name}</option>)}</select></label>
  <div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={S.caption}><table className="core-method-table economic-trace-table"><caption>{S.caption+' · '+current.name}</caption><thead><tr><th scope="col">{L.nature}</th><th scope="col">{L.jh_before}</th></tr></thead><tbody>{Object.entries(core.natures).map(([key,value])=><tr key={key}><th scope="row">{natureName(key)}</th><td className="core-method-number">{n(value as number,0)} {L.jh_unit}</td></tr>)}</tbody><tfoot><tr><th scope="row">{L.total}</th><td className="core-method-number">{n(core.total_jh,0)} {L.jh_unit}</td></tr></tfoot></table></div>
  <dl className="economic-value-summary"><div><dt>{L.core_work}</dt><dd>{amount(core.amounts.prestations)}</dd></div><div><dt>{L.core_coordination}</dt><dd>{amount(core.amounts.pilotage)}</dd></div><div><dt>{L.core_total}</dt><dd>{amount(core.total_eur_ht)}</dd></div></dl>
  <p><MethodText>{S.note}</MethodText></p>
  <h4>{L.capacity}</h4><p><MethodText>{S.capacity_note}</MethodText></p>
  <label className="economic-trace-select">{L.choose_capacity}<select value={feature.id} onChange={event=>setCapacity(event.target.value)}>{core.features.map((row:Data)=><option key={row.id} value={row.id}>{row.name}</option>)}</select></label>
  <article className="economic-capacity-work" aria-live="polite"><h4>{feature.name}</h4>{feature.definition&&<p>{feature.definition}</p>}<p><strong>{feature.justification}</strong></p>
   <dl className="economic-nature-values">{Object.entries(feature.charges).map(([key,value])=><div key={key}><dt>{natureName(key)}</dt><dd>{n(value as number,0)} {L.jh_unit}</dd></div>)}</dl><p className="economic-capacity-amount"><strong>{L.core_work} : {amount(feature.amount)}</strong></p>
  </article>
  <ul className="economic-reading-links">{S.links.map((link:Data)=><li key={link.href}><a className="text-button" href={link.href}>{link.label} →</a></li>)}</ul>
 </div>;
}
