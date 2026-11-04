import {ArrowRight} from 'lucide-react';
import {useStudy,type Data} from './context';
import {economicHash,phaseReadingHash} from './economicNavigation';
import {MethodText} from './MethodDocument';
import {useReadingContext} from './ReadingScopeContext';

function Responsibilities({headers,rows}:{headers:string[];rows:{id:string;label:string;mission:string;capacity?:string}[]}){
 return <table className="eco-table delivery-responsibilities">
  <thead><tr>{headers.map(header=><th scope="col" key={header}>{header}</th>)}</tr></thead>
  <tbody>{rows.map(row=><tr key={row.id}><th scope="row">{row.label}</th><td className="delivery-mission"><MethodText>{row.mission}</MethodText></td>{row.capacity&&<td className="delivery-mission">{row.capacity}</td>}</tr>)}</tbody>
 </table>;
}

export function DeliveryOrganisationPage({page,option,focus}:{page:'organisation-delivery'|'equipes-produit'|'integration-transverse';option:string;focus?:string}){
 const {data}=useStudy();
 const copy=data.ui.essential.delivery_organisation;
 const office=data.content.framework.transformation;
 const team=copy.teams.find((item:Data)=>item.id===focus)||copy.teams[0];
 const next=page==='organisation-delivery'?'equipes-produit':page==='equipes-produit'?'integration-transverse':null;
 const context=useReadingContext();
 const assumptions=economicHash({...context,page:'parametres',option,focus:'programme'})!;
 const nextLink=next?phaseReadingHash({...context,page:next,option})!:economicHash({...context,page:'evaluation-core',option})!;

 return <div className="essential-page economic-dossier">
  {page==='organisation-delivery'&&<section className="eco-section">
   <p><MethodText>{copy.office_intro}</MethodText></p>
   <Responsibilities headers={[copy.office_role_column,copy.office_mission_column,copy.capacity_column]}
    rows={office.roles.map((role:Data)=>({id:role.id,label:role.nom,mission:role.mission,capacity:role.etp+' '+copy.office_capacity_unit}))}/>
   <p>{copy.office_budget}</p>
   <a className="text-button" href={assumptions}>{copy.assumptions_link} →</a>
  </section>}
  {page==='equipes-produit'&&<section className="eco-section">
   <p><MethodText>{copy.teams_intro}</MethodText></p>
   <nav className="eco-options delivery-team-navigation" aria-label={copy.teams_navigation}>
    {copy.teams.map((item:Data)=><a key={item.id} href={phaseReadingHash({...context,page,option,focus:item.id})!} aria-current={item.id===team.id?'true':undefined}>{item.title}</a>)}
   </nav>
   <h2>{team.title}</h2>
   <p>{team.scope}</p>
   <h3>{copy.team_roles_title}</h3>
   <Responsibilities headers={[copy.profile_column,copy.mission_column,copy.capacity_column]}
    rows={[
     ...['product','analysis','development','qa'].map(id=>({id,label:copy[id+'_role'],mission:team.roles[id],capacity:id==='product'?copy.po_capacity:copy.variable_capacity})),
     ...copy.shared_roles.map((role:Data)=>({id:role.label,label:role.label,mission:role.mission,capacity:copy.shared_capacity}))
    ]}/>
   <p>{copy.capacity_note}</p>
   <p>{copy.buy}</p>
  </section>}
  {page==='integration-transverse'&&<section className="eco-section">
   <p><MethodText>{copy.coordination_intro}</MethodText></p>
   <Responsibilities headers={[copy.train_area_column,copy.train_mission_column]}
    rows={copy.coordination_roles.map((role:Data)=>({id:role.label,label:role.label,mission:role.mission}))}/>
   <h2>{copy.example_title}</h2>
   <p>{copy.example}</p>
   <p><a className="text-button" href="https://framework.scaledagile.com/team-and-technical-agility-discipline/">{copy.coordination_reference}</a></p>
  </section>}
  <a className="framework-phase-next text-button" href={nextLink}>{next?data.ui.essential.pages[next].title:copy.costs_link}<ArrowRight size={18} aria-hidden="true"/></a>
 </div>;
}
