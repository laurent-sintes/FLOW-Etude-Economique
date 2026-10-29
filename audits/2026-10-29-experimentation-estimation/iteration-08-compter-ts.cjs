const fs=require('fs'), path=require('path'), crypto=require('crypto');
const root=process.cwd();
const ts=require(path.join(root,'app/node_modules/typescript/lib/typescript.js'));
const paths=[
'axelor-front/src/views/search/search.tsx',
'axelor-front/src/services/http/http.ts',
'axelor-front/src/components/alerts/alerts.tsx',
'axelor-front/src/components/accessible-button/accessible-button.tsx'
];
let out={convention:{name:'TS_AST_LOGICAL_V1',procedural:'Chaque instruction AST hors Block et EmptyStatement; declarations variables comptees une fois par instruction; declarations fonction/class/type/import comptees comme declaration; expressions de retour restent une seule instruction.',declarative:'Chaque declaration type/interface/membre/propriete objet et chaque element JSX ouvrant ou autofermant, chaque attribut JSX, comptent une unite declarative; fermetures et braces seules exclues. Les callbacks ne sont pas une declaration supplementaire, leur corps reste compte. Ce proxy est une convention de lignes logiques, non une certification du standard SEI.',limits:'Les langages sont comptes separement; pas de facteur Python vers Java. Les interfaces declares reutilisees ne sont pas implementation livree gratuite.'},parser_version:ts.version,files:[]};
for(const rel of paths){
 const full=path.join(root,'tmp/oss-audit-axelor-platform',rel), buf=fs.readFileSync(full), src=buf.toString('utf8');
 const sf=ts.createSourceFile(rel,src,ts.ScriptTarget.Latest,true,rel.endsWith('tsx')?ts.ScriptKind.TSX:ts.ScriptKind.TS);
 const counts={procedural:0,declarations:0,object_properties:0,jsx_elements:0,jsx_attributes:0};
 const units=[];
 function walk(n){
   let cat=null;
   if(ts.isImportDeclaration(n)||ts.isExportDeclaration(n)||ts.isTypeAliasDeclaration(n)||ts.isInterfaceDeclaration(n)||ts.isFunctionDeclaration(n)||ts.isClassDeclaration(n)||ts.isModuleDeclaration(n)||ts.isPropertySignature(n)||ts.isMethodSignature(n)||ts.isPropertyDeclaration(n)||ts.isMethodDeclaration(n)) cat='declarations';
   else if(ts.isStatement(n)&&!ts.isBlock(n)&&!ts.isEmptyStatement(n))cat='procedural';
   else if(ts.isPropertyAssignment(n)||ts.isShorthandPropertyAssignment(n)||ts.isSpreadAssignment(n))cat='object_properties';
   else if(ts.isJsxOpeningElement(n)||ts.isJsxSelfClosingElement(n))cat='jsx_elements';
   else if(ts.isJsxAttribute(n)||ts.isJsxSpreadAttribute(n))cat='jsx_attributes';
   if(cat){counts[cat]++; units.push({line:sf.getLineAndCharacterOfPosition(n.getStart(sf)).line+1,kind:ts.SyntaxKind[n.kind],category:cat});}
   ts.forEachChild(n,walk);
 }
 walk(sf);
 const total=Object.values(counts).reduce((a,b)=>a+b,0);
 out.files.push({id:rel.includes('search.tsx')?'TS-SEARCH':rel.includes('/http/')?'TS-HTTP':rel.includes('/alerts/')?'TS-ALERT':'TS-KEYBOARD',repository_id:'axelor-platform',commit:'96caf51eb97fbab7750b7dadf10a371a55a490a3',path:rel,cache_path:path.relative(root,full).replaceAll('\\','/'),ranges:[[1,src.split(/\r?\n/).length]],sha256:crypto.createHash('sha256').update(buf).digest('hex'),counts,total_logical:total,units,read_status:'code lu integralement par assistant',reuse_status:'analogie seulement; aucun code source admis au reutilisable Spring'});
}
const dest=path.join(root,'audits/2026-10-29-experimentation-estimation/iteration-08-ts-mesures.json');
fs.writeFileSync(dest,JSON.stringify(out,null,2)+'\n');
process.stdout.write(JSON.stringify(out.files.map(({id,counts,total_logical,sha256})=>({id,counts,total_logical,sha256})),null,2));
