import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {createContentRenderer} from './presentation_content.mjs';
const require=createRequire(new URL('./syntax-check/package.json',import.meta.url));
const {parse}=require('acorn'),walk=require('acorn-walk');
const data=JSON.parse(await fs.readFile('tmp/investissement-10-ans/inputs.json','utf8'));
const policy=new Set(data.presentation.politique.litteraux_techniques);
const names=new Map();const errors=[];
for(const [id,term] of Object.entries(data.glossaire.notions)){
 if(!term.libelle||!term.definition||!term.source_ref)errors.push(`notions.${id}`);
 if(names.has(term.libelle))errors.push(`DUPLICATE_TERM:${id}`);names.set(term.libelle,id);
 if(term.synonymes_historiques?.some(x=>typeof x!=='string'))errors.push(`INVALID_ALIAS:${id}`);
}
const technical=value=>policy.has(value)||value.length<=1||/^\d+$/.test(value)||/^[A-Z]{1,2}(?::[A-Z]{1,2})?$/.test(value)||/^\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?$/.test(value)||/^(libelles|contenus|formules|formats|messages|palette)\.[a-z0-9_]+$/.test(value)||value.startsWith('./')||value.startsWith('tools/')||value.startsWith('tmp/')||value.startsWith('ERR_')||value==='valid';
function inspect(code){
 const issues=[];const tree=parse(code,{ecmaVersion:'latest',sourceType:'module',locations:true});
 walk.fullAncestor(tree,(n,state,ancestors)=>{
  if(n.type==='Literal'&&typeof n.value==='string'&&!technical(n.value))issues.push({line:n.loc.start.line,value:n.value});
  if(n.type==='TemplateLiteral'){
   const probe=n.quasis.map(q=>q.value.cooked??q.value.raw).join('0');
   if(probe&&!technical(probe)&&/[a-zA-ZÀ-ÿ]/.test(probe))issues.push({line:n.loc.start.line,value:probe});
  }
 });
 return issues;
}
const path='tools/build_investment_excel.mjs';const code=await fs.readFile(path,'utf8');
const hardcoded=inspect(code);errors.push(...hardcoded.map(x=>`${path}:${x.line}:${x.value}`));
// A regression probe verifies that a newly written caption is really rejected.
if(inspect("const caption='Libellé ajouté directement au code';").length!==1)errors.push('REGRESSION_PROBE');
const t=createContentRenderer(data.presentation,data.glossaire);
for(const [id,value] of Object.entries(data.presentation.libelles)){
 try{const actual=t('libelles.'+id,Object.fromEntries(Array.from({length:30},(_,i)=>['p'+i,'1'])));if(typeof actual!=='string')errors.push(id);}catch(e){errors.push(id+':'+e.message);}
}
console.log(JSON.stringify({notions:Object.keys(data.glossaire.notions).length,libelles:Object.keys(data.presentation.libelles).length,hardcoded:hardcoded.length,errors},null,2));
if(errors.length)process.exitCode=1;
