import {Boxes,Workflow,Cloud,RefreshCcw,Headset,FileCheck2,type LucideIcon} from 'lucide-react';
import {useFormat,type Data} from './context';
import './architectureLayers.css';

export const costStructureIcons:Record<string,LucideIcon>={obtention:Boxes,integration:Workflow,core_care:RefreshCcw,client_care:RefreshCcw,run_cloud:Cloud,operations_support:Headset,grouped_buy:FileCheck2};
export function CostActivityTags({tags,allocation}:{tags:Data[];allocation?:Data}){
 const {n}=useFormat();
 return <span className="model-activity-tags">{tags.map(tag=><span key={tag.id} className={'model-activity-tag model-activity-tag-'+tag.id}>{tag.label}{allocation&&<> <strong>{n(allocation[tag.id+'_pct'],1)} %</strong></>}</span>)}</span>;
}

