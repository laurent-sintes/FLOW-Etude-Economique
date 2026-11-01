import {useFormat,type Data} from './context';
import {MethodText} from './MethodDocument';
import {SourceLink} from './components';

export function MarketPhaseSummary({summary:S,unit}:{summary:Data;unit:string}){
 const {money}=useFormat();
 const references=(items:Data[])=>items.length>0&&<ul className="market-phase-references">{items.map((ref:Data)=><li key={ref.id}><a href={ref.href} title={ref.name}>{ref.label}</a></li>)}</ul>;
 return <section className="market-phase-summary" aria-labelledby="market-phase-summary-title">
  <h2 id="market-phase-summary-title">{S.titre}</h2>
  <p className="market-phase-intro"><MethodText>{S.introduction}</MethodText></p>
  <div className="market-phase-rows">{S.phases.map((phase:Data)=><article key={phase.id} data-summary-phase={phase.id} aria-labelledby={'market-phase-'+phase.id}>
   <header><h3 id={'market-phase-'+phase.id}>{phase.titre}</h3><p className="market-phase-conclusion">{phase.conclusion}</p>{phase.groups.map((group:Data)=><div className="market-phase-range" key={group.id}><h5>{group.titre}</h5><p className="market-phase-amount">{money(group.min_eur)} – {money(group.max_eur)} <span>{unit}</span></p></div>)}</header>
   <div className="market-phase-evidence"><h4>{S.labels.appuis}</h4><p><MethodText>{phase.appui}</MethodText></p>
    {phase.groups.map((group:Data)=><div className="market-phase-range" key={group.id}><h5>{group.titre}</h5>{references(group.references)}<p className="market-phase-range-limit"><MethodText>{group.limite}</MethodText></p></div>)}
    {references(phase.references)}
    {phase.documents.map((doc:Data)=><SourceLink key={doc.path} path={doc.path}>{doc.label}</SourceLink>)}
   </div>
   <div className="market-phase-limits"><h4>{S.labels.limites}</h4><p><MethodText>{phase.limites}</MethodText></p><h4>{S.labels.suite}</h4><p><MethodText>{phase.suite}</MethodText></p></div>
  </article>)}</div>
 </section>;
}
