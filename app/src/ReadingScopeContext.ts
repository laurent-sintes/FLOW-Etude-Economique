import {createContext,useContext} from 'react';
import {economicReadingContext} from './economicNavigation';
export const ReadingScopeContext=createContext<{page?:string;option?:string;horizon?:string;view?:string;origin?:string;options?:string;returnTo?:string;family?:string}>({});
export function useReadingContext(){return economicReadingContext(useContext(ReadingScopeContext));}
