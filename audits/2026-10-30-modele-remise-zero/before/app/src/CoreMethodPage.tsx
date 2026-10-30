import {useStudy} from './context';
import {MethodDocument} from './MethodDocument';

export function CoreMethodPage(){
 const {data}=useStudy();
 return <MethodDocument method={data.ui.essential.core_method} prefix="core-method"/>;
}

export function NetCalculationPage(){
 const {data}=useStudy();
 return <MethodDocument method={data.ui.essential.net_method} prefix="net-method"/>;
}

export function RunCalculationPage(){
 const {data}=useStudy();
 return <MethodDocument method={data.ui.essential.run_method} prefix="run-method"/>;
}
