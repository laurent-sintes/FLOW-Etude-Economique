import {useStudy} from './context';
import {MethodDocument} from './MethodDocument';
import './marketMethod.css';

export function MarketMethodPage(){
 const {data}=useStudy(),T=data.ui.essential.market_method;
 return <MethodDocument method={T.document} prefix="market-method" className="market-method-page">
  <p className="market-method-application"><a className="text-button" href={T.application.href}>{T.application.label} <span aria-hidden="true">→</span></a></p>
 </MethodDocument>;
}
