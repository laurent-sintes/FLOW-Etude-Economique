import type {ReactNode} from 'react';
import {useStudy,useFormat,type Data} from './context';
import {CostActivityTags} from './ArchitectureLayers';
import {MethodText} from './MethodDocument';
import {SourceLink} from './components';
import {isModelDataReference} from './documentVisibility';
import './framework.css';

const sectionId=(id:string)=>'framework-section-'+id;

function ParameterSection({id,title,lead,children}:{id:string;title:string;lead:string;children:ReactNode}){
 return <li><section className="core-method-section" data-kind="method" aria-labelledby={sectionId(id)}>
  <h2 id={sectionId(id)} tabIndex={-1}>{title}</h2>
  <p className="core-method-lead"><MethodText>{lead}</MethodText></p>
  <div className="core-method-blocks">{children}</div>
 </section></li>;
}

function Formulas({items}:{items:string[]}){
 return <div className="framework-formulas">{items.map(text=><p className="core-method-formula" key={text}>{text}</p>)}</div>;
}

function ParameterTable({caption,children}:{caption:string;children:ReactNode}){
 return <div className="core-method-table-scroll" tabIndex={0} role="region" aria-label={caption}>
  <table className="core-method-table framework-table"><caption>{caption}</caption>{children}</table>
 </div>;
}

function groupByText(rows:Data[],field:string){
 const groups=new Map<string,Data[]>();
 rows.forEach(row=>groups.set(row[field],[...(groups.get(row[field])||[]),row]));
 return [...groups].map(([text,items])=>({text,items}));
}

function ParameterUsage({personal,status}:{personal?:Data;status?:string}){
 const {data}=useStudy(),T=data.ui.essential.framework;
 const kind=personal?.kind||'reference';
 return <p className="framework-usage">
  {status&&<span className={'framework-status is-'+status}>{T.usage_labels[status]}</span>}
  {kind==='reference'?<span>{T.usage_labels.reference}</span>:<a href="#simuler">{T.usage_labels[kind]}{personal?.label&&' · '+personal.label}</a>}
  {personal?.options?.length>0&&<span className="framework-personal-options">{(personal?.options||[]).map((key:string)=>data.baseline.options.find(option=>option.stack===key)?.name).join(' · ')}</span>}
 </p>;
}

function ProofLinks({items}:{items:Data[]}){
 const unique=[...new Map<string,Data>(items.filter(item=>!isModelDataReference(item.path)).map(item=>[item.path,item])).values()];
 if(!unique.length)return null;
 return <ul className="framework-proof-links">{unique.map(item=><li key={item.path}><SourceLink path={item.path}>{item.title}</SourceLink>{item.locator&&<small>{item.locator}</small>}</li>)}</ul>;
}

function ApplicationHypothesis({id}:{id:string}){
 const {data}=useStudy();
 const note=data.ui.essential.application_framework.hypotheses.sections.find((section:Data)=>section.id===id);
 if(!note)throw new Error('ERR_HYPOTHESIS_NOTE');
 return <div className="framework-prose-group"><h3>{note.title}</h3>
  {note.paragraphs.map((text:string,index:number)=><p key={index}><MethodText>{text}</MethodText></p>)}
  {note.links?.map((link:Data)=><SourceLink key={link.href} path={link.href}>{link.label}</SourceLink>)}
 </div>;
}

export function FrameworkPage(){
 const {data}=useStudy(),{dailyRate,n,annualAmount}=useFormat(),T=data.ui.essential.framework,F=data.content.framework;
 const percent=(value:number)=>n(value,1)+'\u00a0%';
 const natures=Object.keys(F.workload.ia.taux_pct[F.tariffs[0].key]);
 const activityAllocations=data.ui.essential.model_rows.filter((row:Data)=>row.activity_allocation);
 const programme=F.pilotage.programme;
 const pilotage=[
  {key:'build_pct',label:T.pilotage_build,base:T.pilotage_build_base},
  {key:'integration_make_pct',label:T.pilotage_integration,base:T.pilotage_integration_base},
  {key:'deployment_pct',label:T.pilotage_deployment,base:T.pilotage_deployment_base},
  {key:'maintenance_pct',label:T.pilotage_maintenance,base:T.pilotage_maintenance_base},
  {key:'complements_buy_pct',label:T.pilotage_buy,base:T.pilotage_buy_base},
 ];
 const families=[
  {id:'gains',title:T.ia_title},{id:'tarifs',title:T.tariffs_title},
  {id:'pilotage',title:T.pilotage_title},{id:'moyens',title:T.other_title},
  {id:'indexation',title:T.inflation_title},{id:'build-run',title:T.activity_allocation_title},
  {id:'diagnostics',title:T.diagnostics_title},
 ];
 const goTo=(id:string)=>{
  const heading=document.getElementById(sectionId(id));
  heading?.focus({preventScroll:true});
  heading?.scrollIntoView({block:'start',behavior:'auto'});
 };
 const price=(option:Data,key:string)=>option.prices.find((item:Data)=>item.key===key);
 const roles=[
  {key:'expert',label:F.roles.developpement.name,note:F.roles.developpement.scope},
  {key:'expert',label:F.roles.integration.name,note:F.roles.integration.scope},
  {key:'qa',label:T.qa,note:T.qa_note},
  {key:'architecte',label:T.architect_title,note:T.architect_note},
 ];
 const contextGroups=groupByText(F.tariffs.map((option:Data)=>({...option,contextKey:JSON.stringify(option.context)})),'contextKey');
 const tariffEvidence=F.tariffs.flatMap((option:Data)=>option.prices.flatMap((row:Data)=>row.evidence));
 const specialist=F.specialist;
 const otherValue=(row:Data)=>row.unit==='annual'?annualAmount(row.value):n(row.value,0)+' '+T['other_unit_'+row.unit];
 const otherCard=(row:Data)=><article className="framework-fact" key={row.key}>
  <header><h3>{T.other_rows[row.key].label}</h3><strong className="framework-value">{otherValue(row)}</strong></header>
  <p><MethodText>{row.method}</MethodText></p>
  <SourceLink path={row.source}>{T.source_method}</SourceLink>
 </article>;
 const retainedMeans=F.other.filter((row:Data)=>row.status==='retained'&&row.unit!=='daily');
 const replacedMeans=F.other.filter((row:Data)=>row.status==='replaced');
 const means=(rows:Data[])=><div className="framework-means">{groupByText(rows,'method').map(group=><article className="framework-means-group" key={group.items.map(row=>row.key).join('-')}>
  <dl className="framework-means-values">{group.items.map(row=><div key={row.key}><dt>{T.other_rows[row.key].label}</dt><dd className="framework-value">{otherValue(row)}</dd></div>)}</dl>
  <p className="framework-source-text"><MethodText>{group.text}</MethodText></p>
  {groupByText(group.items.map(row=>({...row,personalKey:JSON.stringify(row.personal)})),'personalKey').map(usage=><ParameterUsage key={usage.text} personal={usage.items[0].personal} status={usage.items[0].status==='replaced'?'replaced':'active'}/>)}
  <SourceLink path={group.items[0].source}>{T.source_method}</SourceLink>
 </article>)}</div>;
 const optionHeaders=(build=false)=><tr><th scope="col">{T.ia_nature_label}</th>{F.tariffs.map((option:Data)=><th scope="col" key={option.key}>{option.name}{build&&<small>{option.mode==='Make'?T.ia_make_scope:T.ia_buy_scope}</small>}</th>)}</tr>;

 return <div className="essential-page core-method-page framework-page">
  <nav className="core-method-navigation" aria-label={T.navigation_label}>
   <h2>{T.navigation_label}</h2><ol>{families.map(family=><li key={family.id}><button type="button" aria-controls={sectionId(family.id)} onClick={()=>goTo(family.id)}>{family.title}</button></li>)}</ol>
  </nav>
  <section className="core-method-introduction" aria-labelledby="framework-intro-title">
   <div className="core-method-principle"><h2 id="framework-intro-title">{T.intro_title}</h2><p><MethodText>{T.intro_text}</MethodText></p></div>
   <p className="framework-reference"><MethodText>{T.reference_note}</MethodText></p>
   <div className="framework-retained-choices"><h3>{T.choices_title}</h3><ul className="core-method-bullets">{T.choices.map((text:string)=><li key={text}><MethodText>{text}</MethodText></li>)}</ul></div>
   <p className="framework-reference framework-reading-key"><strong>{T.usage_title} : </strong><MethodText>{T.usage_note}</MethodText></p>
  </section>
  <ol className="core-method-sections">
   <ParameterSection id="gains" title={T.ia_title} lead={T.ia_note}>
    <Formulas items={[T.ia_formula]}/>
    <ApplicationHypothesis id="productivity"/>
    <div className="framework-group">
     <ParameterTable caption={T.ia_detail}><thead>{optionHeaders(true)}</thead><tbody>
      {natures.map(key=><tr key={key}><th scope="row">{data.ui.natures[key]}</th>{F.tariffs.map((option:Data)=><td key={option.key}>{percent(F.workload.ia.taux_pct[option.key][key])}</td>)}</tr>)}
     </tbody></ParameterTable>
     <p><strong>{T.ia_frontend} : {percent(F.workload.ia.frontend_pct)}</strong></p>
     <SourceLink path={F.sources.gains}>{T.gains_source}</SourceLink>
    </div>
    <div className="framework-group">
     <p><MethodText>{T.ia_maintenance_note}</MethodText></p>
     <ParameterTable caption={T.ia_maintenance_detail}><thead>{optionHeaders()}</thead><tbody>
      {F.workload.maintenance_ia[F.tariffs[0].key].map((activity:Data)=><tr key={activity.id}><th scope="row">{activity.label}</th>
       {F.tariffs.map((option:Data)=>{const row=F.workload.maintenance_ia[option.key].find((entry:Data)=>entry.id===activity.id);
        return <td key={option.key}>{row.traitement==='estimation'?percent(row.taux_pct):<><strong className="framework-treatment">{T.ia_treatments[row.traitement]}</strong><small>{T.ia_diagnostic} : {percent(row.taux_pct)}</small></>}</td>;
       })}
      </tr>)}
     </tbody></ParameterTable>
     {F.sources.annual_gains.some((row:Data)=>!isModelDataReference(row.path))&&<div className="framework-reading-sources"><h3>{T.annual_gains_sources}</h3><ProofLinks items={F.sources.annual_gains.map((row:Data)=>({path:row.path,title:F.tariffs.find((option:Data)=>option.key===row.key).name}))}/></div>}
    </div>
   </ParameterSection>

   <ParameterSection id="tarifs" title={T.tariffs_title} lead={T.tariffs_note}>
    <ParameterTable caption={T.tariffs_caption}><thead><tr><th scope="col">{T.tariff_profile}</th>{F.tariffs.map((option:Data)=><th scope="col" key={option.key}>{option.name}</th>)}</tr></thead>
     <tbody>{roles.map(role=><tr key={role.label}><th scope="row">{role.label}</th>{F.tariffs.map((option:Data)=><td className="framework-price" key={option.key}>{dailyRate(price(option,role.key).value)}</td>)}</tr>)}</tbody>
    </ParameterTable>
    <Formulas items={T.tariff_formulas}/>
    <div className="framework-prose-group framework-tariff-context"><h3>{T.tariff_context_title}</h3>{contextGroups.map(group=>{
     const context=group.items[0].context;
     return <div key={group.text}>{contextGroups.length>1&&<h4>{group.items.map(option=>option.name).join(' · ')}</h4>}
      <p><strong>{T.tariff_market} : {context.market}. {T.tariff_purchase_mode} : {data.ui.reading.purchase_modes[context.purchase_mode]}.</strong></p>
      <p>{context.profile}</p><p>{context.geography}</p>
     </div>;
    })}</div>
    <p><MethodText>{T.tariff_scope}</MethodText></p>
    <p><MethodText>{T.tariff_influence}</MethodText></p>
    <ul className="core-method-bullets">{roles.map(role=>role.note&&<li key={role.label}><strong>{role.label} : </strong><MethodText>{role.note}</MethodText></li>)}</ul>
    <div className="framework-prose-group"><h3>{T.tariff_rules_title}</h3>
     <dl className="framework-text-list">{groupByText(F.tariffs,'rule').map(group=><div key={group.text}><dt>{group.items.map(option=>option.name).join(' · ')}</dt><dd><MethodText>{group.text}</MethodText></dd></div>)}</dl>
    </div>
    <div className="framework-prose-group"><h3>{T.tariff_methods_title}</h3>
     <div className="framework-tariff-profiles">{[{key:'expert',label:T.expert},{key:'qa',label:T.qa},{key:'architecte',label:T.architect_title}].map(profile=><section key={profile.key} className="framework-tariff-profile">
      <h4>{profile.label}</h4><dl className="framework-tariff-methods">{groupByText(F.tariffs.map((option:Data)=>({...option,method:price(option,profile.key).method})),'method').map(group=><div key={group.text}>
       <dt>{group.items.map(option=>option.name).join(' · ')}</dt><dd><MethodText>{group.text}</MethodText></dd>
      </div>)}</dl>
     </section>)}</div>
     <p><MethodText>{T.tariff_secondary_note}</MethodText></p>
     <ProofLinks items={tariffEvidence}/>
    </div>
    <div className="framework-prose-group framework-limit"><h3>{T.limits}</h3>
     <dl className="framework-text-list">{groupByText(F.tariffs,'limit').map(group=><div key={group.text}><dt>{group.items.map(option=>option.name).join(' · ')}</dt><dd><MethodText>{group.text}</MethodText></dd></div>)}</dl>
    </div>
    <div className="framework-facts">
     {F.other.filter((row:Data)=>row.status==='retained'&&row.unit==='daily').map(otherCard)}
     {[{key:'frontend',title:T.frontend_title,note:T.frontend_note},{key:'support',title:T.support_title,note:T.support_note}].map(row=><article className="framework-fact" key={row.key}>
      <header><h3>{row.title}</h3><strong className="framework-value">{dailyRate(F[row.key].value)}</strong></header>
      <p><MethodText>{F[row.key].method}</MethodText></p><SourceLink path={F[row.key].source}>{T.source_method}</SourceLink>
     </article>)}
    </div>
    <div className="framework-specialist"><h3>{T.specialist_title}</h3>
     <ApplicationHypothesis id="annual_expertise"/>
     <p className="framework-specialist-ceiling"><strong>{T.specialist_ceiling}</strong><span className="framework-value">{n(specialist.plafond_jh_avant_sensibilite,0)} {T.specialist_unit}</span></p>
     <div className="framework-factors"><h4>{T.specialist_factors_title}</h4><dl>{Object.entries(specialist.factors_jh).map(([key,value])=><div key={key}><dt>{T.specialist_scenarios[key]}</dt><dd>× {n(value as number,2)}</dd></div>)}</dl></div>
     <Formulas items={[T.specialist_formula]}/>
     <p><MethodText>{T.specialist_factor_note}</MethodText></p>
     {[specialist.source,specialist.sensitivity_source].some(path=>!isModelDataReference(path))&&<div className="framework-reading-sources"><SourceLink path={specialist.source}>{T.specialist_method}</SourceLink><SourceLink path={specialist.sensitivity_source}>{T.specialist_sensitivity}</SourceLink></div>}
    </div>
   </ParameterSection>

   <ParameterSection id="pilotage" title={T.pilotage_title} lead={T.pilotage_note}>
    <Formulas items={[T.pilotage_formula]}/>
    <p><MethodText>{T.pilotage_scope}</MethodText></p>
    <ParameterTable caption={T.pilotage_caption}><thead><tr>{T.pilotage_columns.map((label:string)=><th scope="col" key={label}>{label}</th>)}</tr></thead><tbody>{pilotage.map(row=><tr key={row.key}>
     <th scope="row">{row.label}</th><td className="framework-price">{percent(row.key==='deployment_pct'?F.pilotage.deployment_pct:F.pilotage.rates[row.key])}</td><td><MethodText>{row.base}</MethodText></td>
    </tr>)}</tbody></ParameterTable>
    <ApplicationHypothesis id="coordination"/>
    {[F.sources.coordination,F.sources.deployment].some(path=>!isModelDataReference(path))&&<div className="framework-reading-sources"><SourceLink path={F.sources.coordination}>{T.coordination_source}</SourceLink><SourceLink path={F.sources.deployment}>{T.deployment_source}</SourceLink></div>}
    <div className="framework-programme">
     <h3>{T.pilotage_programme_title}</h3>
     <Formulas items={T.programme_formulas}/>
     <p><strong>{T.pilotage_duration} : {programme.duree_mois} {T.pilotage_months}</strong></p>
     <ParameterTable caption={T.programme_caption}><thead><tr>{T.programme_columns.map((label:string)=><th scope="col" key={label}>{label}</th>)}</tr></thead>
      <tbody>{[{key:'direction',label:T.pilotage_direction},{key:'coordination',label:T.pilotage_coordination}].map(role=><tr key={role.key}>
       <th scope="row">{role.label}</th><td>{n(programme[role.key+'_jh_par_mois'],1)}</td><td>{n(programme[role.key+'_jh'],1)}</td><td>{dailyRate(programme['tarif_'+role.key+'_eur_jh'])}</td>
      </tr>)}</tbody>
     </ParameterTable>
     <p><MethodText>{programme.choix}</MethodText></p><p><MethodText>{programme.distinction}</MethodText></p>
     <SourceLink path={F.sources.programme}>{T.programme_source}</SourceLink>
    </div>
   </ParameterSection>

   <ParameterSection id="moyens" title={T.other_title} lead={T.other_note}>
    <ApplicationHypothesis id="annual_means"/>
    <Formulas items={[T.other_formula]}/>
    <p><MethodText>{T.other_scope}</MethodText></p>
    <div className="framework-prose-group"><h3>{T.other_action}</h3>{means(retainedMeans)}</div>
   </ParameterSection>

   <ParameterSection id="indexation" title={T.inflation_title} lead={T.inflation_note}>
    <ApplicationHypothesis id="offer_sequences"/>
    <Formulas items={T.inflation_formulas}/>
    <p><MethodText>{T.inflation_scope}</MethodText></p>
    <div className="framework-facts">{F.inflation.map((row:Data)=><article key={row.key} className="framework-fact">
     <header><h3>{row.label}</h3><strong className="framework-value">{percent(row.value*100)}</strong></header>
     <ParameterUsage personal={row.personal} status="active"/>
     <p><MethodText>{T.inflation_summaries[row.key]}</MethodText></p>
     <SourceLink path={row.source}>{T.source_method}</SourceLink><ProofLinks items={row.evidence}/>
    </article>)}</div>
   </ParameterSection>

   <ParameterSection id="build-run" title={T.activity_allocation_title} lead={T.activity_allocation_note}>
    <Formulas items={[T.activity_formula]}/>
    <div className="framework-activity-allocations">{activityAllocations.map((row:Data)=><article className="framework-fact" key={row.key}>
     <h3>{row.title}</h3><CostActivityTags tags={row.activity_tags} allocation={row.activity_allocation}/><p>{row.activity_allocation.basis}</p>
    </article>)}</div>
    <p><MethodText>{T.activity_scope}</MethodText></p>
    <SourceLink path={F.sources.allocation}>{T.allocation_source}</SourceLink>
   </ParameterSection>
   <ParameterSection id="diagnostics" title={T.diagnostics_title} lead={T.diagnostics_note}>
    <div className="framework-group framework-diagnostic">
     <ParameterUsage status="diagnostic"/>
     <ParameterTable caption={T.ia_integration_detail}><thead>{optionHeaders()}</thead><tbody><tr><th scope="row">{T.ia_integration}</th>{F.tariffs.map((option:Data)=><td key={option.key}>{percent(F.workload.ia.integration_pct[option.key])}</td>)}</tr></tbody></ParameterTable>
     <p><MethodText>{T.ia_integration_note}</MethodText></p><SourceLink path={F.sources.gains}>{T.gains_source}</SourceLink>
    </div>
    {replacedMeans.length>0&&<div className="framework-prose-group framework-diagnostic"><h3>{T.other_replaced_title}</h3>
     <p><MethodText>{T.other_replaced_note}</MethodText></p>{means(replacedMeans)}
    </div>}
   </ParameterSection>
  </ol>
  <div className="framework-links">{T.method_links.map((link:Data)=><a key={link.href} href={link.href}>{link.label}</a>)}<a className="text-button" href="#simuler">{T.simulate_action} →</a></div>
  <a className="text-button essential-structure-next" href="#evaluation-core">{T.next} →</a>
 </div>;
}
