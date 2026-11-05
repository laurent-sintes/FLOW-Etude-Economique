import {useEffect,useRef,useState} from 'react';
import {useStudy,useFormat,type Data} from './context';
import {MdmOssAssessment} from './MdmOssAssessment';
import {ScopeRevisionPanel} from './ScopeRevisionPanel';
import {WorkEstimatePanel} from './WorkEstimatePanel';
import {TeamSelect} from './TeamTopology';
import {phaseReadingHash} from './economicNavigation';
import {useReadingContext} from './ReadingScopeContext';
import './workUnits.css';
import './domainCosts.css';
import {ArrowLeft,ArrowRight,Search} from 'lucide-react';
import {UnitScenarioPanel,ScenarioAllocationRules} from './ConsolidationViews';

function useWork(){const {data}=useStudy();const D=data.content.delivery_organisation;return {D,W:D.work_catalog,L:D.work_catalog.labels};}

export function TeamWorkScope({team,working=false}:{team:string;working?:boolean}){
 const {D,W,L}=useWork(),context=useReadingContext(),scope=W.team_scopes.find((s:Data)=>s.team_ref===team);
 const units=W.units.filter((u:Data)=>(working?D.team_consolidations.working.unit_readings.find((r:Data)=>r.work_unit_ref===u.id).team_refs.includes(team):u.contributions.some((c:Data)=>c.team_ref===team))||u.candidate_refs.includes(team));
 return <section className="work-team-scope"><h3>{L.scope_title}</h3><p>{L.scope_note}</p><strong>{scope.scope_kind==='direct'?L.direct:L.indirect}</strong><p>{scope.basis}</p>{W.domains.filter((d:Data)=>scope.capabilities.some((c:Data)=>c.domain_ref===d.id)).map((d:Data)=><section key={d.id}><h4>{d.label}</h4><ul className="work-capabilities">{scope.capabilities.filter((c:Data)=>c.domain_ref===d.id).map((c:Data)=><li key={c.id}>{c.label}</li>)}</ul></section>)}<h3>{L.units}</h3>{units.length?<ul className="work-team-units">{units.map((u:Data)=><li key={u.id}><a href={phaseReadingHash({...context,page:'unites-travail',view:working?'working':'reference',focus:u.id})!}>{u.label}</a><small>{D.phases.find((p:Data)=>p.id===u.phase_ref).label}{!(working?D.team_consolidations.working.unit_readings.find((r:Data)=>r.work_unit_ref===u.id).team_refs.includes(team):u.contributions.some((c:Data)=>c.team_ref===team))&&' · '+L.candidates}</small></li>)}</ul>:<p>{L.no_units}</p>}<p className="delivery-note">{L.candidate_note}</p></section>;
}

type WorkTab='overview'|'estimate'|'teams'|'sources';
export function WorkUnitsPage({view,focus}:{view?:string;focus?:string}){
 const {D,W,L}=useWork(),{data}=useStudy(),{n}=useFormat(),context=useReadingContext(),C=D.team_consolidations,P=W.estimate_labels.work_page;
 const [query,setQuery]=useState(''),[team,setTeam]=useState(''),[phase,setPhase]=useState(''),[onlyMissing,setOnlyMissing]=useState(false);
 const working=view?.includes('working')||false,abaque=view==='abaque'||view==='abaque-working';
 const tab:WorkTab=(['estimate','teams','sources'] as WorkTab[]).find(t=>view?.endsWith('-'+t))||'overview';
 const domainKey=(u:Data)=>u.domain_classification.status==='direct'?u.domain_classification.domain_refs[0]:'unallocated';
 const domainLabel=(u:Data)=>domainKey(u)==='unallocated'?W.domain_labels[u.domain_classification.status]:W.domains.find((d:Data)=>d.id===domainKey(u)).label;
 const selected=W.units.find((u:Data)=>u.id===focus);
 const reading=(u:Data)=>C.working.unit_readings.find((r:Data)=>r.work_unit_ref===u.id);
 const actors=(u:Data)=>working?(reading(u).status==='pending'?reading(u).team_refs:reading(u).team_contributions.map((c:Data)=>c.team_ref)):u.contributions.map((c:Data)=>c.team_ref);
 const gaps=(u:Data):string[]=>working?reading(u).missing:u.estimation.missing;
 const gapLabel=(key:string)=>working?C.labels.missing[key]:W.estimate_labels.missing_labels[key];
 const name=(id:string|null)=>id===null?P.team_pending:id==='governance'?L.governance:D.teams.find((t:Data)=>t.id===id)?.label||id;
 const scope=(u:Data)=>working&&reading(u).selection.estimate_source==='proposal'?{...u.estimation.scope,deliverable:u.estimation.proposal.inputs.deliverable||u.estimation.scope.deliverable,acceptance:u.estimation.proposal.inputs.acceptance||u.estimation.scope.acceptance}:u.estimation.scope;
 const charge=(u:Data)=>working?reading(u).net_jh:u.totals.jh;
 const cost=(u:Data)=>working?reading(u).cost_eur_ht:u.totals.cost_eur_ht;
 const noEffort=(u:Data)=>working&&(reading(u).selection.work_kind==='expense'||['excluded','included'].includes(reading(u).status)||reading(u).selection.estimate_source==='proposal'&&u.estimation.proposal.result.human_applicable===false);
 const amount=(value:number|null,isCost=false,annual=false)=>value===null?P.pending:n(isCost?value/1000:value,isCost?0:1)+' '+(isCost?L.cost:L.jh)+(annual?' '+P.per_year:'');
 const status=(u:Data)=>working?C.labels.unit_states[reading(u).status]:cost(u)!==null||charge(u)!==null?(gaps(u).length?P.reference_more:P.reference_available):P.not_priced;
 const displayView=(isWorking=working,detail:WorkTab=tab)=>((isWorking?'working':'reference')+(detail==='overview'?'':'-'+detail));
 const href=(id?:string,detail:WorkTab='overview')=>phaseReadingHash({...context,page:'unites-travail',view:id?displayView(working,detail):working?'working':'reference',focus:id})!;
 const rulesHref=phaseReadingHash({...context,page:'unites-travail',view:working?'abaque-working':'abaque'})!;
 const normal=(text:string)=>text.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase();
 const matching=W.units.filter((u:Data)=>(!team||actors(u).includes(team)||u.candidate_refs.includes(team))&&(!onlyMissing||gaps(u).length>0)&&normal([u.label,u.id,L.nature_labels[u.nature],...u.capabilities.map((c:Data)=>c.label)].join(' ')).includes(normal(query)));
 const rows=matching.filter((u:Data)=>!phase||phase===u.phase_ref);
 const pageRef=useRef<HTMLDivElement>(null),titleRef=useRef<HTMLHeadingElement>(null),returnFocus=useRef<string|null>(null);
 useEffect(()=>{
  const frame=requestAnimationFrame(()=>{
   if(selected&&!abaque){returnFocus.current=selected.id;titleRef.current?.focus();}
   else if(!abaque&&returnFocus.current){
    const link=Array.from(pageRef.current?.querySelectorAll<HTMLAnchorElement>('.work-unit-link')||[]).find(a=>a.dataset.unit===returnFocus.current);
    link?.focus();returnFocus.current=null;
   }
  });
  return()=>cancelAnimationFrame(frame);
 },[selected?.id,abaque,tab]);
 const readingControl=<label className="work-reading-select"><span>{P.reading}</span><select value={working?'working':'reference'} onChange={event=>{const active=event.target.value==='working';location.hash=phaseReadingHash({...context,page:'unites-travail',focus:selected?.id,view:abaque?(active?'abaque-working':'abaque'):selected?displayView(active):active?'working':'reference'})!;}}><option value="reference">{P.reference}</option><option value="working">{P.working}</option></select></label>;
 const contributionRows=selected?(working?reading(selected).team_contributions:selected.contributions):[];
 return <div ref={pageRef} className="essential-page delivery-page work-page work-redesign">
  {!selected&&!abaque?<>
   <div className="work-purpose"><p>{P.purpose}</p><span>{P.scope_note}</span></div>
   {focus&&<p role="status" className="delivery-note">{P.invalid_focus}</p>}
   <section className="work-phase-picker" aria-label={P.choose_phase}><div className="work-section-heading"><h2>{P.choose_phase}</h2><button type="button" className="text-button" aria-pressed={!phase} onClick={()=>setPhase('')}>{P.all_phases}</button></div><div className="work-phase-options">{D.phases.map((p:Data)=><button type="button" key={p.id} data-phase-choice={p.id} aria-pressed={phase===p.id} onClick={()=>setPhase(p.id)}><strong>{P.phase_labels[p.id]}</strong><span>{P.phase_notes[p.id]}</span><small>{n(matching.filter((u:Data)=>u.phase_ref===p.id).length,0)+' '+P.work_count}<ArrowRight size={17} aria-hidden="true"/></small></button>)}</div></section>
   <div className="work-search-row"><label className="work-search"><span>{P.search}</span><span className="work-search-control"><Search size={19} aria-hidden="true"/><input type="search" value={query} placeholder={P.search_placeholder} onChange={e=>setQuery(e.target.value)}/></span></label><TeamSelect value={team} onChange={setTeam}/></div>
   <div className="work-list-controls"><label className="work-missing-toggle"><input type="checkbox" checked={onlyMissing} onChange={e=>setOnlyMissing(e.target.checked)}/>{P.only_missing}</label>{readingControl}<a className="work-rules-link" href={rulesHref}>{P.rules_link}</a></div>
   <div className="work-list-heading"><strong>{n(rows.length,0)+' '+P.result_count}</strong><span>{P.reading_notes[working?'working':'reference']}</span></div>
   <section className="work-catalog" aria-label={P.grouped_list}>{D.phases.flatMap((p:Data)=>[...W.domains,{id:'unallocated',label:W.domain_labels.unallocated}].filter((d:Data)=>rows.some((u:Data)=>u.phase_ref===p.id&&domainKey(u)===d.id)).map((d:Data)=><section className="work-phase-group" key={p.id+'/'+d.id} data-domain-group={d.id}><h2>{P.phase_labels[p.id]+' · '+d.label}<span>{n(rows.filter((u:Data)=>u.phase_ref===p.id&&domainKey(u)===d.id).length,0)+' '+P.work_count}</span></h2><ul className="work-item-list">{rows.filter((u:Data)=>u.phase_ref===p.id&&domainKey(u)===d.id).map((u:Data)=><li key={u.id}><a className="work-unit-link" data-unit={u.id} href={href(u.id)} aria-label={P.open+' · '+u.label}><span className="work-item-main"><strong>{u.label}</strong><small>{L.nature_labels[u.nature]}</small><span className="work-item-status" data-has-gaps={gaps(u).length>0}>{status(u)}</span></span><span className="work-item-team">{actors(u).length?actors(u).map((id:string|null)=><span key={id??'unallocated'}>{name(id)}</span>):P.team_pending}{team&&u.candidate_refs.includes(team)&&!actors(u).includes(team)&&<small className="work-item-status">{L.candidates+' · '+name(team)}</small>}</span><span className="work-item-figures"><span>{noEffort(u)?P.without_effort:amount(charge(u),false,u.recurrence==='annual')}</span><strong>{working&&['excluded','included'].includes(reading(u).status)?C.labels.unit_states[reading(u).status]:amount(cost(u),true,u.recurrence==='annual')}</strong></span><span className="work-item-open">{P.open}<ArrowRight size={18} aria-hidden="true"/></span></a></li>)}</ul></section>))}</section>
   {!rows.length&&<section className="work-empty"><p>{P.empty}</p><button className="secondary" onClick={()=>{setQuery('');setTeam('');setPhase('');setOnlyMissing(false);}}>{P.reset}</button></section>}
   <p className="work-consultation"><strong>{P.consultation}</strong>{' · '+P.consultation_note}</p>
  </>:abaque?<>
   <div className="work-detail-navigation"><a href={href()}><ArrowLeft size={18} aria-hidden="true"/>{P.back}</a>{readingControl}</div>
   <section className="work-abaque"><h2>{P.rules_title}</h2><p>{P.rules_intro}</p><div className="delivery-table-scroll" role="region" tabIndex={0} aria-label={P.rules_title}><table className="eco-table"><thead><tr>{[L.rule,L.condition,L.share,L.basis].map((t:string)=><th key={t} scope="col">{t}</th>)}</tr></thead><tbody>{W.abaque.rules.map((r:Data)=><tr key={r.id}><th scope="row">{r.label}</th><td>{r.condition}</td><td>{n(r.share_pct,0)} %</td><td>{r.basis}</td></tr>)}</tbody></table></div>
   <h3>{L.overrides}</h3>{W.abaque.overrides.length?<ul>{W.abaque.overrides.map((r:Data)=><li key={r.id}><a href={href(r.work_unit_ref,'teams')}>{W.units.find((u:Data)=>u.id===r.work_unit_ref).label}</a><p>{r.basis}</p><ul>{r.shares.map((s:Data)=><li key={s.team_ref}>{name(s.team_ref)+' · '+n(s.share_pct,1)+' % · '+L.contribution_labels[s.contribution_kind]}</li>)}</ul></li>)}</ul>:<p>{L.no_overrides}</p>}{working&&<ScenarioAllocationRules/>}<p className="delivery-note">{L.candidate_note}</p></section>
  </>:selected&&<>
   <div className="work-detail-navigation"><a href={href()}><ArrowLeft size={18} aria-hidden="true"/>{P.back}</a>{readingControl}</div>
   <article className="work-detail" data-work-detail={selected.id}><header className="work-detail-header"><p>{P.phase_labels[selected.phase_ref]}{' · '+(selected.recurrence==='annual'?L.annual:L.initial)}</p><h2 ref={titleRef} tabIndex={-1}>{selected.label}</h2><span className="work-item-status" data-has-gaps={gaps(selected).length>0}>{status(selected)}</span></header>
    <dl className="work-key-figures"><div><dt>{working?P.charge_working:P.charge_reference}</dt><dd>{noEffort(selected)?P.without_effort:amount(charge(selected),false,selected.recurrence==='annual')}</dd></div><div><dt>{P.cost}</dt><dd>{working&&['excluded','included'].includes(reading(selected).status)?C.labels.unit_states[reading(selected).status]:amount(cost(selected),true,selected.recurrence==='annual')}</dd></div><div><dt>{L.team}</dt><dd>{actors(selected).length?actors(selected).map(name).join(', '):P.team_pending}</dd></div></dl>
    <nav className="work-detail-tabs" aria-label={P.tabs_label}>{(['overview','estimate','teams','sources'] as WorkTab[]).map(t=><a key={t} href={href(selected.id,t)} aria-current={tab===t?'page':undefined}>{P.tabs[t]}</a>)}</nav>
    <div className="work-detail-content">
     {tab==='overview'&&<section className="work-overview"><h3>{P.result}</h3>{scope(selected).deliverable?.includes(' · ')?<ul className="work-outcomes">{scope(selected).deliverable.split(' · ').map((text:string,i:number)=><li key={i}>{text}</li>)}</ul>:<p>{scope(selected).deliverable||P.result_pending}</p>}
      {selected.included_activities.length>0&&<section className="work-included-activities"><h3>{P.included_activities}</h3><ul>{selected.included_activities.map((text:string,i:number)=><li key={i}>{text}</li>)}</ul></section>}
      <section className="work-gaps"><h3>{P.gaps}</h3>{gaps(selected).length?<><p>{P.gaps_note}</p><ul>{gaps(selected).map((key:string)=><li key={key}>{gapLabel(key)}</li>)}</ul></>:<p>{P.no_gaps}</p>}<small>{P.consultation_note}</small></section>
      <h3>{P.acceptance}</h3>{scope(selected).acceptance?.length?<ul>{scope(selected).acceptance.map((text:string)=><li key={text}>{text}</li>)}</ul>:<p>{P.acceptance_pending}</p>}
      <h3>{W.domain_labels.classification}</h3><strong className="work-domain-label">{domainLabel(selected)}</strong><p>{selected.domain_classification.basis}</p><h3>{P.scope}</h3>{scope(selected).boundary&&<p>{scope(selected).boundary}</p>}{selected.capabilities.length?<ul className="work-capabilities">{selected.capabilities.map((c:Data)=><li key={c.id}>{c.label}</li>)}</ul>:<p>{L.scope_pending}</p>}
      {selected.parent_ref&&<p className="work-parent-link">{P.parent+' '}<a href={href(selected.parent_ref)}>{W.units.find((u:Data)=>u.id===selected.parent_ref).label}</a></p>}
      {W.units.some((u:Data)=>u.parent_ref===selected.id)&&<><h3>{P.children}</h3><ul>{W.units.filter((u:Data)=>u.parent_ref===selected.id).map((u:Data)=><li key={u.id}><a href={href(u.id)}>{u.label}</a></li>)}</ul></>}
     </section>}
     {tab==='estimate'&&<>{working&&<UnitScenarioPanel unit={selected}/>}{selected.id===D.scope_revision?.work_unit_ref&&<><MdmOssAssessment assessment={D.mdm_oss_assessment}/>{D.scope_revision.historical?<details className="mdm-oss-details"><summary>{data.ui.essential.scope_revision.historical_title}</summary><ScopeRevisionPanel detail/></details>:<ScopeRevisionPanel detail/>}</>}<WorkEstimatePanel unit={selected} showProposal={selected.id!==D.scope_revision?.work_unit_ref}/></>}
     {tab==='teams'&&<section><h3>{P.tabs.teams}</h3><p>{P.teams_intro}</p>{contributionRows.length?contributionRows.map((c:Data)=><article className="work-contribution" key={c.team_ref??'unallocated'}><h4>{c.team_ref&&c.team_ref!=='governance'?<a href={phaseReadingHash({...context,page:'equipes-produit',view:working?'working':'reference',focus:c.team_ref})!}>{name(c.team_ref)}</a>:name(c.team_ref)}</h4><p>{(noEffort(selected)?P.without_effort:amount(working?c.net_jh:c.jh,false,selected.recurrence==='annual'))+' · '+amount(c.cost_eur_ht,true,selected.recurrence==='annual')}</p><small>{L.rule_refs+' · '+c.rule_refs.join(', ')}</small></article>):<p>{P.no_contribution}</p>}{selected.candidate_refs.length>0&&<section className="work-candidates"><h3>{L.candidates}</h3><p>{P.candidates_intro}</p><ul>{selected.candidate_refs.map((id:string)=><li key={id}>{name(id)}</li>)}</ul></section>}<a href={rulesHref}>{P.rules_link}</a></section>}
     {tab==='sources'&&<section><h3>{P.tabs.sources}</h3><p>{P.sources_intro}</p><p>{selected.basis}</p>{selected.measurements.length?selected.measurements.map((r:Data)=><article className="work-measurement" key={r.id}><h4>{r.label}</h4><p>{amount(r.jh)+' · '+amount(r.cost_eur_ht,true)}</p><small>{L.source+' · '+r.source_ref}</small>{r.roles.length>0&&<ul>{r.roles.map((role:Data)=><li key={role.id}>{role.label+' · '+n(role.jh,1)+' '+L.jh}{role.rate_eur_jh!==undefined&&' · '+n(role.rate_eur_jh,0)+' '+L.rate_unit}</li>)}</ul>}</article>):<p>{P.no_source}</p>}</section>}
    </div>
   </article>
  </>}
 </div>;
}
