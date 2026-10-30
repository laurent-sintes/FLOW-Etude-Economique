import {useStudy,useFormat,type Option,type Data} from './context';
import {SourceLink} from './components';
import {TableViewport} from './TableViewport';

export function FundingValue({option,kind,value,annual=false}:{option:Option;kind:string;value:number;annual?:boolean}){
 const {data}=useStudy(),{amount,annualAmount}=useFormat();
 const bundled=option.mode==='Buy'&&['core_lifecycle','mco_client','client_evolutions'].includes(kind)&&value===0;
 return bundled?<span className="parameter-readonly">{data.ui.composable.included}</span>:<>{annual?annualAmount(value):amount(value)}</>;
}

export function FundingTable({options,values,annual=false}:{options:Option[];values:(option:Option)=>Record<string,number>;annual?:boolean}){
 const {data}=useStudy(),C=data.ui.composable;
 const hasBuy=options.some(o=>o.mode==='Buy');
 const rows=C.rows.filter((row:Data)=>(!annual||row.key!=='integration_client')&&(hasBuy||row.key!=='grouped_buy'));
 return <><p className="journey-note">{annual?C.annual_note:C.note}</p><TableViewport title={annual?C.annual_title:C.title}>
  <table className="simulation-breakdown"><thead><tr><th>{annual?C.annual_title:C.title}<small>{annual?data.ui.labels.annual_money_unit:data.ui.labels.money_unit}</small></th>{options.map(o=><th key={o.stack} scope="col">{o.name}</th>)}</tr></thead>
   <tbody>{rows.map((row:Data)=><tr key={row.key}><th scope="row">{annual&&row.annual_label||row.label}{row.key==='run'&&hasBuy&&<small>{C.outside_bundle}</small>}</th>{options.map(o=><td key={o.stack}><FundingValue option={o} kind={row.key} value={values(o)[row.key]||0} annual={annual}/></td>)}</tr>)}</tbody>
  </table></TableViewport><SourceLink path={C.source}/></>;
}
