import type {ReactNode} from 'react';
import {Hammer,ShoppingCart,Boxes,Cloud,Layers3,CalendarClock,ChartNoAxesCombined,type LucideIcon} from 'lucide-react';
import {useStudy,type Data} from './context';
import {SourceLink} from './components';
import {MethodText} from './MethodDocument';
import {GlossaryText} from './GlossaryText';
import {ModelMap} from './ModelMap';
import {CostActivityTags,costStructureIcons} from './ArchitectureLayers';
import './modelReading.css';

const icons:Record<string,LucideIcon>={make:Hammer,buy:ShoppingCart,programme:Layers3,product:Boxes,platform:Cloud,...costStructureIcons,calendar:CalendarClock,service:ChartNoAxesCombined};
const sectionId=(id:string)=>`model-chapter-${id}`;
const Text=({children,className=''}:{children:string;className?:string})=><p className={className}><MethodText>{children}</MethodText></p>;

export function ModelPage(){
 const {data}=useStudy(),E=data.ui.essential,R=E.model_reading;
 const goToSection=(id:string)=>{
  const heading=document.getElementById(sectionId(id));
  heading?.focus({preventScroll:true});
  heading?.scrollIntoView({block:'start',behavior:'auto'});
 };
 const links=(items:Data[])=><div className="model-reading-links">{items.map(link=>link.href.startsWith('source/')?<SourceLink path={link.href} key={link.href}>{link.label}</SourceLink>:<a className="text-button" href={link.href} key={link.href}>{link.label} <span aria-hidden="true">→</span></a>)}</div>;
 const content:Record<string,ReactNode>={
  scope:<>
   <div className="model-reading-concepts">{E.concepts.map((concept:Data)=>{const Icon=icons[concept.icon],term=data.glossary.notions[concept.notion];return <article key={concept.notion}><Icon aria-hidden="true" size={22}/><h3><GlossaryText>{term.libelle}</GlossaryText></h3><Text>{concept.text}</Text></article>;})}</div>
   <Text className="model-reading-composition">{R.composition}</Text>
   <Text>{R.scope}</Text>
   <ModelMap/>
  </>,
  strategies:<>
   <div className="model-reading-strategies">{E.choices.map((choice:Data)=>{const Icon=icons[choice.icon];return <article key={choice.title}><div className="model-reading-card-title"><Icon aria-hidden="true" size={24}/><h3>{choice.title}</h3></div><Text>{choice.text}</Text></article>;})}</div>
   <Text className="model-reading-callout">{R.strategy_note}</Text>
   {links(R.strategy_links)}
  </>,
  activities:<>
   <dl className="model-reading-activities">{E.model_activities.types.map((type:Data)=><div key={type.id} className={'model-reading-activity-'+type.id}><dt><GlossaryText>{type.label}</GlossaryText></dt><dd><MethodText>{type.text}</MethodText></dd></div>)}</dl>
   <Text className="model-reading-callout">{R.activity_note}</Text>
  </>,
  workload:<>
   <div className="model-reading-workloads">{E.model_workload.stages.map((stage:Data)=>{const term=data.glossary.notions[stage.notion];return <article key={stage.id}><h3><GlossaryText>{term.libelle}</GlossaryText></h3><p className="model-reading-producer">{stage.producer}</p><Text>{stage.text}</Text></article>;})}</div>
   <div className="model-reading-relations">{E.model_workload.relations.map((relation:Data)=><Text key={relation.operation}>{relation.text}</Text>)}</div>
   <Text className="model-reading-callout">{R.workload_note}</Text>
   {links(E.model_workload.links)}
   <section className="model-estimation-rules"><h3>{E.estimation_model.title}</h3><Text>{E.estimation_model.purpose}</Text>
    {E.estimation_model.rules.map((rule:Data)=><article key={rule.id}><h4>{rule.title}</h4><p className="core-method-formula">{rule.expression} · {rule.unit}</p>
     <dl>{Object.entries(rule.variables).map(([key,value])=><div key={key}><dt>{key}</dt><dd>{String(value)}</dd></div>)}</dl>{rule.note&&<Text>{rule.note}</Text>}</article>)}
    <ul>{E.estimation_model.invariants.map((text:string)=><li key={text}><MethodText>{text}</MethodText></li>)}</ul>
   </section>
  </>,
  costs:<>
   <Text>{R.costs_intro}</Text>
   <div className="model-reading-costs">{E.model_rows.map((row:Data)=>{const Icon=costStructureIcons[row.icon],block=E.model_architecture.blocks.find((item:Data)=>item.cost===row.key),layers=block.layers.map((id:string)=>E.model_architecture.layers.find((layer:Data)=>layer.id===id).label);return <article key={row.key} data-cost={row.key}>
    <div className="model-reading-cost-name"><Icon aria-hidden="true" size={21}/><h3>{row.title}</h3></div>
    <div className="model-reading-cost-body">{row.text&&<Text>{row.text}</Text>}{row.bullets&&<ul>{row.bullets.map((text:string)=><li key={text}><MethodText>{text}</MethodText></li>)}</ul>}<CostActivityTags tags={row.activity_tags}/><p className="model-reading-coverage"><span>{R.coverage_label} : </span>{layers.join(' · ')}</p>{block.scope_note&&<Text className="model-reading-coverage">{block.scope_note}</Text>}</div>
   </article>;})}</div>
   <Text className="model-reading-callout">{R.costs_note}</Text>
  </>,
  calendar:<>
   <div className="model-reading-calendar">{E.calendar.map((step:Data)=>{const Icon=icons[step.icon];return <article key={step.title}><Icon aria-hidden="true" size={22}/><h3>{step.title}</h3>{step.text&&<Text>{step.text}</Text>}{step.bullets&&<ul>{step.bullets.map((item:string)=><li key={item}><MethodText>{item}</MethodText></li>)}</ul>}</article>;})}</div>
   <Text className="model-reading-callout">{E.calendar_text}</Text>
   <Text className="model-reading-limit">{E.model_limit}</Text>
  </>
 };
 return <div className="essential-page essential-model model-reading">
  <section className="model-download"><a className="text-button" href={import.meta.env.BASE_URL+'exports/flow-modele-metier.yaml'} download="flow-modele-metier.yaml">{data.ui.model_download.label}</a><Text>{data.ui.model_download.description}</Text></section>
  <nav className="model-reading-navigation" aria-label={R.toc_label}><h2>{R.toc_label}</h2><ol>{R.chapters.map((chapter:Data)=><li key={chapter.id}><button type="button" aria-controls={sectionId(chapter.id)} onClick={()=>goToSection(chapter.id)}>{chapter.title}</button></li>)}</ol></nav>
  {R.chapters.map((chapter:Data,index:number)=><section className="model-reading-chapter" key={chapter.id} data-chapter={chapter.id} aria-labelledby={sectionId(chapter.id)}><h2 id={sectionId(chapter.id)} tabIndex={-1}><span aria-hidden="true">{index+1}</span>{chapter.title}</h2><Text className="model-reading-lead">{chapter.lead}</Text>{content[chapter.id]}</section>)}
  <a className="text-button essential-structure-next" href={R.next_href}>{R.next_label} <span aria-hidden="true">→</span></a>
 </div>;
}
