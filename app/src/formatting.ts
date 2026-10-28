export type MoneyDisplay = {scale:number;decimals:number;rate_scale:number;rate_decimals:number;quantity_decimals:number};
type MoneyUnits = {money_unit:string;annual_money_unit:string;price_unit:string};

// Values stay in euros in the model and scenario payloads. Scale only at display time.
export function createFormat(locale:string,display:MoneyDisplay,units:MoneyUnits){
 const n=(value:number,digits=display.quantity_decimals)=>new Intl.NumberFormat(locale,{maximumFractionDigits:digits,minimumFractionDigits:digits}).format(value);
 const money=(value:number,digits=display.decimals)=>n(value/display.scale,digits);
 const rate=(value:number)=>n(value/display.rate_scale,display.rate_decimals);
 const amount=(value:number,unit=units.money_unit)=>money(value)+'\u00a0'+unit;
 return {n,money,rate,amount,annualAmount:(value:number)=>amount(value,units.annual_money_unit),dailyRate:(value:number)=>rate(value)+'\u00a0'+units.price_unit,pct:(value:number)=>n(value*100,0)};
}
