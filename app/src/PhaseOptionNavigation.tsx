import {useContext} from 'react';
import {ReadingScopeContext} from './ReadingScopeContext';
import {DossierLabel} from './Dossier';
import {PhaseIcon} from './StudyIcons';
import type {Data} from './context';
import {phaseReadingHash,economicReadingContext} from './economicNavigation';

export function PhaseOptionNavigation({journey,phase,option,onChoose,prefix='',horizon}:{journey:Data;phase:string;option:string;onChoose:(id:string)=>void;prefix?:string;horizon?:string}){
 const scope=useContext(ReadingScopeContext),context={...economicReadingContext(scope),returnTo:scope.returnTo,family:scope.family};
 return <><nav className="framework-phase-track" aria-label={journey.labels.phases}>{journey.phases.map((p:Data)=><a href={phaseReadingHash({...context,page:prefix+p.id,option,horizon})!} key={p.id} aria-current={p.id===phase?'step':undefined}><span aria-hidden="true"><PhaseIcon phase={p.id} size={18}/></span>{p.short_title}</a>)}</nav>
  <nav className="dossier-navigation journey-option-navigation" aria-label={journey.labels.option}>{journey.options.map((o:Data)=><a key={o.id} href={phaseReadingHash({...context,page:prefix+phase,option:o.id,horizon})!} aria-current={o.id===option?'page':undefined} data-open={o.id===option} onClick={()=>onChoose(o.id)}><DossierLabel label={o.label} shortLabel={o.short_label}/></a>)}</nav></>;
}
