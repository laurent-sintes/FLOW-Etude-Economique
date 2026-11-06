import {useState,type CSSProperties} from 'react';
import {ChartNoAxesCombined,Users,Network,Layers,Info} from 'lucide-react';
import {useStudy,useFormat,type Data} from './context';
import {Drawer} from './components';
import './chargeDistribution.css';

export function ChargeDistribution(){
 const {data}=useStudy(),{n}=useFormat(),W=data.content.delivery_organisation.charge_dossier,S=W.distribution,L=W.labels.distribution;
 const [detail,setDetail]=useState<string|null>(null),[dismissed,setDismissed]=useState<string|null>(null);
 const pct=(v:number)=>n(v,1)+' %',days=(v:number)=>n(v,Math.abs(v-Math.round(v))<1e-7?0:1)+' JH';
 const titles:Record<string,React.ReactNode>={functions:<ChartNoAxesCombined/>,roles:<Users/>,team_types:<Network/>,purposes:<Layers/>};
 const heading=(id:string)=><header><h2>{titles[id]}{L[id]}</h2><span className="charge-information" onMouseLeave={()=>setDismissed(null)}><button type="button" className="distribution-info" aria-describedby={'distribution-info-'+id} aria-label={L.details+' · '+L[id]} onFocus={()=>setDismissed(null)} onKeyDown={event=>{if(event.key==='Escape')setDismissed(id);}} onClick={()=>setDetail(id)}><Info size={18}/></button><span id={'distribution-info-'+id} role="tooltip" hidden={dismissed===id}>{L[id+'_info']}</span></span></header>;
 const bars=(id:string,rows:Data[])=><ol className="distribution-bars">{rows.map(row=><li key={row.id} data-distribution-item={row.id}>
  <div className="distribution-bar-label">{id==='functions'?<a href={'#charges-acquisition?option=java-spring&focus='+encodeURIComponent(row.id)}>{row.label}</a>:<span>{row.label}</span>}<span className="distribution-value"><strong>{days(row.jh)}</strong><span>{pct(row.share_pct)}</span></span></div>
  <div className="distribution-track" aria-hidden="true"><span style={{width:row.bar_pct+'%'}}/></div>
 </li>)}</ol>;
 const purposes=S.purposes.map((row:Data)=>({...row,color:row.id==='core-domain'?'#236159':'#C24F00'}));
 const legend=(rows:Data[])=><ul className="distribution-legend">{rows.map(row=><li key={row.id} data-distribution-item={row.id}><span className="distribution-swatch" style={{background:row.color}} aria-hidden="true"/><span>{row.label}</span><span className="distribution-value"><strong>{days(row.jh)}</strong><span>{pct(row.share_pct)}</span></span></li>)}</ul>;
 return <div className="charge-distribution">
  <div className="distribution-summary"><span>{L.scope}</span><strong>{days(S.total_jh)}</strong></div>
  <div className="distribution-grid">
   <section className="distribution-panel distribution-functions" data-distribution="functions">{heading('functions')}<p className="distribution-insight">{L.concentration.replace('{share}',pct(S.top_two_pct))}</p>{bars('functions',S.functions)}</section>
   <section className="distribution-panel distribution-roles" data-distribution="roles">{heading('roles')}{bars('roles',S.roles)}</section>
   <section className="distribution-panel" data-distribution="team_types">{heading('team_types')}<div className="distribution-donut-layout"><div className="distribution-donut">
    <svg viewBox="0 0 120 120" aria-hidden="true">{S.team_types.map((row:Data)=><circle key={row.id} cx="60" cy="60" r="46" pathLength="100" fill="none" stroke={row.color} strokeWidth="19" strokeDasharray={`${row.share_pct} ${100-row.share_pct}`} strokeDashoffset={-row.offset_pct} transform="rotate(-90 60 60)"/>)}</svg>
    <div><strong>{n(S.total_jh,0)}</strong><span>{L.unit}</span></div>
   </div>{legend(S.team_types)}</div></section>
   <section className="distribution-panel" data-distribution="purposes">{heading('purposes')}<div className="distribution-stacked" aria-hidden="true">{purposes.map((row:Data)=><span key={row.id} style={{width:row.share_pct+'%',background:row.color} as CSSProperties}>{pct(row.share_pct)}</span>)}</div>{legend(purposes)}</section>
  </div>
  {detail&&<Drawer title={L[detail]} onClose={()=>setDetail(null)}><p>{L[detail+'_info']}</p></Drawer>}
 </div>;
}
