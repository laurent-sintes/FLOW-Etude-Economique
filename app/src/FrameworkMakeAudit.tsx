import {useStudy,type Data} from './context';
import {SourceLink} from './components';
import {MethodText} from './MethodDocument';
export function FrameworkMakeAudit({plan,technical=false}:{plan:Data;technical?:boolean}){
 const {data}=useStudy(),L=data.ui.essential.framework_vision.journey.labels,M=data.ui.essential.estimation_model;
 const method=data.ui.essential[plan.method];
 const mapping=plan.mapping;
 if(mapping&&!technical){
  const E=mapping.example,R=E.resolved;
  return <section className="make-audit make-mapping" aria-labelledby="make-mapping-title">
   <h3 id="make-mapping-title">{mapping.title}</h3>
   <p><MethodText>{mapping.intro}</MethodText></p>
   <ol className="make-audit-steps">{mapping.steps.map((step:Data)=><li key={step.title}><h4>{step.title}</h4><p><MethodText>{step.text}</MethodText></p></li>)}</ol>
   <p className="make-mapping-relation"><MethodText>{mapping.relation}</MethodText></p>
   <section className="journey-example make-mapping-example">
    <h4>{E.title}</h4>
    <ol>
     <li><strong>{E.capability_label}</strong><p>{R.capability.label} · {R.capability.id}</p><p>{R.capability.definition}</p></li>
     <li><strong>{E.function_label}</strong><p>{R.function.resultat}</p><code>{R.function.id}</code></li>
     <li><strong>{E.feature_label}</strong><p>{R.feature.label} · {R.feature.id}</p><p>{R.feature.outcome}</p></li>
     <li><strong>{E.code_label}</strong>{R.references.map((reference:Data)=><section key={reference.title}>
      <h5>{reference.title}</h5>
      <ul>{reference.files.map((file:Data)=><li key={file.path}><SourceLink path={file.url}><code>{file.path}</code></SourceLink></li>)}</ul>
      <small><code>{reference.revision}</code></small>
     </section>)}</li>
     <li><strong>{E.boundary_label}</strong><p>{R.feature.boundary}</p></li>
    </ol>
   </section>
   <h4>{mapping.estimation.title}</h4><p><MethodText>{mapping.estimation.text}</MethodText></p>
   <h4>{mapping.roles.title}</h4><p><MethodText>{mapping.roles.text}</MethodText></p>
   <p><a className="text-button make-mapping-roles" href={mapping.roles.href}>{mapping.roles.label} →</a></p>
   <a className="text-button make-mapping-appendix" href={mapping.appendix.href}>{mapping.appendix.label} →</a>
  </section>;
 }
 return <section className="make-audit" aria-labelledby="make-audit-heading"><h3 id="make-audit-heading">{plan.title}</h3><p><MethodText>{plan.intro}</MethodText></p>
  <ol className="make-audit-steps">{plan.steps.map((step:Data)=><li key={step.title}><h4>{step.title}</h4><p><MethodText>{step.text}</MethodText></p>
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
