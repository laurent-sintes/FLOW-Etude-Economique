import {useStudy,type Data} from './context';
import {MethodText} from './MethodDocument';
import {SourceLink} from './components';
import {BusinessAreaSummary,ScopeDiagram} from './ModelMap';
import './cartography.css';

export function CartographyPage(){
 const {data}=useStudy(),T=data.ui.essential.cartography,S=data.content.delivery_readiness.scope;
 const subdomains=S.hierarchy.flatMap((domain:Data)=>domain.subdomains),areas=subdomains.flatMap((subdomain:Data)=>subdomain.areas);
 const summary=S.labels.hierarchy_summary.replace('{capabilities}',S.rows.length).replace('{subdomains}',subdomains.length).replace('{areas}',areas.length);
 return <div className="essential-page cartography-page">
  <section aria-labelledby="cartography-source"><h2 id="cartography-source">{T.source_title}</h2><p><strong>{T.source_name}</strong></p><p><MethodText>{T.intro}</MethodText></p>
   <dl className="cartography-provenance"><div><dt>{S.labels.capture_date}</dt><dd><time dateTime={S.source.date}>{new Intl.DateTimeFormat(data.ui.locale,{dateStyle:'long',timeZone:'UTC'}).format(new Date(S.source.date))}</time></dd></div><div><dt>{S.labels.version}</dt><dd>{S.source.version}</dd></div></dl>
   <p><MethodText>{summary}</MethodText></p><p><MethodText>{S.introduction}</MethodText></p><p className="cartography-boundary"><MethodText>{S.note}</MethodText></p>
  </section>
  <ScopeDiagram heading="h2"><div className="model-reading-links"><SourceLink path={S.link.href}>{S.link.label}</SourceLink></div></ScopeDiagram>
  <BusinessAreaSummary heading="h2" provenance={false}/>
  <p className="cartography-model-link"><a className="text-button" href="#modele?section=scope">{T.model_link} →</a></p>
 </div>;
}
