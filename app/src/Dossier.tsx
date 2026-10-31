import {useEffect,type ReactNode} from 'react';
import {Folder,FolderOpen} from 'lucide-react';
import type {DossierEntry} from './dossierNavigation';
import './dossier.css';

export function DossierLabel({label,shortLabel}:{label:string;shortLabel?:string}){
 return <><Folder className="dossier-folder-closed" size={18} aria-hidden="true"/><FolderOpen className="dossier-folder-open" size={18} aria-hidden="true"/><span className="dossier-label">{label}</span><span className="dossier-short-label" aria-hidden="true">{shortLabel||label}</span></>;
}
export function DossierNavigation({pages,current,label,className='',ancestor=false}:{pages:DossierEntry[];current:string;label:string;className?:string;ancestor?:boolean}){
 return <nav className={'dossier-navigation '+className} aria-label={label}>{pages.map(page=><a key={page.id} href={page.href} title={page.description} aria-label={page.label} data-open={current===page.id} aria-current={current===page.id?(ancestor?'location':'page'):undefined}><DossierLabel label={page.label} shortLabel={page.short_label}/></a>)}</nav>;
}
export function DossierSheet({view,children}:{view:string;children:ReactNode}){
 return <div className="dossier-sheet"><div className="dossier-content" key={view}>{children}</div></div>;
}
export function useDossierFocus(target?:string){
 useEffect(()=>{if(!target)return;const frame=requestAnimationFrame(()=>{const element=document.getElementById(target);element?.focus({preventScroll:true});element?.scrollIntoView({block:'start',behavior:'auto'});});return()=>cancelAnimationFrame(frame);},[target]);
}
