import {useStudy,useFormat,type Data} from './context';
import {Section,Disclosure,SourceLink,SearchField,Empty} from './components';
import {TableViewport} from './TableViewport';
import {FundingTable} from './ComposableCosts';
import {GlossaryText} from './GlossaryText';
import {useReadingState,matchesReadingText} from './readerNavigation';

export function BuyCoverageReview(){
 const {data}=useStudy();const Q=data.content.buy_review,L=Q.presentation;const {money}=useFormat();
 return <Section title={L.titre} description={L.note}>
  <p>{Q.hypothese}</p>
  {Q.exceptions.map((e:Data)=><Disclosure key={e.id} title={e.titre} meta={e.stacks.map((s:string)=>data.glossary.options[s].libelle).join(' / ')}>
   <p><GlossaryText>{e.decision}</GlossaryText></p><p className="small-prose">{L.cout+' : '+(e.cout_initial_eur_ht===null?L.non_chiffre:money(e.cout_initial_eur_ht)+' '+data.ui.labels.money_unit)+' / '+(e.cout_annuel_eur_ht===null?L.non_chiffre:money(e.cout_annuel_eur_ht)+' '+data.ui.labels.annual_money_unit)}</p>
   <div className="source-row">{e.sources.map((id:string)=><SourceLink key={id} path={Q.sources[id].reference}>{Q.sources[id].titre}</SourceLink>)}</div>
  </Disclosure>)}
  <SourceLink path="source/qualification-buy.yaml">{L.source}</SourceLink>
 </Section>;
}

export function IntegrationEstimates(){
 const {data}=useStudy();const {amount,n}=useFormat();const L=data.ui.integration_reading,P=data.content.integration_paths,T=P.presentation,Q=data.content.buy_review.presentation,R=data.ui.estimation_reading,U=data.ui.labels;
 const options=data.baseline.options;const state=useReadingState(),query=state.get('scenario_q');
 const focus=state.get('focus','budget'),scenarioId=focus.startsWith('scenario-')?focus.slice('scenario-'.length):'';
 const selectedScenario=P.scenarios.find((row:Data)=>row.scenario===scenarioId);
 const sections=R.sections.integration,view=scenarioId?'scenarios':sections.some((item:Data)=>item.id===focus)?focus:'budget';
 const open=(next:string)=>state.set({section:'integration',focus:next},true);
 const scenarios=P.scenarios.filter((row:Data)=>matchesReadingText(query,row.source.title,row.source.situation,row.source.objective,row.names,row.paths));
 return <>
  <nav className="study-tabs" aria-label={R.navigation}>{sections.map((item:Data)=><button key={item.id} className={view===item.id?'active':''} aria-pressed={view===item.id} onClick={()=>open(item.id)}>{item.label}</button>)}</nav>
  {view==='budget'&&<div id="estimate-integration-budget" className="estimation-anchor"><Section title={L.titre} description={L.note}>
   <TableViewport title={L.titre} className="comparison-scroll"><table className="integration-matrix"><thead><tr><th>{U.option}</th>{options.map(o=><th key={o.stack}>{o.name}</th>)}</tr></thead><tbody>
    <tr><th>{L.rows.budget}<small>{U.money_unit}</small></th>{options.map(o=><td key={o.stack}><strong>{amount(o.integration)}</strong></td>)}</tr>
    <tr><th>{L.rows.duration}<small>{L.months}</small></th>{options.map(o=><td key={o.stack}>{n(o.mode==='Make'?data.baseline.make_integration_months:data.baseline.parameters.options[o.stack].integration_mois,0)}</td>)}</tr>
   </tbody></table></TableViewport>
   <p>{data.ui.pages.estimations.integration_note}</p>
   <p className="small-prose">{Q.budget_note+' '}<a href="#perimetres?section=buy-coverage">{Q.budget_link}</a></p>
  </Section></div>}
  {view==='basis'&&<div id="estimate-integration-basis" className="estimation-anchor"><Section title={L.rows.basis}>
   <div className="estimation-explanations"><article><h3>{L.make_group}</h3><p>{L.make_basis}</p></article>{options.filter(o=>o.mode==='Buy').map(o=><article key={o.stack}><h3>{o.name}</h3><p>{L.buy_basis[o.stack]}</p></article>)}</div>
   <div className="reading-next"><a href="#synvance?section=enveloppe">{data.ui.editorial.bridge_link}<span>→</span></a></div>
   <FundingTable options={options} values={o=>o.initial_responsibilities}/><h3>{L.anchor_title}</h3><p>{L.anchor_note}</p><TableViewport title={L.anchor_title}><table className="estimate-budget-table"><thead><tr><th>{U.option}</th><th>{U.investment_anchor}<small>{U.money_unit}</small></th><th>{U.integration_counterpoint}<small>{U.money_unit}</small></th></tr></thead><tbody>{options.filter(o=>o.mode==='Make').map(o=><tr key={o.stack}><th>{o.name}</th><td>{amount(o.integration)}</td><td>{data.baseline.anchor.budget_apres_bonus_eur_ht===null?L.na:amount(data.baseline.anchor.budget_apres_bonus_eur_ht)}</td></tr>)}</tbody></table></TableViewport><SourceLink path="source/plan-investissement.yaml#integration_make"/>
  </Section></div>}
  {view==='works'&&<div id="estimate-integration-works" className="estimation-anchor"><Section title={T.titre} description={T.introduction}><div className="estimation-explanations">
   {P.lots.map((lot:Data)=><article key={lot.id}><h3>{lot.titre}</h3><p>{lot.texte}</p><div className="source-row">{lot.activites.map((id:string)=><SourceLink key={id} path={'source/integration.yaml#'+id}>{id}</SourceLink>)}</div></article>)}
  </div></Section></div>}
  {view==='scenarios'&&!selectedScenario&&<div id="estimate-integration-scenarios" className="estimation-anchor"><Section title={T.scenarios} action={<SearchField label={R.search_scenario} value={query} onChange={scenario_q=>state.set({scenario_q})}/>}>
   {scenarioId&&<p role="status">{T.scenario_not_found}</p>}
   <p>{T.list_note}</p><p className="small-prose">{P.principe}</p><div className="estimation-results"><span role="status">{scenarios.length+' / '+P.scenarios.length+' · '+R.scenario_results}</span>{query&&<button className="text-button" onClick={()=>state.set({scenario_q:''})}>{data.ui.reading.reset_filters}</button>}</div>
   <ul>{scenarios.map((row:Data)=><li key={row.scenario}><button className="text-button" onClick={()=>open('scenario-'+row.scenario)}>{row.source.title}</button></li>)}</ul>
   {!scenarios.length&&<Empty/>}<SourceLink path={P.capture}>{T.source}</SourceLink>
  </Section></div>}
  {view==='scenarios'&&selectedScenario&&<div id={'estimate-integration-scenario-'+selectedScenario.scenario} className="estimation-anchor">
   <button className="text-button" onClick={()=>open('scenarios')}>{T.back_to_scenarios}</button>
   <Section title={selectedScenario.source.title} description={T.nature}>
    <p><GlossaryText>{selectedScenario.source.situation}</GlossaryText></p><p><GlossaryText>{selectedScenario.source.objective}</GlossaryText></p>
    <SourceLink path={P.capture+'#'+selectedScenario.scenario}>{T.source}</SourceLink>
    <div className="estimation-scenario-context"><div><h3>{T.capacites}</h3><ul>{selectedScenario.capacites.map((id:string,i:number)=><li key={id}><a className="source-link" href={'#perimetres?section=coverage&capability='+encodeURIComponent(id)}>{selectedScenario.names[i]}</a></li>)}</ul></div><div><h3>{T.parcours}</h3><ul>{selectedScenario.paths.map((p:Data)=><li key={p.id}>{p.title}</li>)}</ul></div></div>
    <p className="small-prose">{selectedScenario.justification}</p><p className="small-prose">{P.financement}</p>
    <SourceLink path={'source/parcours-integration.yaml#'+selectedScenario.scenario}>{T.mapping_source}</SourceLink>
   </Section>
  </div>}
 </>;
}

