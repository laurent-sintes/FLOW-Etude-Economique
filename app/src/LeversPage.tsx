import {useStudy} from './context';
import {MethodDocument} from './MethodDocument';

export function LeversPage(){
 const {data}=useStudy();
 return <MethodDocument method={data.ui.essential.levers_method} prefix="levers" className="levers-page"/>;
}
