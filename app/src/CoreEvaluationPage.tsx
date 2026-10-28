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
