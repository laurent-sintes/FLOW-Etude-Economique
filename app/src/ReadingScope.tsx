import {useEffect,useId,useRef,useState,type CSSProperties,type FormEvent} from 'react';
import {ChevronDown,SlidersHorizontal} from 'lucide-react';
import {useStudy} from './context';
import {economicHash,economicPeriod,readingOrigin,readingOrigins,shownOptions,type EconomicRoute} from './economicNavigation';
import './readingScope.css';

export function ReadingScope({route}:{route:EconomicRoute}){
 const {data}=useStudy(),T=data.ui.essential.economic_dossier.reading_scope;
 const id=useId(),trigger=useRef<HTMLButtonElement>(null);
 const [open,setOpen]=useState(false),[duration,setDuration]=useState(String(economicPeriod(route))),[origin,setOrigin]=useState(readingOrigin(route)),[selected,setSelected]=useState(shownOptions(route)),[error,setError]=useState('');
 useEffect(()=>{setOpen(false);setError('');},[route.page,route.option,route.horizon,route.view,route.origin,route.options]);
 const comparative=route.page==='comparer';
 const year=economicPeriod(route),unit=year===1?T.one_year:T.years;
 const scope=route.page==='parametres'?T.all_options:comparative?(shownOptions(route).length===3?T.all_options:shownOptions(route).map(key=>T.option_names[key]).join(', ')):T.option_names[route.option||'java-spring'];
 const summary=T.summary.replace('{years}',String(year)).replace('{unit}',unit).replace('{origin}',T.origin_phrases[readingOrigin(route)]).replace('{options}',scope);
 const close=()=>{setOpen(false);trigger.current?.focus({preventScroll:true});};
 const toggle=()=>{if(open){close();return;}setDuration(String(year));setOrigin(readingOrigin(route));setSelected(shownOptions(route));setError('');setOpen(true);};
 const apply=(event:FormEvent)=>{
  event.preventDefault();
  if(!/^(?:[1-9]|1[0-5])$/.test(duration)){setError(T.duration_error);return;}
  if(comparative&&!selected.length){setError(T.options_error);return;}
  const next=economicHash({...route,horizon:duration,origin,options:selected.join(','),view:/^\d+$/.test(route.view||'')?undefined:route.view})!;
  if(next!==location.hash){history.pushState(null,'',next);window.dispatchEvent(new PopStateEvent('popstate'));}
  close();
 };
 return <div className="reading-scope" onKeyDown={event=>{if(open&&event.key==='Escape'){event.preventDefault();event.stopPropagation();close();}}}>
  <button ref={trigger} type="button" className="reading-scope-trigger" aria-expanded={open} aria-controls={id} onClick={toggle}><SlidersHorizontal size={19} aria-hidden="true"/><span><small>{T.title}</small><strong>{summary}</strong></span><ChevronDown size={18} aria-hidden="true"/></button>
  {route.page==='parametres'&&<p className="reading-scope-fixed">{T.fixed_reading_hint}</p>}
  {open&&<form id={id} className="reading-scope-panel" onSubmit={apply} noValidate>
   <fieldset><legend>{T.start}</legend><div className="reading-scope-origins">{readingOrigins.map(value=><label key={value}><input type="radio" name={id+'-origin'} value={value} checked={origin===value} onChange={()=>setOrigin(value)}/><span><b>{T.origins[value]}</b><small>{T.origin_help[value]}</small></span></label>)}</div></fieldset>
   <fieldset className="reading-scope-duration-field"><legend>{T.duration}</legend><div className="reading-scope-duration">
    <div className="reading-scope-slider-heading"><label htmlFor={id+'-years'}>{T.duration_label}</label><output htmlFor={id+'-years'}>{duration} {duration==='1'?T.one_year:T.years}</output></div>
    <input id={id+'-years'} className="reading-scope-range" type="range" min={1} max={15} step={1} value={duration} aria-valuetext={duration+' '+(duration==='1'?T.one_year:T.years)} aria-describedby={id+'-duration-hint'} style={{'--reading-progress':((Number(duration)-1)/14*100)+'%'} as CSSProperties} onChange={event=>{setDuration(event.target.value);setError('');}}/>
    <div className="reading-scope-range-bounds" aria-hidden="true"><span>{1} {T.one_year}</span><span>{15} {T.years}</span></div>
    <div className="reading-scope-presets" role="group" aria-label={T.shortcuts}>{[3,5,7,10,15].map(value=><button type="button" key={value} aria-pressed={duration===String(value)} onClick={()=>{setDuration(String(value));setError('');}}>{value} {T.years}</button>)}</div>
   </div><p id={id+'-duration-hint'}>{T.duration_hint}</p></fieldset>
   {comparative&&<fieldset><legend>{T.options}</legend><p>{T.options_hint}</p><div className="reading-scope-options">{data.ui.essential.active_options.map((key:string)=><label key={key}><input type="checkbox" checked={selected.includes(key)} onChange={()=>{setSelected(current=>current.includes(key)?current.filter(value=>value!==key):[...current,key]);setError('');}}/>{T.option_labels[key]}</label>)}<button type="button" className="text-button" onClick={()=>{setSelected([...data.ui.essential.active_options]);setError('');}}>{T.all_options}</button></div></fieldset>}
   {error&&<p role="alert" id={id+'-error'} className="reading-scope-error">{error}</p>}
   <div className="reading-scope-actions"><button type="submit" className="primary">{T.apply}</button><button type="button" className="secondary" onClick={close}>{T.cancel}</button></div>
  </form>}
 </div>;
}

export function ReadingPeriodNote({route}:{route:EconomicRoute}){
 const {data}=useStudy(),T=data.ui.essential.economic_dossier.reading_scope,origin=readingOrigin(route);
 return <aside className="reading-period-note"><p><b>{T.period_costs}</b> {T.period_notes[origin]}</p>{origin!=='project'&&<p>{T.relative_periods}</p>}</aside>;
}
