import {DossierNavigation,DossierSheet,useDossierFocus} from './Dossier';
import {dossierHref,dossierTargetPage,navigationPages,selectDossierPage} from './dossierNavigation';
import type {ReactNode} from 'react';
import {useStudy,type Data} from './context';
import {MethodDocument,MethodText} from './MethodDocument';
import {SourceLink} from './components';
import './deliveryReadiness.css';

export function DeliveryConditionsPage(){
 const {data}=useStudy();
 return <MethodDocument method={data.content.delivery_method} prefix="delivery-conditions" className="delivery-conditions-page"/>;
}

const targetId=(kind:string,id:string)=>'delivery-readiness-'+kind+'-'+id;

export function DeliveryReadinessPage({view,focus}:{view?:string;focus?:string}){
 const {data}=useStudy(),D=data.content.delivery_readiness,L=D.labels;
 const N=data.ui.essential.dossiers.delivery,pages=navigationPages('capacite-realisation',N.pages),current=selectDossierPage(pages,view);
 useDossierFocus(focus);
 const goTo=(kind:string,id:string)=>{
  const owner=dossierTargetPage(pages,kind==='proof'?'partenaire':kind==='role'?'organisation':kind==='gate'?'jalons':id),target=targetId(kind,id);
  if(owner.id!==current.id){location.hash=dossierHref('capacite-realisation',owner.id,pages[0].id,'view',target);return;}
  const element=document.getElementById(target);element?.focus({preventScroll:true});element?.scrollIntoView({block:'start',behavior:'auto'});
 };
 const proofs=new Map<string,Data>(D.proofs.map((row:Data)=>[row.id,row])),roles=new Map<string,Data>(D.roles.map((row:Data)=>[row.id,row])),gates=new Map<string,Data>(D.gates.map((row:Data)=>[row.id,row]));
 const partnerProofs=new Set(D.partner.map((row:Data)=>row.proof_ref));
 const validation=(owner:string)=>owner.endsWith(L.validation_suffix)?owner.slice(0,-L.validation_suffix.length):owner;
 const proofLinks=(ids:string[])=><span className="delivery-proof-links">{ids.map(id=>{const proof=proofs.get(id)!;return <button type="button" className="text-button" key={id} data-proof-ref={id} aria-controls={current.id==='proofs'?targetId('proof',id):undefined} title={proof.title} onClick={()=>goTo('proof',id)}>{proof.short_title}</button>;})}</span>;
 const state=(status:string)=><span className="delivery-state" data-status={status}>{L.states[status]}</span>;
 const section=(id:string,children:ReactNode)=>{if(!current.sections?.includes(id))return null;const row=D.sections.find((item:Data)=>item.id===id);return <li key={id}><section className="core-method-section" aria-labelledby={targetId('section',id)}><h2 id={targetId('section',id)} tabIndex={-1}>{row.title}</h2><p className="core-method-lead"><MethodText>{row.lead}</MethodText></p>{children}</section></li>;};
 return <div className="essential-page core-method-page delivery-readiness-page dossier-page">
  <DossierNavigation pages={pages} current={current.id} label={N.navigation}/>
  <DossierSheet view={current.id}>
  {current.id==='missions'&&<section className="core-method-introduction" aria-labelledby="delivery-readiness-principle-title">
   <h2 id="delivery-readiness-principle-title">{D.principle.title}</h2><p className="delivery-review-date">{L.review_date} <time dateTime={D.date}>{new Intl.DateTimeFormat(data.ui.locale,{dateStyle:'long',timeZone:'UTC'}).format(new Date(D.date))}</time></p>
   <p><MethodText>{D.principle.text}</MethodText></p>
   <div className="delivery-document-summary"><p><strong>{D.proofs.filter((p:Data)=>p.status==='disponible').length}</strong> {L.available_summary}</p><p><strong>{D.proofs.filter((p:Data)=>p.status==='attendue').length}</strong> {L.expected_summary}</p></div>
   <aside className="core-method-notice"><h3>{D.notice.title}</h3><p><MethodText>{D.notice.text}</MethodText></p></aside>
   <p><a className="text-button" href={D.method_link.href}>{D.method_link.label} →</a></p>
  </section>}
  <ol className="core-method-sections">
   {section('organisation',<div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={D.sections[0].title}><table className="core-method-table delivery-role-table"><thead><tr>{L.role_columns.map((text:string)=><th scope="col" key={text}>{text}</th>)}</tr></thead><tbody>{D.roles.map((role:Data)=><tr key={role.id} data-delivery-role={role.id}><th scope="row" id={targetId('role',role.id)} tabIndex={-1}>{role.title}</th><td><p>{role.actor}</p><small title={role.validation_owner}>{L.validation_label} : {validation(role.validation_owner)}</small></td><td>{state(role.status)}{proofLinks(role.proof_refs)}</td></tr>)}</tbody></table></div>)}
   {section('points-chauds',<div className="delivery-hotspots">{D.hotspots.map((hotspot:Data)=>{const role=roles.get(hotspot.role_ref)!,gate=gates.get(hotspot.gate_ref)!;return <article key={hotspot.id} data-hotspot={hotspot.id}><h3>{hotspot.title}</h3><p>{hotspot.risk}</p><p><strong>{L.action_label} : </strong>{hotspot.action}</p><div className="delivery-case-relations"><button type="button" className="text-button" aria-controls={current.id==='missions'?targetId('role',role.id):undefined} onClick={()=>goTo('role',role.id)}>{role.title}</button><button type="button" className="text-button" aria-controls={current.id==='gates'?targetId('gate',gate.id):undefined} onClick={()=>goTo('gate',gate.id)}>{gate.title}</button></div>{proofLinks([...hotspot.available_refs,...hotspot.expected_refs])}<div className="delivery-native-links">{hotspot.capability_refs.map((id:string)=>{const capability=D.scope.rows.find((row:Data)=>row.capability_id===id);return <SourceLink path={capability.href} key={id}>{capability.name}</SourceLink>;})}</div></article>;})}</div>)}
   {section('partenaire',<div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={D.sections[2].title}><table className="core-method-table delivery-proof-register"><thead><tr>{L.proof_columns.map((text:string)=><th scope="col" key={text}>{text}</th>)}</tr></thead><tbody>{D.proofs.map((proof:Data)=><tr key={proof.id} data-delivery-proof={proof.id}><th scope="row"><h3 id={targetId('proof',proof.id)} tabIndex={-1}>{proof.title}</h3>{partnerProofs.has(proof.id)&&<small className="delivery-partner-requirement">{L.partner_requirement}</small>}</th><td><span className="delivery-state" data-status={proof.status}>{L.proof_states[proof.status]}</span>{proof.href&&<SourceLink path={proof.href}>{L.proof_access}</SourceLink>}</td><td>{proof.detail}</td></tr>)}</tbody></table></div>)}
   {section('jalons',<div className="delivery-gates">{D.gates.map((gate:Data)=><article key={gate.id} data-delivery-gate={gate.id}><header><h3 id={targetId('gate',gate.id)} tabIndex={-1}>{gate.title}</h3>{state(gate.status)}</header><p>{gate.expected}</p><p className="delivery-validation" title={gate.validation_owner}><strong>{L.validation_label} : </strong>{validation(gate.validation_owner)}</p><dl><div><dt>{L.proceed_label}</dt><dd>{gate.proceed}</dd></div><div><dt>{L.reconsider_label}</dt><dd>{gate.reconsider}</dd></div></dl>{proofLinks(gate.proof_refs)}</article>)}</div>)}
  </ol>
  <a className="text-button essential-structure-next" href={D.next.href}>{D.next.label} →</a>
  </DossierSheet>
 </div>;
}
