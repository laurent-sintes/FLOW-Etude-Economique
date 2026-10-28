import fs from 'node:fs';
import path from 'node:path';
import {parse} from '@babel/parser';
import traverse from '@babel/traverse';
const walk=traverse.default||traverse;
function inspect(code){
 const errors=[];
 walk(parse(code,{sourceType:'module',plugins:['typescript','jsx']}),{
  JSXText(p){if(/[\p{L}\p{N}]/u.test(p.node.value.trim()))errors.push(p.node.loc.start.line);},
  JSXAttribute(p){if(['title','placeholder','aria-label','alt'].includes(p.node.name.name)&&p.node.value?.type==='StringLiteral'&&/[\p{L}\p{N}]/u.test(p.node.value.value))errors.push(p.node.loc.start.line);},
  JSXExpressionContainer(p){if(p.node.expression.type==='StringLiteral'&&/[\p{L}\p{N}]/u.test(p.node.expression.value))errors.push(p.node.loc.start.line);},
  StringLiteral(p){
   const value=p.node.value;
   if(/[À-ž]/u.test(value))errors.push(p.node.loc.start.line);
   if(/[a-zA-Z]+\s+[a-zA-Z]+/.test(value)){
    const attr=p.findParent(q=>q.isJSXAttribute());
    if(attr?.node.name.name!=='className')errors.push(p.node.loc.start.line);
   }
  }
 });
 return [...new Set(errors)];
}
const issues=[];
for(const name of fs.readdirSync('src').filter(f=>/\.tsx?$/.test(f))){const lines=inspect(fs.readFileSync(path.join('src',name),'utf8'));if(lines.length)issues.push({file:name,lines});}
if(!inspect('const x=<h1>Texte ajouté en dur</h1>;').length)throw Error('ERR_CONTENT_PROBE');
if(!inspect('const x=<input placeholder="Nom"/>;').length)throw Error('ERR_CONTENT_PROBE');
console.log(JSON.stringify({issues},null,2));
if(issues.length)process.exitCode=1;
