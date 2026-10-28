type MigrationContext={simulation_contract:string;model_version:string;ui:Record<string,any>};

// Applies only to recognized pre-selection contracts. Never alters the saved original.
export function migrateBuySelection(data:MigrationContext,options:Record<string,Record<string,number>>,contract:unknown,version:string):boolean{
 const rule=data.ui.buy_selection_migration;
 if(!rule||contract===data.simulation_contract)return false;
 const legacy=contract===undefined&&rule.legacy_versions?.includes(version);
 if(!legacy&&!rule.from_contracts?.includes(contract))return false;
 for(const slug of rule.options){
  const values=options[slug];
  if(values&&Object.hasOwn(values,'integration')){
   if(typeof values.integration!=='number'||!Number.isFinite(values.integration))throw Object.assign(new Error('invalid_number'),{code:'invalid_number'});
   const amount=values.integration-rule.preparation_eur;
   if(amount<0)throw Object.assign(new Error('invalid_number'),{code:'invalid_number'});
   values.integration=amount;
  }
 }
 return true;
}
