import {FileCode,FileJson,FileSpreadsheet,FileText} from 'lucide-react';
export function FileFormatMark({format}:{format:string}){
 const value=format.toLowerCase(),Icon=value==='xlsx'?FileSpreadsheet:value==='yaml'?FileCode:value==='json'?FileJson:FileText;
 return <span className={'file-format-mark synvance-file-type synvance-file-type--'+value}><Icon size={19} aria-hidden="true"/><span>{format.toUpperCase()}</span></span>;
}
