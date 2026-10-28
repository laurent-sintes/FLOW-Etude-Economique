import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const require=createRequire('C:/Users/laure/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {marked}=await import(pathToFileURL(require.resolve('marked')).href);
const out='outputs/01a1530f-f378-7fd1-9654-468c9b2141b6/FLOW_Dossier_client_2026-10-21';
await fs.mkdir(out+'/annexes',{recursive:true});
await fs.mkdir(out+'/sources/recherche-tco-2026-10-20',{recursive:true});
await fs.cp('sources/client',out+'/sources/client',{recursive:true});
await fs.copyFile('sources/Gestion de la configuration.pdf',out+'/sources/Gestion de la configuration.pdf');
for(const name of ['cabinet-office-illustrative-scm.xlsx','smartsheet-tco-roi-template.xlsx','thoughtworks-build-vs-buy-2022.pdf'])await fs.copyFile('sources/recherche-tco-2026-10-20/'+name,out+'/sources/recherche-tco-2026-10-20/'+name);
await fs.cp('assets/exalt-logo.png',out+'/exalt-logo.png');
await fs.copyFile('outputs/01a1530f-f378-7fd1-9654-468c9b2141b6/FLOW_Make_abaques_et_prix_France_v4.xlsx',out+'/FLOW_Comparaison.xlsx');
const docs=(await fs.readdir('.')).filter(n=>/^(01|02|03|04|05|06|07|09|11|12|13|15|16|20)-.*\.md$/.test(n));
const css=`body{font:16px/1.55 Arial,sans-serif;color:#19344c;background:#f3f5f8;margin:0}main{max-width:1120px;margin:28px auto;padding:36px 48px;background:white}h1{font-size:30px;line-height:1.2;margin:24px 0}h2{font-size:22px;margin-top:36px;color:#19344c}h3{font-size:18px;margin-top:24px}a{color:#5041c9}nav{padding:14px 0;border-bottom:2px solid #6554ff}img{max-width:150px;height:auto}table{width:100%;border-collapse:collapse;margin:20px 0;font-size:14px;table-layout:auto}th{background:#19344c;color:white;text-align:left}td,th{padding:10px 12px;border-bottom:1px solid #dce3e9;vertical-align:top}tr:nth-child(even){background:#f2f0ff}code{word-break:break-word}blockquote{border-left:3px solid #6554ff;margin-left:0;padding-left:18px}footer{margin-top:36px;font-size:12px;color:#617488}.actions{display:flex;gap:18px;padding:18px;background:#efedff}.actions a{font-weight:bold}@media(max-width:700px){main{margin:0;padding:20px}table{font-size:12px}td,th{padding:6px}}@media print{body{background:white}main{margin:0;padding:0;max-width:none}nav,.actions{display:none}h2,h3{break-after:avoid}tr{break-inside:avoid}a{color:inherit}th{-webkit-print-color-adjust:exact}}`;
const issues=[];
function rewrite(text,sub){return text.replace(/(!?\[[^\]]*\])\(([^)]+)\)/g,(whole,label,target)=>{
 let t=target.replace(/^<|>$/g,''); if(/^https?:|^#/.test(t))return whole;
 const decoded=decodeURIComponent(t);
 if(decoded==='assets/exalt-logo.png') t=(sub?'../':'')+'exalt-logo.png';
 else if(decoded.endsWith('.md')){if(!docs.includes(decoded)&&decoded!=='README.md')issues.push(decoded); t=decoded==='README.md'?(sub?'../':'')+'index.html':(sub?'':'annexes/')+decoded.replace(/\.md$/,'.html');}
 else if(decoded.includes('FLOW_Make_abaques_et_prix_France_v4.xlsx'))t=(sub?'../':'')+'FLOW_Comparaison.xlsx';
 else {t=(sub?'../':'')+t;}
 return `${label}(${t})`;
});}
for(const name of docs){
 const content=await fs.readFile(name,'utf8'); const title=(content.match(/^# (.+)$/m)||[])[1];
 const html=marked.parse(rewrite(content,true));
 await fs.writeFile(`${out}/annexes/${name.replace('.md','.html')}`,`<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title}</title><style>${css}</style><main><nav><a href="../index.html">Accueil du dossier</a> · <a href="20-registre-sources.html">Pièces et références</a> · <a href="../FLOW_Comparaison.xlsx">Excel</a></nav>${html}<footer>Laurent Sintès · eXalt · 21 octobre 2026 · Étude sous hypothèses</footer></main></html>`);
}
let intro=await fs.readFile('README.md','utf8');
intro+=`\n## Annexes de calcul\n\n${docs.filter(n=>['09','12','16'].includes(n.slice(0,2))).map(n=>'- ['+n.replace(/^\d+-|\.md$/g,'').replaceAll('-',' ')+']('+n+')').join('\n')}\n`;
await fs.writeFile(out+'/index.html',`<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FLOW Étude économique</title><style>${css}</style><main><div class="actions"><a href="FLOW_Etude_decision.pdf">Note de décision PDF</a><a href="FLOW_Comparaison.xlsx">Comparaison Excel</a><a href="annexes/20-registre-sources.html">Sources</a></div>${marked.parse(rewrite(intro,false))}<footer>Les références publiques nécessitent Internet. Les pièces locales sont incluses ; extraire entièrement le dossier avant lecture.</footer></main></html>`);
// Marked tokens feed the PDF renderer; authoring text has a single source.
await fs.writeFile('tmp/client_note_tokens.json',JSON.stringify(marked.lexer(await fs.readFile('04-resultats-etude.md','utf8'))));
await fs.writeFile(out+'/LIRE-MOI.txt','FLOW — Étude économique\r\nLaurent Sintès · eXalt · 21 octobre 2026\r\n\r\nExtraire entièrement cette archive, puis ouvrir index.html dans un navigateur.\r\nLa note de décision est fournie en PDF. Le classeur FLOW_Comparaison.xlsx contient les trois onglets de calcul.\r\nLes annexes HTML et les pièces sources se consultent depuis l’accueil et le registre des références.\r\nLes sources locales sont incluses ; les publications de marché nécessitent une connexion Internet.\r\nLes propositions fournisseurs et questionnaires Beaumanoir sont confidentiels.\r\n');
if(issues.length)throw Error('Unpublished links: '+issues.join(','));
console.log(out,docs.length,'HTML annexes');
