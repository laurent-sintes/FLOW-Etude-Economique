import {useContext} from 'react';
import {ReadingScopeContext} from './ReadingScopeContext';
import {DossierLabel} from './Dossier';
import type {Data} from './context';
import {phaseReadingHash,economicReadingContext} from './economicNavigation';

export function PhaseOptionNavigation({journey,phase,option,onChoose,prefix='',horizon}:{journey:Data;phase:string;option:string;onChoose:(id:string)=>void;prefix?:string;horizon?:string}){
 const scope=useContext(ReadingScopeContext),context={...economicReadingContext(scope),returnTo:scope.returnTo,family:scope.family};
 return <nav className="dossier-navigation journey-option-navigation" aria-label={journey.labels.option}>{journey.options.map((o:Data)=><a key={o.id} href={phaseReadingHash({...context,page:prefix+phase,option:o.id,horizon})!} aria-current={o.id===option?'page':undefined} data-open={o.id===option} onClick={()=>onChoose(o.id)}><DossierLabel label={o.label} shortLabel={o.short_label}/></a>)}</nav>;
}
