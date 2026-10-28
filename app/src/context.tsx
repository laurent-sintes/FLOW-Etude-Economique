import {createContext,useContext} from 'react';
import type {Dispatch,SetStateAction} from 'react';
import type {ReaderSession} from './reloadSession';
import {createFormat} from './formatting';
export type Data = Record<string,any>;
export type Parameters = {common:Record<string,number>;options:Record<string,Record<string,number>>};
export type Totals = {build:number;integration:number;mco_run:number;total:number};
export type Horizon = {years:number;totals:Totals;cost_natures:Record<string,number>;responsibilities:Record<string,number>;service_years:number;build_progress:number|null;integration_progress:number;remaining:number;stage:string};
export type Option = {stack:string;name:string;mode:string;horizons:Horizon[];annual:({annee:number;responsibilities:Record<string,number>}&Totals)[];service_start_month:number;selection_buy:number;selection_months:number;initial_months:number;obtention:number;build:number;integration:number;annual_base:Record<string,number>;editor_prices:number[];services:{core:number|null;integration:number|null;groupes:number};funding_ledger:Data[];annual_services:Record<string,number>;annual_responsibilities:Record<string,number>;initial_responsibilities:Record<string,number>;hosting_build:number};
export type Projection = {model_version:string;parameters:Parameters;options:Option[];anchor:Record<string,number>;make_integration_months:number};
export type Bootstrap = {ui:Data;glossary:Data;baseline:Projection;content:Data;model_version:string;simulation_contract:string;server_revision:string;date:string;edition:{mode:'current'|'draft'|'release';date:string;id?:string};resumedProjection?:Projection};
export const StudyContext=createContext<{data:Bootstrap;openDoc:(path:string)=>void;session:ReaderSession;setSession:Dispatch<SetStateAction<ReaderSession>>}|null>(null);
export function useStudy(){const ctx=useContext(StudyContext);if(!ctx)throw Error('ERR_CONTEXT');return ctx;}
export function useFormat(){const {data}=useStudy();return createFormat(data.ui.locale,data.ui.monetary_display,data.ui.labels as {money_unit:string;annual_money_unit:string;price_unit:string});}
export {request} from './transport';
