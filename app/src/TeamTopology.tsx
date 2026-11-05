import {useId,type CSSProperties} from 'react';
import './deliveryTopology.css';
import {ChevronDown,ArrowUpRight} from 'lucide-react';
import {useStudy,type Data} from './context';
import {phaseReadingHash} from './economicNavigation';
import {useReadingContext} from './ReadingScopeContext';

// Adapted from Team Topologies Team-Shape-Templates, CC BY-SA 4.0.
// Graphical adaptations in this file and deliveryTopology.css share that license.
export function TeamMark({type,color}:{type:string;color:string}){
 return <span aria-hidden="true" className="tt-team-mark" data-team-type={type} style={{'--team-color':color} as CSSProperties}><i/></span>;
}
// Book notation: shared hatched/dotted area, or paired service brackets.
// The explanatory diagrams show both teams. The map uses the shared symbol.
export function InteractionMark({mode,color,angle=0,illustrated=false}:{mode:string;color:string;angle?:number;illustrated?:boolean}){
 const id=useId().replace(/:/g,''),pattern=id+'-pattern';
 const lens=illustrated?'M100 12.5A44 44 0 0 1 100 83.5A44 44 0 0 1 100 12.5Z':'M16 2Q38 16 16 30Q-6 16 16 2Z';
 return <svg aria-hidden="true" focusable="false" className={'tt-interaction-mark'+(illustrated?' tt-interaction-illustration':'')} data-mode={mode} data-notation="book" viewBox={illustrated?'0 0 200 96':'0 0 32 32'} style={{'--mode-color':color,transform:!illustrated&&mode==='x-as-a-service'?`rotate(${angle}deg)`:undefined} as CSSProperties}>
  {mode!=='x-as-a-service'&&<defs><pattern id={pattern} width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#CBB5DC"/>{mode==='collaboration'?<path d="M0,0 8,8M8,0 0,8" fill="none" stroke={color} strokeWidth="1.6"/>:<circle cx="4" cy="4" r="1.7" fill={color}/>}</pattern></defs>}
  {illustrated&&<g strokeWidth="3"><circle cx={mode==='x-as-a-service'?45:74} cy="48" r={mode==='x-as-a-service'?40:44} fill="#F2C595" stroke="#CC954E"/><circle cx={mode==='x-as-a-service'?155:126} cy="48" r={mode==='x-as-a-service'?40:44} fill="#96C6DC" stroke="#709FB8"/></g>}
  {mode==='x-as-a-service'?<g transform={illustrated?'translate(84 32)':undefined} fill="none" stroke={color} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"><path d="M3 5H8Q12 5 12 10V22Q12 27 8 27H3"/><path d="M29 5H24Q20 5 20 10V22Q20 27 24 27H29"/></g>:<path className="tt-shared-area" d={lens} fill={'url(#'+pattern+')'} stroke={color} strokeWidth={illustrated?3:2}/>}
 </svg>;
}
export function TeamBadge({team}:{team:Data}){
 const {data}=useStudy(),kind=data.content.delivery_organisation.team_types.find((t:Data)=>t.id===team.type);
 return <span className="delivery-team-badge" data-team-type={kind.id} style={{'--team-color':kind.color} as CSSProperties}><TeamMark type={kind.id} color={kind.color}/>{kind.label}</span>;
}
export function TeamDirectory({selected,option,view}:{selected:string;option:string;view?:string}){
 const {data}=useStudy(),D=data.content.delivery_organisation,L=D.labels,context=useReadingContext();
 return <nav className="delivery-team-directory" aria-label={L.team_filter}><p className="delivery-directory-title">{L.team_directory}</p>{D.team_types.map((kind:Data)=><section key={kind.id}><h3><TeamMark type={kind.id} color={kind.color}/>{kind.label}</h3>{D.teams.filter((t:Data)=>t.type===kind.id).map((t:Data)=><a key={t.id} href={phaseReadingHash({...context,page:'equipes-produit',option,view,focus:t.id})!} aria-current={selected===t.id?'page':undefined}><span>{t.label}</span><ArrowUpRight size={15} aria-hidden="true"/></a>)}</section>)}</nav>;
}
export function TeamSelect({value,onChange}:{value:string;onChange:(value:string)=>void}){
 const {data}=useStudy(),D=data.content.delivery_organisation,L=D.labels,id=useId();
 return <label className="delivery-selector delivery-select-field"><span id={id}>{L.team_filter}</span><span className="delivery-select-control"><select aria-labelledby={id} value={value} onChange={event=>onChange(event.target.value)}><option value="">{L.all_teams}</option>{D.team_types.map((kind:Data)=><optgroup key={kind.id} label={kind.label}>{D.teams.filter((t:Data)=>t.type===kind.id).map((t:Data)=><option key={t.id} value={t.id}>{t.label}</option>)}</optgroup>)}</select><ChevronDown size={18} aria-hidden="true"/></span></label>;
}
export function TopologyAttribution(){
 const {data}=useStudy(),L=data.content.delivery_organisation.labels;
 return <p className="delivery-topology-credit">{L.shapes_credit} <a href="https://github.com/TeamTopologies/Team-Shape-Templates">{L.shapes_kit}</a> · <a href="https://creativecommons.org/licenses/by-sa/4.0/">{L.shapes_license}</a></p>;
}
