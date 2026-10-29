// Mesures Java Axelor lecture seule, lance depuis C:/Dev/FLOW-Etude-Economique.
const fs=require('fs'),crypto=require('crypto');
const root='tmp/oss-audit-axelor/',plat='tmp/oss-audit-axelor-platform/';
const specs=[
 ['AXCSV_PROCESS',plat+'axelor-core/src/main/java/com/axelor/data/csv/CSVImporter.java',[[232,367]]],
 ['AXCSV_ROW_REPLAY',plat+'axelor-core/src/main/java/com/axelor/data/csv/CSVImporter.java',[[380,447]]],
 ['AXPACK_SERVICE',root+'axelor-base/src/main/java/com/axelor/apps/base/service/ProductPackagingServiceImpl.java',[[30,89]]],
 ['AXPACK_CONTROL',root+'axelor-base/src/main/java/com/axelor/apps/base/web/ProductPackagingController.java',[[30,47]]],
 ['AXUNIT_CONVERSION',root+'axelor-base/src/main/java/com/axelor/apps/base/service/UnitConversionServiceImpl.java',[[88,145],[264,303]]],
 ['AXSHARING_QUERY',root+'axelor-base/src/main/java/com/axelor/apps/base/service/DataSharingReferentialLineServiceImpl.java',[[43,165]]],
 ['AXTOKEN_LOAD',plat+'axelor-core/src/main/java/com/axelor/auth/web/UserTokenController.java',[[47,60]]],
 ['AXTOKEN_CREATE',plat+'axelor-core/src/main/java/com/axelor/auth/web/UserTokenController.java',[[62,98]]],
 ['AXTOKEN_REVOKE',plat+'axelor-core/src/main/java/com/axelor/auth/web/UserTokenController.java',[[100,120]]],
 ['AXSHARING_CONTROL',root+'axelor-base/src/main/java/com/axelor/apps/base/web/DataSharingReferentialLineController.java',[[32,43]]]
];
function countJava(code){
 let annotations=0,semis=0,heads=0; const units=[];
 code=code.replace(/"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\/\*[\s\S]*?\*\/|\/\/[^\n]*/g,m=>m.startsWith('/')?'':'STR');
 code=code.replace(/^\s*@[^\n]+/gm,m=>{annotations++;return '';});let par=0,pending='';
 for(const c of code){if(c==='(')par++;if(c===')')par--;if(c===';'&&par===0){if(pending.trim()){semis++;units.push(pending.trim().replace(/\s+/g,' '));}pending='';}else if(c==='{'&&par===0){if(pending.trim()){if(/=\s*$/.test(pending))throw new Error('Initialiseur hors convention, examiner manuellement');heads++;units.push(pending.trim().replace(/\s+/g,' '));}pending='';}else if(c==='}'&&par===0){pending='';}else pending+=c;}
 return {semicolon_units:semis,compound_headers:heads,logical_units_proxy:semis+heads,annotations_separate:annotations,normalized_units:units};
}
const result={id:'iteration-08-java-mesures',date:'2026-10-29',status:'Mesure du code uniquement, aucun effort humain',counter_convention:'Lignes logiques normalisées, proxy explicite : une instruction/déclaration terminée par point-virgule hors parenthèses ; une entête de bloc ouvrant ; vide/commentaire/chaînes/accolades seules exclus. Les continuations sont réunies. Un if sans accolade et son return restent une unité. Annotations isolées séparées. Cette convention ne constitue pas un comptage AST standardisé.',limitations:['Les tranches sélectionnées ont été lues et ne comportent pas de corps d initialisation de tableau/collection avec accolades ; le compteur rejette les initialisations = {, mais ne prétend pas analyser tout Java.','Les signatures, déclarations locales, appels, branches et traitements erreur sont comptés ; package/imports exclus par sélection de plage.','Pas de code généré ou de tests dans les tranches Java. Les tests et le support devront être traités séparément pour une taille cible.','Aucun code Axelor admis comme composant réutilisable en Spring. Aucun ratio automatique de conversion Java vers Spring.'],samples:[]};
for(const [id,path,ranges] of specs){const raw=fs.readFileSync(path),lines=raw.toString('utf8').split(/\r?\n/);const parts=ranges.map(([a,b])=>countJava(lines.slice(a-1,b).join('\n')));result.samples.push({id,path,ranges,sha256:crypto.createHash('sha256').update(raw).digest('hex'),commit:path.includes('platform')?'96caf51eb97fbab7750b7dadf10a371a55a490a3':'e7cbea53bae88d2540f59a70b09bf0f326f1022e',logical_units_proxy:parts.reduce((n,p)=>n+p.logical_units_proxy,0),annotations_separate:parts.reduce((n,p)=>n+p.annotations_separate,0),detail:parts});}
result.declarative=[];
for(const [id,path,range] of [
 ['AXPACK_DOMAIN',root+'axelor-base/src/main/resources/domains/ProductPackaging.xml',[10,16]],
 ['AXUNIT_DOMAIN',root+'axelor-base/src/main/resources/domains/UnitConversion.xml',[10,22]],
 ['AXPACK_VIEW',root+'axelor-base/src/main/resources/views/ProductPackaging.xml',[6,44]]
]){const raw=fs.readFileSync(path),part=raw.toString('utf8').split(/\r?\n/).slice(range[0]-1,range[1]).join('\n');const cleaned=part.replace(/<!\[CDATA\[[\s\S]*?\]\]>/g,'').replace(/<!--[\s\S]*?-->/g,'');const tags=[...cleaned.matchAll(/<([A-Za-z][\w-]*)\b[^>]*>/g)].map(m=>m[1]);result.declarative.push({id,path,range,sha256:crypto.createHash('sha256').update(raw).digest('hex'),declarative_open_elements:tags.length,element_names:tags,cdata_code_excluded:true});}
process.stdout.write(JSON.stringify(result,null,2)+'\n');
