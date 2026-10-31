import {useStudy,type Data} from './context';
import {MethodText,MethodReferenceCards} from './MethodDocument';
export function FrameworkMakeAudit({plan}:{plan:Data}){
 const {data}=useStudy(),L=data.ui.essential.framework_vision.journey.labels,M=data.ui.essential.estimation_model;
 const method=data.ui.essential[plan.method];
 const referenceSection=method.sections.find((section:Data)=>section.id==='observer-fonctions');
 const references=(referenceSection?[referenceSection]:[]).flatMap((section:Data)=>section.blocks.filter((block:Data)=>block.kind==='reference_cards'));
 return <section className="make-audit" aria-labelledby="make-audit-heading"><h3 id="make-audit-heading">{plan.title}</h3><p><MethodText>{plan.intro}</MethodText></p>
  <ol className="make-audit-steps">{plan.steps.map((step:Data)=><li key={step.title}><h4>{step.title}</h4><p><MethodText>{step.text}</MethodText></p>
   {step.rule_refs.includes('prepare_size')&&referenceSection&&<p><MethodText>{referenceSection.lead}</MethodText></p>}
   {step.rule_refs.includes('prepare_size')&&references.map((block:Data,index:number)=><MethodReferenceCards key={index} cards={block.cards} headingLevel={5}/>)}
   {step.rule_refs.map((ref:string)=>{const rule=M.rules.find((r:Data)=>r.id===ref),implementations=M.implementations.filter((i:Data)=>i.rules.includes(ref));return <section className="make-rule" data-rule-ref={ref} key={ref}>
    <h5>{rule.title}<span className="make-rule-unit">{rule.unit}</span></h5>
    <pre className="make-formula"><code>{rule.expression}</code></pre>
    {rule.variables&&Object.keys(rule.variables).length>0&&<dl className="make-rule-variables" aria-label={L.variables}>{Object.entries(rule.variables).map(([key,value])=><div key={key}><dt><code>{key}</code></dt><dd>{String(value)}</dd></div>)}</dl>}
    {rule.note&&<p><MethodText>{rule.note}</MethodText></p>}
    <p className="make-rule-provenance"><code>{ref}</code>{' · '+L.implementation+' : '}{implementations.map((i:Data)=><code key={i.path}>{i.path}</code>)}</p>
   </section>;})}
  </li>)}</ol>
  {method.sections.filter((section:Data)=>plan.sections.includes(section.id)).map((section:Data)=><section className="make-method-formulas" key={section.id}><h4>{section.title}</h4>{section.blocks.filter((block:Data)=>block.kind==='formula').map((block:Data)=><p className="make-formula" key={block.text}>{block.text}</p>)}</section>)}
  <nav className="journey-links" aria-label={L.audit}>{plan.links.map((link:Data)=><a className="text-button" href={link.href} key={link.href}>{link.label}</a>)}<a className="text-button" href={import.meta.env.BASE_URL+'exports/flow-modele-metier.yaml'} download="flow-modele-metier.yaml">{data.ui.model_download.label}</a></nav>
 </section>;
}
