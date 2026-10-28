import type {ReactNode} from 'react';
import {SourceLink} from './components';

// A URL or filename identifies the source; it does not establish its evidence type.
export function marketSourceName(path:string):string{
 if(/^https?:\/\//.test(path)){
  try{
   const url=new URL(path),host=url.hostname.replace(/^www\./,''),name=decodeURIComponent(url.pathname.split('/').filter(Boolean).pop()||'');
   return name&&name!=='index.html'&&!/^[0-9a-f]{32,40}$/i.test(name)?`${host} · ${name}`:host;
  }catch{return path;}
 }
 return path.split('#')[0].split('/').pop()||path;
}

export function MarketSourceLink({path,label,children}:{path:string;label:string;children?:ReactNode}){
 return <SourceLink path={path}>{children?<>{children} · {marketSourceName(path)}</>:`${label} · ${marketSourceName(path)}`}</SourceLink>;
}

export function MarketSourceList({paths,label}:{paths:string[];label:string}){
 return <div className="essential-market-proofs">{paths.map(path=><MarketSourceLink key={path} path={path} label={label}/>)}</div>;
}
