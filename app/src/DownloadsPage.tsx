import {useEffect,useState} from 'react';
import {ArrowRight,Download,RefreshCw} from 'lucide-react';
import {useStudy,useFormat,type Data} from './context';
import {fileHref} from './transport';
import {FileFormatMark} from './FileFormatMark';
import {MethodText} from './MethodDocument';
import {ReadingNote} from './ReadingNote';
import './downloads.css';

export function DownloadsPage(){
 const {data}=useStudy(),{n}=useFormat(),D=data.content.downloads,L=D.reading;
 const [metadata,setMetadata]=useState<Data|null>(null),[failed,setFailed]=useState(false),[attempt,setAttempt]=useState(0);
 const packageUrl=import.meta.env.BASE_URL+D.model_package.asset;
 useEffect(()=>{
  const controller=new AbortController();setFailed(false);setMetadata(null);
  fetch(import.meta.env.BASE_URL+D.model_package.metadata_asset,{signal:controller.signal}).then(async response=>{
   if(!response.ok)throw Error('ERR_DOWNLOAD_METADATA');
   const value=await response.json();
   if(value.asset!==D.model_package.asset||!Number.isSafeInteger(value.bytes)||value.bytes<=0||!Number.isSafeInteger(value.sources)||value.sources<=0||value.format_version!==2||![value.sha256,value.source_fingerprint].every(v=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v)))throw Error('ERR_DOWNLOAD_METADATA');
   if(!controller.signal.aborted)setMetadata(value);
  }).catch(()=>{if(!controller.signal.aborted)setFailed(true);});
  return()=>controller.abort();
 },[D.model_package.asset,D.model_package.metadata_asset,attempt]);
 const dateLabels=data.content.synvance_reference.documents.date_labels;
 const dateLabel=(row:Data)=>dateLabels[row.date?.nature||'unknown'];
 const size=(bytes:number)=>n(bytes/1_000_000,1)+' '+L.size_unit;
 const documentDate=(row:Data)=>row.date?.value?new Intl.DateTimeFormat(data.ui.locale,{dateStyle:'long',timeZone:'UTC'}).format(new Date(row.date.value+'T12:00:00Z')):L.date_unknown;
 const card=(row:Data,original=false)=><li key={row.path} className="download-card">
  <div className="download-card-heading"><FileFormatMark format={row.format}/><h3>{row.title}</h3></div>
  <p><MethodText>{row.description}</MethodText></p>
  {original&&<p className="download-origin">{row.author} · {dateLabel(row)+' : '+documentDate(row)}</p>}
  <p className="download-file-meta"><span>{row.filename}</span><span>{size(row.bytes)}</span></p>
  <a className="secondary download-action" href={fileHref(row.path)} download={row.filename} aria-label={L.download+' · '+row.title+' · '+row.format}><Download size={17} aria-hidden="true"/>{L.download}<span className="download-format">{row.format}</span></a>
  <details className="download-details"><summary>{L.details}</summary><dl><dt>{L.hash_label}</dt><dd><code>{row.sha256}</code></dd>{row.date?.provenance&&<><dt>{dateLabel(row)}</dt><dd>{row.date.provenance}</dd></>}</dl></details>
 </li>;
 return <div className="essential-page downloads-page">
  <section className="download-model" aria-labelledby="download-model-title"><div className="download-card-heading"><FileFormatMark format={L.model_format}/><h2 id="download-model-title">{L.model_title}</h2></div><p>{L.model_description}</p>
   <a className="primary download-action" href={packageUrl} download={D.model_package.filename} aria-label={L.model_action+' · '+L.model_format}><Download size={18} aria-hidden="true"/>{L.model_action}<span className="download-format">{L.model_format}</span></a>
   {metadata&&<><dl className="download-model-meta"><div><dt>{L.size_label}</dt><dd>{size(metadata.bytes)}</dd></div><div><dt>{L.version_label}</dt><dd><code title={metadata.source_fingerprint}>{metadata.source_fingerprint.slice(0,12)}</code></dd></div></dl><details className="download-details"><summary>{L.details}</summary><dl><dt>{L.hash_label}</dt><dd><code>{metadata.sha256}</code></dd></dl></details></>}
   {failed&&<p className="download-metadata-status" role="status">{L.metadata_unavailable}<button className="text-button" onClick={()=>setAttempt(a=>a+1)}><RefreshCw size={14} aria-hidden="true"/>{L.retry}</button></p>}
   <ReadingNote>{L.model_limit}</ReadingNote>
  </section>
  <section aria-labelledby="download-originals-title"><h2 id="download-originals-title">{L.originals_title}</h2><p>{L.originals_intro}</p><ul className="download-grid">{D.originals.map((row:Data)=>card(row,true))}</ul></section>
  <section aria-labelledby="download-documents-title"><h2 id="download-documents-title">{L.documents_title}</h2><p>{L.documents_intro}</p><ul className="download-grid">{D.documents.map((row:Data)=>card(row))}</ul></section>
  <section className="download-personal" aria-labelledby="download-personal-title"><div className="download-card-heading"><FileFormatMark format={L.personal_format}/><h2 id="download-personal-title">{L.personal_title}</h2></div><p>{L.personal_description}</p><a className="secondary download-action" href={D.personal_route}>{L.personal_action}<ArrowRight size={17} aria-hidden="true"/></a></section>
 </div>;
}
