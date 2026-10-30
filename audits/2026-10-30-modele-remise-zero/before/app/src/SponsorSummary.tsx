import {GlossaryText} from './GlossaryText';
import {useStudy,useFormat,type Data} from './context';
import {Disclosure,Notice,Section,SourceLink} from './components';
import {StrategyChoices,DecisionEvidence,DecisionMandate} from './SponsorDecision';

export function SponsorSummary(){
 const {data,session,setSession}=useStudy();const S=data.content.sponsor;const T=S.affichage;const {n,money,amount}=useFormat();
 const horizon=session.horizon;const setHorizon=(horizon:number)=>setSession(s=>({...s,horizon}));
 const view=S.horizons.find((h:Data)=>h.years===horizon);
 const documentTitle=(path:string)=>data.ui.documents.find((d:Data)=>d.path===path)?.title||path;
 const D=S.decision;const L=D.affichage;const calendar=S.calendar;const Q=S.lecture_rapide;
 const overview=view.rows.filter((o:Data)=>o.stack===view.make_reference||o.mode==='Buy');
 const unfinished=overview.some((o:Data)=>o.remaining>0);
 return <div className="sponsor-summary">
  <section className="sponsor-verdict sponsor-brief-interest" aria-label={Q.interet}><p className="eyebrow">{Q.interet}</p><h2><GlossaryText>{S.verdict.titre}</GlossaryText></h2><p className="sponsor-position"><GlossaryText>{S.verdict.texte}</GlossaryText></p></section>
  <Section title={Q.couts} className="sponsor-brief-costs" action={<a className="text-button" href={'#'+data.ui.simulation_workspace.pages.parameters}>{Q.simulation}<span aria-hidden="true"> →</span></a>}>
   <div className="sponsor-horizon"><div className="horizon-selector"><span>{T.horizon}</span><div role="group" aria-label={T.horizon}>{data.ui.horizons.map((y:number)=><button key={y} aria-pressed={horizon===y} className={horizon===y?'active':''} onClick={()=>setHorizon(y)}>{y}<small>{T.ans}</small></button>)}</div></div><span className="sponsor-unit">{Q.reference+' · '+data.ui.labels.money_unit}</span></div>
   <div className="sponsor-brief-options">{overview.map((o:Data)=>{
    const comparison=view.comparisons.find((c:Data)=>c.buy===o.stack);
    return <article key={o.stack} className={o.stack===view.make_reference?'is-reference':''}>
     <h3>{o.name}</h3><strong className="sponsor-brief-total">{money(o.total)}<small className="amount-unit">{data.ui.labels.money_unit}</small></strong>
     <p className="sponsor-brief-delta">{comparison?<>{Q.ecart}<b>{(comparison.delta>0?'+':comparison.delta<0?'−':'')+money(Math.abs(comparison.delta))+' '+data.ui.labels.money_unit}</b></>:Q.repere}</p>
     <dl><div><dt>{Q.service}</dt><dd>{n(o.service_years,1)}</dd></div>{unfinished&&<div><dt>{Q.reste}</dt><dd>{money(o.remaining)+' '+data.ui.labels.money_unit}</dd></div>}</dl>
    </article>;
   })}</div>
   <p className="sponsor-brief-note">{unfinished&&<>{Q.inacheve+' '}</>}{Q.calendrier}</p>
   <p className="small-prose">{Q.buy_scope+' '}<a href="#perimetres?section=buy-coverage">{Q.buy_scope_link}</a></p>
  </Section>
  <Section title={Q.go} className="sponsor-brief-go"><div className="sponsor-go-conditions">{Q.conditions.map((c:Data)=><article key={c.titre}><h3><GlossaryText>{c.titre}</GlossaryText></h3><p><GlossaryText>{c.texte}</GlossaryText></p></article>)}</div><p className="sponsor-go-decision">{Q.decision}</p></Section>
  <div className="sponsor-details-heading"><h2>{Q.details}</h2><button className="secondary" onClick={()=>window.print()}>{L.imprimer}</button></div>
  <Disclosure title={Q.couts_detail}>
   <p className="small-prose">{S.lecture_economique.portee}</p>
   <p className="small-prose">{S.lecture_economique.repere_make+' '+data.ui.labels.money_unit}</p>
   <div className="table-scroll"><table className="sponsor-cost-table"><thead><tr><th>{T.option}</th><th>{T.depenses}<small>{data.ui.labels.money_unit}</small></th><th>{T.reste}<small>{data.ui.labels.money_unit}</small></th><th>{T.service}</th><th>{T.service_complet}</th><th>{T.etat}</th></tr></thead><tbody>{view.rows.map((o:Data)=><tr key={o.stack} className={o.stack===view.make_reference?'sponsor-reference':''}><th scope="row"><strong>{o.name}</strong><small>{o.mode}{o.stack===view.make_reference?' · '+T.repere:''}</small></th><td className="strong">{amount(o.total)}</td><td>{amount(o.remaining)}</td><td>{n(o.service_start_month,0)+' '+T.mois}</td><td>{n(o.service_years,1)}</td><td><span className="sponsor-stage">{data.ui.labels[o.stage]}</span></td></tr>)}</tbody></table></div>
   <p className="sponsor-reading-note">{S.lecture_economique.durees}</p>
   <Disclosure title={L.calendrier}><p>{L.calendrier_note}</p>{calendar?<><h3 className="sponsor-comparison-title">{calendar.name}</h3><div className="table-scroll"><table className="calendar-test"><thead><tr><th>{L.scenario}</th><th>{L.build_mois}</th><th>{L.depenses}</th><th>{L.service}</th></tr></thead><tbody>{(['before','after'] as const).map(k=><tr key={k}><th scope="row">{k==='before'?L.reference:L.retard}</th><td>{n(calendar[k==='before'?'months_before':'months_after'],0)+' '+T.mois}</td><td>{money(calendar[k].totals.total)+' '+data.ui.labels.money_unit}</td><td>{n(calendar[k].service_years,2)}</td></tr>)}</tbody></table></div><p className="sponsor-reading-note">{L.delta+' : '+money(calendar.after.totals.total-calendar.before.totals.total)+' '+data.ui.labels.money_unit}</p></>:<Notice>{L.test_indisponible}</Notice>}</Disclosure>
   {view.comparisons.map((c:Data)=><p key={c.buy} className="sponsor-reading-note">{S.lecture_economique.lectures_buy[c.buy]}</p>)}
   <p className="sponsor-reading-note">{S.lecture_economique.lecture_ecart}</p><div className="source-row">{S.lecture_economique.preuves.map((s:Data)=><SourceLink key={s.path} path={s.path}>{s.titre}</SourceLink>)}</div>
   <div className="reading-next"><a href="#synvance?section=enveloppe">{data.ui.editorial.bridge_link}<span>→</span></a></div>
   <h3 className="sponsor-comparison-title">{L.financement}</h3><div className="decision-benefits">{D.financement.map((f:Data)=><article key={f.titre}><h3>{f.titre}</h3><p>{f.texte}</p></article>)}</div>
  </Disclosure>
  <Disclosure title={Q.choix_detail}><StrategyChoices/><div className="reading-next"><a href="#perimetres?section=decision">{data.ui.editorial.strategy_link}<span>→</span></a></div></Disclosure>
  <Disclosure title={Q.go_detail}><DecisionEvidence/><DecisionMandate/></Disclosure>
  <Disclosure title={T.methode}><p>{S.lecture_economique.limite}</p><div className="decision-version"><span>{L.date+' · '+D.date}</span><span>{L.version+' · '+data.model_version}</span></div><SourceLink path="source/synthese-sponsor.yaml">{documentTitle('source/synthese-sponsor.yaml')}</SourceLink>{S.dependances.map((p:string)=><SourceLink key={p} path={p}>{documentTitle(p)}</SourceLink>)}</Disclosure>
 </div>;
}
