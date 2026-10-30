/** Reader-facing visibility only; this does not change model data or transport. */
export function isModelDataReference(reference:string):boolean{
 const value=reference.trim();
 // Public third-party sources keep their own formats and are not model exports.
 if (/^(?:https?:)?\/\//i.test(value)) return false;
 const [withoutFragment]=value.split('#');
 const [pathname,query='']=withoutFragment.split('?');
 let documentPath=(pathname==='/api/file'||pathname==='/api/document')
  ?new URLSearchParams(query).get('path')||pathname:pathname;
 try{documentPath=decodeURIComponent(documentPath);}catch{/* Compare the original path. */}
 return /\.ya?ml$/i.test(documentPath.split('#')[0].split('?')[0]);
}
