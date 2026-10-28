import {TableViewport} from './TableViewport';
import {GlossaryText} from './GlossaryText';
import {useState} from 'react';
import {ArrowUpRight} from 'lucide-react';
import {useStudy,type Data} from './context';
import {Disclosure,Drawer,Section,SourceLink} from './components';

export function StrategyComparison(){
 const {data}=useStudy();const D=data.content.sponsor.decision;const L=D.affichage;
 const [selected,setSelected]=useState<Data|null>(null);
 const matrix=(rows:Data[])=><TableViewport title={L.comparaison} className="comparison-scroll"><table className="strategy-matrix"><thead><tr><th scope="col">{L.dimension}</th>{D.options.map((o:Data)=><th scope="col" key={o.id}>{o.nom}</th>)}</tr></thead><tbody>{rows.map((r:Data)=><tr key={r.id}><th scope="row"><strong><GlossaryText>{r.titre}</GlossaryText></strong><button className="reading-detail" onClick={()=>setSelected(r)}>{L.approfondir}<ArrowUpRight size={13}/></button></th>{D.options.map((o:Data)=><td key={o.id}><p><b>{L.avantage}</b><GlossaryText>{r.options[o.id].apport}</GlossaryText></p><p className="strategy-tradeoff"><b>{L.contrepartie}</b><GlossaryText>{r.options[o.id].contrepartie}</GlossaryText></p></td>)}</tr>)}</tbody></table></TableViewport>;
 return <Section title={L.comparaison} description={L.introduction} className="strategy-comparison">
  {matrix(D.criteres.filter((r:Data)=>r.principal))}
  <Disclosure title={L.autres_criteres}>{matrix(D.criteres.filter((r:Data)=>!r.principal))}</Disclosure>
  {selected&&<Drawer title={selected.titre} onClose={()=>setSelected(null)} wide><div className="decision-proof"><h3>{L.preuve}</h3><p><GlossaryText>{selected.preuve}</GlossaryText></p><h3>{L.responsable}</h3><p><GlossaryText>{selected.responsable}</GlossaryText></p><h3>{L.impact}</h3><p><GlossaryText>{selected.impact}</GlossaryText></p><SourceLink path={selected.source}/></div></Drawer>}
 </Section>;
}

export function StrategyChoices(){
 const {data}=useStudy();const D=data.content.sponsor.decision;const L=D.affichage;
 return <Section title={L.positionnement} description={L.positionnement_note}><div className="strategy-choices">{D.options.map((o:Data)=><article key={o.id}><h3>{o.nom}</h3><h4>{L.favorable}</h4><p><GlossaryText>{o.favorable}</GlossaryText></p><p className="strategy-commitment"><GlossaryText>{o.engagement}</GlossaryText></p><h4>{L.renoncer}</h4><p><GlossaryText>{o.renoncer}</GlossaryText></p></article>)}</div><Disclosure title={L.alternatives}>{D.alternatives.map((a:Data)=><article className="decision-paragraph" key={a.titre}><h3><GlossaryText>{a.titre}</GlossaryText></h3><p><GlossaryText>{a.texte}</GlossaryText></p></article>)}</Disclosure></Section>;
}

export function DecisionEvidence(){
 const {data}=useStudy();const D=data.content.sponsor.decision;const L=D.affichage;
 return <>
  <Section title={L.benefices} description={L.benefices_note}><div className="decision-benefits">{D.benefices.map((b:Data)=><article key={b.id}><h3><GlossaryText>{b.titre}</GlossaryText></h3><p><GlossaryText>{b.indicateur}</GlossaryText></p><Disclosure title={data.ui.editorial.benefits_detail}><dl>{(['initial','cible','echeance'] as const).map(k=><div key={k}><dt>{L[k]}</dt><dd>{b[k]??L.inconnu}</dd></div>)}</dl><small><GlossaryText>{b.responsable}</GlossaryText></small></Disclosure></article>)}</div></Section>
  <Disclosure title={L.sortie}><p>{L.sortie_note}</p><div className="decision-gates">{D.preuves.map((p:Data)=><article key={p.id}><header><h3><GlossaryText>{p.titre}</GlossaryText></h3></header><p><GlossaryText>{p.livrable}</GlossaryText></p><div className="decision-gate-rule"><div><h4>{L.poursuivre}</h4><p><GlossaryText>{p.poursuivre}</GlossaryText></p></div><div><h4>{L.arreter}</h4><p><GlossaryText>{p.arreter}</GlossaryText></p></div></div><Disclosure title={L.approfondir}><h4>{L.risque}</h4><p><GlossaryText>{p.risque}</GlossaryText></p><h4>{L.reponse}</h4><p><GlossaryText>{p.reponse}</GlossaryText></p><h4>{L.responsable}</h4><p><GlossaryText>{p.responsable}</GlossaryText></p><SourceLink path={p.source}/></Disclosure></article>)}</div></Disclosure>
 </>;
}

export function DecisionMandate(){
 const {data}=useStudy();const D=data.content.sponsor.decision;const L=D.affichage;
 return <Section title={L.mandat} description={L.mandat_texte} className="decision-mandate">
  <Disclosure title={data.ui.editorial.mandate_detail}>
  <div className="mandate-fields">{D.mandat.map((m:Data)=><article key={m.id}><h3>{m.titre}</h3><strong>{m.valeur??L.inconnu}</strong><p>{m.aide}</p></article>)}</div></Disclosure>
  <p className="sponsor-arbitration">{data.content.sponsor.decision_suivante.regle_arbitrage}</p>

  <Disclosure title={L.methodes}>{D.methodes.map((m:Data)=><article key={m.source} className="decision-paragraph"><SourceLink path={m.source}>{m.titre}</SourceLink><p>{m.apport}</p><p className="small-prose">{m.limite}</p></article>)}</Disclosure>
 </Section>;
}
