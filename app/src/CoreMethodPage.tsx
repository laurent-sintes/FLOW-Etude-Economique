import {useStudy,type Data} from './context';
import {useDossierFocus} from './Dossier';
import {FrameworkMakeAudit} from './FrameworkMakeAudit';
import {MethodDocument} from './MethodDocument';

export function CoreMethodPage({focus}:{focus?:string}){
 useDossierFocus(focus==='formules'?'core-method-section-calculs-reproductibles':focus==='roles'?'core-method-section-repartir-roles':undefined);
 const {data}=useStudy();
 const original=data.ui.essential.core_method,link=data.ui.essential.prestudies.method_link;
 const method={...original,sections:original.sections.map((section:Data)=>({...section,blocks:section.blocks.map((block:Data)=>section.id==='observer-fonctions'&&block.kind==='reference_cards'?{kind:'links',items:[link]}:block)}))};
 const plan=data.ui.essential.framework_vision.journey.phases[0].make_audit;
 return <MethodDocument method={method} prefix="core-method" additionalSections={[{id:'calculs-reproductibles',title:plan.title}]}>
  <section id="core-method-section-calculs-reproductibles" tabIndex={-1}>
   <FrameworkMakeAudit plan={plan} technical/>
   <a className="text-button" href="#acquisition?option=java-spring&focus=method">{plan.mapping?.return_label||data.ui.essential.pages.acquisition.title} →</a>
  </section>
 </MethodDocument>;
}

export function NetCalculationPage(){
 const {data}=useStudy();
 return <MethodDocument method={data.ui.essential.net_method} prefix="net-method"/>;
}

export function RunCalculationPage(){
 const {data}=useStudy();
 return <MethodDocument method={data.ui.essential.run_method} prefix="run-method"/>;
}
