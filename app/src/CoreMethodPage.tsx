import {useStudy,type Data} from './context';
import {MethodDocument} from './MethodDocument';

export function CoreMethodPage(){
 const {data}=useStudy();
 const original=data.ui.essential.core_method,link=data.ui.essential.prestudies.method_link;
 const method={...original,sections:original.sections.map((section:Data)=>({...section,blocks:section.blocks.map((block:Data)=>section.id==='observer-fonctions'&&block.kind==='reference_cards'?{kind:'links',items:[link]}:block)}))};
 return <MethodDocument method={method} prefix="core-method"/>;
}

export function NetCalculationPage(){
 const {data}=useStudy();
 return <MethodDocument method={data.ui.essential.net_method} prefix="net-method"/>;
}

export function RunCalculationPage(){
 const {data}=useStudy();
 return <MethodDocument method={data.ui.essential.run_method} prefix="run-method"/>;
}
