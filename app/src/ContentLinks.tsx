import {ArrowRight} from 'lucide-react';
import {useStudy,type Data} from './context';
import {economicDestination} from './economicNavigation';

// Global destinations belong in the sidebar. A content link must add a
// specific detail, a local section, a source, or a destination outside it.
export function ContentLinks({links,label,className=''}:{links:{href:string;label:string}[];label:string;className?:string}){
 const {data}=useStudy();
 const pages=new Set(data.ui.essential.nav_groups.filter((group:Data)=>!group.hidden).flatMap((group:Data)=>group.items));
 const items=links.filter(link=>{
  if(!link.href.startsWith('#'))return true;
  const [page,query='']=link.href.slice(1).split('?'),params=new URLSearchParams(query);
  const destination=economicDestination(page,params)?.page||page;
  if(!pages.has(destination))return true;
  return [...params].some(([key,value])=>Boolean(value)&&!['option','options','horizon','origin','zone','returnTo'].includes(key)&&(key!=='view'||!/^\d+$/.test(value)));
 });
 return items.length?<nav className={className} aria-label={label} style={{display:'flex',flexWrap:'wrap',gap:'.6rem 1.2rem'}}>{items.map(link=><a className="text-button" key={link.href} href={link.href}>{link.label}<ArrowRight size={15} aria-hidden="true"/></a>)}</nav>:null;
}
