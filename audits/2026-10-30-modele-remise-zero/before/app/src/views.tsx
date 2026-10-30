import {TableViewport} from './TableViewport';
import {GlossaryText} from './GlossaryText';
import {useEffect,useRef} from 'react';

import {useStudy,useFormat,type Data} from './context';
import {Section,SourceLink} from './components';
import {Architecture,EconomicResponsibilities,EconomicCosts} from './StudyReading';
import {BusinessMap} from './BusinessMap';
import {BusinessCalibration} from './BusinessCalibration';
import {IntegrationEstimates} from './IntegrationEstimates';
import {StrategyComparison} from './SponsorDecision';
import {useReadingState} from './readerNavigation';

export function Perimetres(){
 const {data}=useStudy();const {ui,content,baseline}=data;const state=useReadingState();
 const section=ui.perimeter_sections.some((s:Data)=>s.id===state.get('section'))?state.get('section'):'coverage';
 const stack=content.stacks[state.get('stack')]?state.get('stack'):baseline.options[0].stack;
 return <><div className="study-tabs">{ui.perimeter_sections.map((item:Data)=><button key={item.id} className={section===item.id?'active':''} aria-pressed={section===item.id} onClick={()=>state.set({section:item.id,capability:''},true)}>{item.label}</button>)}</div>
 {section==='coverage'&&<BusinessMap/>}
 {section==='decision'&&<StrategyComparison/>}
 {section==='economics'&&<EconomicResponsibilities/>}
 {section==='architecture'&&<Architecture stack={stack} onSelect={stack=>state.set({stack},true)}/>}
 </>;
}
export function Estimations({focusOnly=false}:{focusOnly?:boolean}){
 const {data}=useStudy();const {ui,content,baseline}=data;const L=ui.labels,R=ui.estimation_reading;const {amount,n}=useFormat();const state=useReadingState();
 const section=ui.estimation_sections.some((s:Data)=>s.id===state.get('section'))?state.get('section'):'build';
 const focus=state.get('focus');const options=baseline.options.filter(o=>o.mode==='Make');const previousSection=useRef(section);
 const sectionHref=(id:string)=>{const params=new URLSearchParams(location.hash.split('?')[1]);params.set('section',section);params.set('focus',id);return '#estimations?'+params;};
 useEffect(()=>{
  const changed=previousSection.current!==section;previousSection.current=section;
  if(!focus&&!changed)return;
  let arrival=0;
  const layout=requestAnimationFrame(()=>{arrival=requestAnimationFrame(()=>{
   const target=focus?document.getElementById('estimate-'+section+'-'+focus):null;
   if(target){
    if(!document.querySelector('dialog[open]')){target.tabIndex=-1;target.focus({preventScroll:true});}
    target.scrollIntoView({block:'start'});
   }else window.scrollTo(0,0);
  });});
  return()=>{cancelAnimationFrame(layout);cancelAnimationFrame(arrival);};
 },[section,focus]);
 return <>{!focusOnly&&<div className="study-tabs">{ui.estimation_sections.map((s:Data)=><button key={s.id} className={section===s.id?'active':''} aria-pressed={section===s.id} onClick={()=>state.set({section:s.id,focus:''},true)}>{s.label}</button>)}</div>}
 {R.sections[section]&&<nav className="estimation-contents" aria-label={R.navigation}>{R.sections[section].filter((item:Data)=>!focusOnly||item.id!=='work').map((item:Data)=><a key={item.id} href={sectionHref(item.id)} aria-current={focus===item.id?'location':undefined}>{item.label}</a>)}</nav>}
 {section==='build'&&<>
 {(!focusOnly||focus==='budget')&&<div id="estimate-build-budget" className="estimation-anchor"><Section title={L.sensitivity} description={ui.pages.estimations.sensitivity_note}><TableViewport title={L.sensitivity}><table className="estimate-budget-table"><thead><tr><th>{L.option}</th>{[L.low,L.central,L.high].map(label=><th key={label}>{label}<small>{L.money_unit}</small></th>)}</tr></thead><tbody>{options.map(o=>{const e=content.stacks[o.stack].economic;return <tr key={o.stack}><th>{o.name}</th><td>{amount(e.sensibilite_eur_ht.bas.build_core)}</td><td><strong>{amount(o.build)}</strong></td><td>{amount(e.sensibilite_eur_ht.haut.build_core)}</td></tr>;})}</tbody></table></TableViewport></Section></div>}
 {(!focusOnly||focus!=='budget')&&<div id="estimate-build-method" className="estimation-anchor"><Section title={ui.editorial.assumptions_detail}><p>{data.content.journey.build.method_note}</p><div className="reading-next"><a href={'#market?detail=references&section=rates&stack='+encodeURIComponent(state.get('stack'))}>{R.rates_link}<span>→</span></a><a href={'#build?detail=architecture&stack='+encodeURIComponent(state.get('stack'))}>{R.architecture_link}<span>→</span></a></div><h3>{L.ia}</h3><p>{content.calibration.ia.nature}</p><TableViewport title={L.ia}><table className="estimate-budget-table"><thead><tr><th>{L.role}</th>{options.map(o=><th key={o.stack}>{o.name}<small>{L.percent_unit}</small></th>)}</tr></thead><tbody>{[...Object.keys(content.calibration.ia.taux_pct[options[0].stack]),'frontend'].map(key=><tr key={key}><th>{ui.natures[key]||L[key]}</th>{options.map(o=><td key={o.stack}>{n(key==='frontend'?content.calibration.ia.frontend_pct:content.calibration.ia.taux_pct[o.stack][key],0)}</td>)}</tr>)}</tbody></table></TableViewport><p className="small-prose">{content.calibration.ia.justification}</p><SourceLink path="source/calibration-couts.yaml#ia"/></Section></div>}
 {!focusOnly&&<div id="estimate-build-work" className="estimation-anchor"><BusinessCalibration/></div>}
 </>}
 {section==='integration'&&<IntegrationEstimates/>}
 {section==='annual'&&<EconomicCosts/>}
 {!focusOnly&&<div className="section-source"><SourceLink path="source/README.md">{ui.reading.method_link}</SourceLink></div>}</>;
}

