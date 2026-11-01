import {createLucideIcon,Compass,Calculator,ChartNoAxesCombined,ListTree,Server,Files,BookOpen,Download,LibraryBig,Map as MapIcon,BriefcaseBusiness,Columns3,Tags,Gauge,Route,ClipboardCheck,SlidersHorizontal,Scale,FlaskConical,BookOpenText,type LucideIcon,type LucideProps} from 'lucide-react';
import {useStudy,type Data} from './context';

const Foundation=createLucideIcon('Foundation',[
 ['path',{d:'M2 21h20',key:'ground'}],
 ['path',{d:'M4 21v-5h16v5',key:'footing'}],
 ['path',{d:'M7 16V8h10v8',key:'wall'}],
 ['path',{d:'M7 8V3m10 5V3M5 5h4m6 0h4',key:'reinforcement'}],
 ['path',{d:'M10 16v5m4-5v5',key:'blocks'}],
]);
const PuzzleAssembly=createLucideIcon('PuzzleAssembly',[
 ['path',{d:'M3 3h7v3a2 2 0 1 1 0 4v2h3a2 2 0 1 0 4 0h4v9H3Z',key:'assembly'}],
 ['path',{d:'M3 12h3a2 2 0 1 1 4 0h2v9',key:'joint'}],
 ['path',{d:'M15 2h7v7h-3a2 2 0 1 0-4 0h-1V6a2 2 0 1 0 0-4Z',key:'last-piece'}],
]);
const Running=createLucideIcon('Running',[
 ['circle',{cx:'16',cy:'4',r:'2',key:'head'}],
 ['path',{d:'m13 8-3 6 5 3-2 5',key:'body-front-leg'}],
 ['path',{d:'m10 14-3 5H2',key:'back-leg'}],
 ['path',{d:'m13 8 4 4h5',key:'front-arm'}],
 ['path',{d:'m13 8-5-1-3 4',key:'back-arm'}],
]);

/** Semantic icon names belong to the application configuration. */
export const studyIcons:Record<string,LucideIcon>={compass:Compass,calculator:Calculator,chart:ChartNoAxesCombined,grid:ListTree,server:Server,files:Files,book:BookOpen,download:Download,library:LibraryBig,map:MapIcon,projects:BriefcaseBusiness,compare:Columns3,prices:Tags,productivity:Gauge,route:Route,decisions:ClipboardCheck,parameters:SlidersHorizontal,balance:Scale,experiment:FlaskConical,glossary:BookOpenText,foundation:Foundation,puzzle:PuzzleAssembly,running:Running};
export function PhaseIcon({phase,...props}:{phase:string}&LucideProps){
 const {data}=useStudy(),name=data.ui.essential.nav.find((item:Data)=>item.id===phase)?.icon,Icon=studyIcons[name]||Compass;
 return <Icon aria-hidden="true" {...props}/>;
}
