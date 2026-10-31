import {Info} from 'lucide-react';
import {useStudy} from './context';
import {MethodText} from './MethodDocument';
import './readingNote.css';

export function ReadingNote({title,children}:{title?:string;children:string}){
 const {data}=useStudy();
 const label=title||data.ui.essential.editorial_notes.label;
 return <aside className="reading-note" role="note" aria-label={label}>
  <span className="reading-note-symbol" aria-hidden="true"><Info size={16}/></span>
  <div className="reading-note-copy"><strong className="reading-note-label">{label}</strong><p><MethodText>{children}</MethodText></p></div>
 </aside>;
}
