import {useEffect,useLayoutEffect,useId,useRef,useState,type ReactNode} from 'react';
import {createPortal} from 'react-dom';
import {useStudy,type Data} from './context';

function TermLink({id}:{id:string}){
 const {data}=useStudy();const term=data.glossary.notions[id];const anchor=useRef<HTMLButtonElement>(null),bubble=useRef<HTMLSpanElement>(null);const tooltipId=useId();
 const closeTimer=useRef<ReturnType<typeof setTimeout>|null>(null);const show=()=>{if(closeTimer.current)clearTimeout(closeTimer.current);setOpen(true);};const hide=()=>{closeTimer.current=setTimeout(()=>setOpen(false),150);};useEffect(()=>()=>{if(closeTimer.current)clearTimeout(closeTimer.current);},[]);
 const [open,setOpen]=useState(false),[position,setPosition]=useState({left:8,top:8});
 useLayoutEffect(()=>{if(!open)return;const place=()=>{const a=anchor.current?.getBoundingClientRect(),b=bubble.current?.getBoundingClientRect();if(!a||!b)return;setPosition({left:Math.max(8,Math.min(a.left,window.innerWidth-b.width-8)),top:a.top>=b.height+16?a.top-b.height-8:Math.max(8,Math.min(a.bottom+8,window.innerHeight-b.height-8))});};place();const dismiss=(e:KeyboardEvent)=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();setOpen(false);}};window.addEventListener('resize',place);window.addEventListener('scroll',place,true);window.addEventListener('keydown',dismiss,true);return()=>{window.removeEventListener('resize',place);window.removeEventListener('scroll',place,true);window.removeEventListener('keydown',dismiss,true);};},[open]);
 return <span className="glossary-inline" onMouseEnter={show} onMouseLeave={hide}><button ref={anchor} type="button" className="glossary-term" aria-describedby={open?tooltipId:undefined} aria-expanded={open} onFocus={show} onBlur={()=>setOpen(false)} onClick={show}>{term.libelle}</button>{open&&createPortal(<span ref={bubble} id={tooltipId} role="tooltip" className="glossary-tooltip" style={position} onMouseEnter={show} onMouseLeave={hide}>{term.definition}</span>,anchor.current?.closest('dialog')||document.body)}</span>;
}

export function GlossaryText({children,linked=true}:{children:ReactNode;linked?:boolean}){
 const {data}=useStudy();if(typeof children!=='string')return <>{children}</>;
 const config=data.ui.glossary_links;const terms=config.terms.flatMap((term:Data)=>term.matches.map((label:string)=>({label,id:term.id})));const protectedLabels:string[]=config.protected_labels;
 const entries=[...protectedLabels.map(label=>({label,id:null})),...terms].sort((a,b)=>b.label.length-a.label.length);
 const escape=(s:string)=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
 const pattern=new RegExp('(?<![\\p{L}\\p{N}_])('+entries.map(e=>escape(e.label)).join('|')+')(?![\\p{L}\\p{N}_])','gu');
 const parts:ReactNode[]=[];let offset=0;for(const match of children.matchAll(pattern)){const index=match.index!;parts.push(children.slice(offset,index));const entry=entries.find(e=>e.label===match[0]);parts.push(entry?.id?(linked?<TermLink key={index} id={entry.id}/>:data.glossary.notions[entry.id].libelle):match[0]);offset=index+match[0].length;}parts.push(children.slice(offset));return <>{parts}</>;
}
