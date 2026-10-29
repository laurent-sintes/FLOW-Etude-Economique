import {GlossaryText} from './GlossaryText';
import {useEffect,useId,useRef,useState,type ReactNode} from 'react';
import {ArrowUpRight,ArrowRight,BookmarkCheck,Search,X,Info,ChevronRight,FileText} from 'lucide-react';
import {useReadingArrival} from './ReadingIdentity';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {request,useStudy,type Data} from './context';
import {fileHref} from './transport';
import {isModelDataReference} from './documentVisibility';

export function SourceLink({path,children}:{path:string;children?:ReactNode}){
 const {data,openDoc}=useStudy(),route=data.ui.document_routes?.[path.split('#')[0]];
 if(isModelDataReference(path))return null;
 const destination=path.startsWith('#')?path:route;
 if(destination)return <a className="source-link" href={destination}>{children||data.ui.labels.source}<ArrowUpRight size={13}/></a>;
 const outside=/^https?:\/\//.test(path),isDoc=/\.(md|yaml|py)(#.*)?$/.test(path);
 if(outside||!isDoc){const href=outside?path:fileHref(path);if(href)return <a className="source-link" href={href} target="_blank" rel="noreferrer">{children||data.ui.labels.source}<ArrowUpRight size={13}/></a>;}
 return <button className="source-link" onClick={()=>openDoc(path)}>{children||data.ui.labels.source}<ArrowUpRight size={13}/></button>;
}
export function Notice({children,quiet=false}:{children:ReactNode;quiet?:boolean}){return <div className={quiet?'notice quiet':'notice'}><Info size={17}/><div>{children}</div></div>;}
export function SearchField({value,onChange,label}:{value:string;onChange:(value:string)=>void;label?:string}){const {data}=useStudy();return <label className="search"><Search size={16}/><input aria-label={label||data.ui.labels.search} placeholder={label||data.ui.labels.search} value={value} onChange={e=>onChange(e.target.value)}/>{value&&<button aria-label={data.ui.labels.clear_search} onClick={()=>onChange('')}><X size={14}/></button>}</label>;}
export function Section({title,description,action,children,className=''}:{title:string;description?:string;action?:ReactNode;children:ReactNode;className?:string}){return <section className={'section '+className}><div className="section-heading"><div><h2><GlossaryText>{title}</GlossaryText></h2>{description&&<p><GlossaryText>{description}</GlossaryText></p>}</div>{action}</div>{children}</section>;}
export function OptionTabs({selected,onSelect,makeOnly=false}:{selected:string;onSelect:(slug:string)=>void;makeOnly?:boolean}){const {data}=useStudy();return <div className="option-tabs" role="tablist">{data.baseline.options.filter(o=>!makeOnly||o.mode==='Make').map(o=><button role="tab" aria-selected={selected===o.stack} key={o.stack} className={selected===o.stack?'active':''} onClick={()=>onSelect(o.stack)}><i style={{background:data.ui.option_colors[o.stack]}}/>{o.name}</button>)}</div>;}
export function Metric({label,value,unit,sub}:{label:string;value:ReactNode;unit?:string;sub?:ReactNode}){return <div className="metric"><span>{label}</span><strong>{value}{unit&&<small>{unit}</small>}</strong>{sub&&<div className="metric-sub">{sub}</div>}</div>;}
export function Drawer({title,onClose,children,wide=false}:{title:string;onClose:()=>void;children:ReactNode;wide?:boolean}){const {data}=useStudy();const titleId=useId(),ref=useRef<HTMLDialogElement>(null);useEffect(()=>{const previous=document.activeElement as HTMLElement;ref.current?.showModal();return()=>previous?.focus({preventScroll:true});},[]);return <dialog ref={ref} aria-labelledby={titleId} className={'drawer '+(wide?'wide':'')} onCancel={onClose} onClick={e=>{if(e.target===e.currentTarget)onClose();}}><div className="drawer-shell"><header><h2 id={titleId}><GlossaryText>{title}</GlossaryText></h2><button className="icon-button" onClick={onClose} aria-label={data.ui.labels.close}><X size={22}/></button></header><div className="drawer-content">{children}</div></div></dialog>;}
export function DocumentViewer({path,onClose}:{path:string;onClose:()=>void}){
 const {data}=useStudy(),F=data.ui.document_focus;
 const [doc,setDoc]=useState<Data|null>(null),[error,setError]=useState(''),[fullPath,setFullPath]=useState('');
 const hidden=isModelDataReference(path),sourcePath=path.split('#')[0],isFull=fullPath===path,requestedPath=isFull?sourcePath:path,download=hidden?null:fileHref(sourcePath);
 const hasFragment=Boolean(path.split('#').slice(1).join('#'));
 useEffect(()=>{if(hidden)onClose();},[hidden,onClose]);
 useEffect(()=>{
  if(hidden)return;
  let current=true;setDoc(null);setError('');
  request<Data>('/api/document?path='+encodeURIComponent(requestedPath)).then(d=>{if(current)setDoc(d);}).catch(e=>{if(current)setError(data.ui.errors[e.code]||data.ui.errors.missing_document);});
  return()=>{current=false;};
 },[requestedPath,data.ui.errors,hidden]);
 if(hidden)return null;
 const title=data.ui.documents.find((d:Data)=>d.path===sourcePath)?.title||sourcePath.split('/').pop();
 return <Drawer title={title} onClose={onClose} wide>
  <div className="document-meta"><FileText size={16}/><span>{sourcePath}</span>{download&&<a className="source-link" href={download} download>{data.ui.labels.download}<ArrowUpRight size={13}/></a>}</div>
  {hasFragment&&<p><button className="source-link" onClick={()=>setFullPath(isFull?'':path)}>{isFull?F.excerpt:F.full}<ArrowUpRight size={13}/></button></p>}
  {error&&<Notice>{error}</Notice>}
  {!doc&&!error&&<p>{data.ui.labels.loading}</p>}
  {doc?.focus&&<Notice quiet={doc.focus.status==='matched'}><strong>{F[doc.focus.status]}</strong><p>{doc.focus.status==='matched'?F.location:F.requested}{' · '}<code>{doc.focus.location||doc.focus.fragment}</code></p>{doc.focus.candidates.length>0&&<><p>{F.candidates}</p><ul>{doc.focus.candidates.map((candidate:Data)=><li key={candidate.reference}><SourceLink path={sourcePath+'#'+candidate.reference}>{candidate.location}</SourceLink></li>)}</ul></>}</Notice>}
  {doc&&isFull&&hasFragment&&<p>{F.complete}</p>}
  {doc?.content&&(doc.format==='.md'?<article className="markdown"><Markdown remarkPlugins={[remarkGfm]} components={{a:({href,children})=>{
   if(!href)return <span>{children}</span>;
   if(href.startsWith('#')&&data.ui.essential.nav.some((route:Data)=>'#'+route.id===href))return <a href={href} onClick={onClose}>{children}</a>;
   const relative=new URL(href,'http://reference/'+doc.path);
   const target=/^https?:/.test(href)?href:decodeURIComponent(relative.pathname.slice(1))+relative.hash;
   return isModelDataReference(target)?<span>{children}</span>:<SourceLink path={target}>{children}</SourceLink>;
  }}}>{doc.content}</Markdown></article>:<pre className="document-code">{doc.content}</pre>)}
 </Drawer>;
}
export function Empty(){const {data}=useStudy();return <p className="empty">{data.ui.labels.no_result}</p>;}
export function JourneyNext({page}:{page:string}){
 const {data}=useStudy();const {ref,arrived}=useReadingArrival(page);const J=data.ui.reading_journey,item=J.steps[page];if(!item)return null;
 const destination=data.ui.nav.find((entry:Data)=>entry.id===item.to.split('?')[0]);if(!destination)return null;
 return <nav ref={ref} className="journey-next" data-arrived={arrived} aria-label={J.label}>
  <div className="journey-takeaway"><div className="journey-signature"><span className="journey-icon" aria-hidden="true"><BookmarkCheck size={25}/></span><h2>{J.takeaway_label}</h2></div><p>{item.takeaway}</p></div>
  <div className="journey-destination"><span className="journey-prompt">{J.next_label}</span><a href={'#'+item.to} aria-describedby={'journey-purpose-'+page}>{destination.label}<ArrowRight size={20} aria-hidden="true"/></a><p id={'journey-purpose-'+page}>{item.text}</p></div>
 </nav>;
}
export function Disclosure({title,children,meta}:{title:string;children:ReactNode;meta?:ReactNode}){return <details className="disclosure"><summary><ChevronRight size={16}/><span><GlossaryText linked={false}>{title}</GlossaryText></span>{meta&&<small>{meta}</small>}</summary><div className="disclosure-body">{children}</div></details>;}

