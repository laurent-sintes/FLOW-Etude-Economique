export type ModelRevision={date:string;number:number};
export function validModelRevision(value:unknown):value is ModelRevision{
 if(!value||typeof value!=='object')return false;
 const item=value as ModelRevision;
 if(typeof item.date!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(item.date)||!Number.isSafeInteger(item.number)||item.number<1)return false;
 const parsed=new Date(item.date+'T12:00:00Z');
 return !Number.isNaN(parsed.getTime())&&parsed.toISOString().slice(0,10)===item.date;
}
export function modelRevisionLabel(revision:ModelRevision|undefined|null,locale:string,numberLabel:string):string|null{
 if(!revision)return null;
 if(!validModelRevision(revision))throw Error('ERR_MODEL_REVISION');
 return new Intl.DateTimeFormat(locale,{dateStyle:'short',timeZone:'UTC'}).format(new Date(revision.date+'T12:00:00Z'))+' · '+numberLabel.replace('{number}',String(revision.number));
}
