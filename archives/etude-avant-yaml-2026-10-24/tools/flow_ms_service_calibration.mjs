// Activity estimate, independent of SAP prices and FLOW construction effort.
export function applyMicrosoftServiceCalibration(ctx) {
 const {S,set,f,inp,band,note,total,borders,C,font,fmtJH,fmtEuro,fmtRate}=ctx;
 const s=S['Run Flow'],u=S['Prix unitaire Microsoft'],ref=S['Références'];
 const zero="'Paramètres'!$D$18",two="'Paramètres'!$D$23";
 const guardedProduct=(a,b)=>`=IF(AND(COUNT(${a},${b})=${two},MIN(${a},${b})>=${zero}),${a}*${b},NA())`;
 const title=(r,text)=>{s.getRange(`B${r}:I${r}`).merge();band(s,`B${r}:I${r}`,text);};
 const sourceText='Microsoft/Avanade, réponse RFI #1, p. 39 : 40 interfaces au pilote. Repère de patrimoine, pas inventaire de la cible FLOW.';
 set(ref,'B118','Interfaces du pilote Microsoft');set(ref,'C118',40);
 ref.getRange('C118').setNumberFormat('0 "interfaces"');
 note(ref,'E118',sourceText,'H',54);
 note(ref,'B120','Responsabilités Run : Microsoft Learn, Service solution et Transition to support team. Le client/intégrateur entretient la santé de sa solution, ses configurations et intégrations. Ces sources ne chiffrent ni JH ni effectifs Beaumanoir.','H',54);
 note(ref,'B121','https://learn.microsoft.com/en-us/dynamics365/guidance/implementation-guide/service-solution','H',34);
 note(ref,'B122','https://learn.microsoft.com/en-us/dynamics365/guidance/implementation-guide/transition-to-support-team','H',34);
 note(ref,'B123','Versions : quatre publications/an et au moins deux adoptions selon Microsoft Learn (consulté le 20/10/2026). Quatre validations/an retenues ici ; charge client estimée.','H',50);
 note(ref,'B124','https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/get-started/public-preview-releases','H',34);
 s.getRange('B196:I320').format.font={name:font,size:10,color:C.ink};
 s.getRange('B196:I320').format.wrapText=true;
 s.getRange('B196:I320').format.verticalAlignment='center';
 s.getRange('B196:I320').format.rowHeight=36;
 title(196,'Microsoft — périmètre, activités et compétences');
 note(s,'B198','Un budget de travail en heures ouvrées, après stabilisation. Équipe fournisseur mutualisée en France ; sans L1 métier, astreinte ni garantie de présence dédiée. Les compétences sont une ventilation des mêmes jours, jamais un second budget.','I',58);
 title(200,'Entrées modifiables et statut des hypothèses');
 s.getRange('B201:I201').values=[['Paramètre','Valeur','Unité','Statut / justification','','','','']];
 band(s,'B201:I201',null,true);
 const drivers=[
  [202,'Domaines opérationnels',6,'domaines','Hypothèse de regroupement : achats ; commandes/retours ; stock ; allocation/promesse ; fulfillment/intercompany ; documents. Pas six ERP ni vingt équipes de marque.'],
  [203,'Interfaces à entretenir',40,'interfaces','Hypothèse cible modifiable, initialisée au repère RFI de la ligne 219. Ne pas modifier la donnée source pour ajuster l’inventaire cible.'],
  [204,'Scénarios automatisés existants',"=IF(ISNUMBER('Passage Buy France'!C64),'Passage Buy France'!C64,NA())",'scénarios','Hypothèse déjà financée au build Microsoft : 120 chaînes automatisées. Entretien des scripts existants seulement ; nouveaux tests dans les changements.'],
  [205,'Mois par an',"='Paramètres'!D29",'mois','Conversion du calendrier.'],
  [206,'Jours de service humain/an',250,'jours','Convention de service en jours ouvrés ; supervision automatisée permanente. Ne garantit pas de couverture hors horaires.'],
  [207,'Campagnes de versions/an',4,'campagnes','Hypothèse : valider les quatre publications D365 et coordonner K3. Tests ciblés des correctifs exclus de ces campagnes transverses.'],
  [208,'Dossiers par domaine et par mois',4,'dossiers','Hypothèse : une demande spécialisée par domaine et par semaine environ, après tri L1. Aucun taux issu du nombre de commandes.'],
  [209,'Analyses techniques approfondies par domaine/mois',1,'analyses','Sous-ensemble des dossiers : analyse technique additionnelle après qualification fonctionnelle ; pas une deuxième réception du ticket.'],
  [210,'Correctifs par domaine/an',6,'correctifs','Hypothèse : un correctif bimestriel par domaine sur toutes les adaptations/interfaces. Code standard éditeur exclu.'],
  [211,'Reprises par interface/an',2,'reprises','Hypothèse : deux épisodes de rejets nécessitant rejeu et rapprochement par interface. Un épisode peut regrouper plusieurs messages ; hors codage.'],
  [212,'Rétablissements techniques/an',12,'incidents','Hypothèse d’un incident mensuel de connectivité/batch/environnement ; intervention sans correction de code ni rejeu métier.'],
  [213,'Revues mensuelles/an','=C205','revues','Cadence des paramètres, accès, capacité et pilotage.'],
  [214,'Revues de procédures par domaine/an',2,'revues','Relecture semestrielle des procédures métier et techniques existantes.'],
  [215,'Exercices de reprise métier/an',4,'exercices','Un exercice trimestriel transverse ; ne réachète pas les sauvegardes de la plateforme SaaS.'],
  [216,'Préparations des environnements de recette/an','=C207','préparations','Données de test, rafraîchissement et vérification des environnements à chaque campagne ; hébergement séparé.'],
  [217,'Préparations des pics/an',4,'campagnes','Hypothèse : deux bascules saisonnières et deux pics commerciaux. Une campagne transverse au groupe, pas une par marque.'],
  [218,'Revues préventives par interface/an',4,'revues','Revue trimestrielle des rejets récurrents et contrats ; hors contrôle quotidien, reprise et nouveau connecteur.'],
  [219,'Interfaces du pilote RFI — source',"=IF(ISNUMBER('Références'!C118),'Références'!C118,NA())",'interfaces','Avanade p. 39. Repère documentaire, distinct du nombre cible modifiable en C203 ; aucune extrapolation automatique par marque.'],
  [220,'Jours par personne-année',"='Paramètres'!D11",'JH/personne-an','Convention 200 JH. Conversion de capacité, pas obligation d’équipe dédiée ni coût supplémentaire.'],
 ];
 for(const [r,label,value,unit,why] of drivers){
  set(s,'B'+r,label); if(typeof value==='string'&&value.startsWith('='))f(s,'C'+r,value);else{set(s,'C'+r,value);inp(s,'C'+r,'0',0,100000,'whole');}
  set(s,'D'+r,unit);note(s,'E'+r,why,'I',48);
 }
 note(s,'B222','Les fréquences sont des hypothèses de travail explicites, pas des mesures Beaumanoir. Les vingt marques partagent les domaines et interfaces ; aucun multiplicateur de CA, de pièces vendues, de marque ou de coût Make n’est utilisé.','I',56);
 title(230,'Activités — volume × jours par compétence × tarif');
 s.getRange('B231:I231').values=[['Activité','Volume/an','JH/unité','JH/an','Compétence','€/JH','€/an','Frontière / justification']];
 band(s,'B231:I231',null,true);
 const roles=['Fonctionnel','Technique / intégration','Développement','Tests / versions','Pilotage du service'];
 const rows=[
 // row, group, activity, quantity formula, effort, skill, boundary
 [232,148,'Qualification et diagnostic fonctionnel','=C202*C208*C205',.5,0,'Traçage commande/stock/règle, qualification et escalade ; hors correctif.'],
 [233,148,'Diagnostic technique approfondi','=C202*C209*C205',.75,1,'Logs, échanges, configuration technique. Sous-ensemble des dossiers ; analyse différente du diagnostic fonctionnel.'],
 [235,149,'Conception du correctif','=C202*C210',.5,0,'Analyse de la correction à réaliser après diagnostic ; paramètres et critères de recette.'],
 [236,149,'Réalisation du correctif','=C202*C210',2,2,'Corrections de toutes les adaptations et interfaces, OMS compris ; hors code standard D365/K3.'],
 [237,149,'Tests ciblés du correctif','=C202*C210',.5,3,'Vérification ciblée et documentation du correctif ; hors campagne transverse.'],
 [239,150,'Validation métier des versions','=C207*C202',.5,0,'Un contrôle représentatif par domaine et campagne ; pas tous les utilisateurs de toutes les marques.'],
 [240,150,'Régression par domaine','=C207*C202',1.5,3,'Exécution, analyse des écarts et preuve de tests transverses. Scripts automatisés supposés disponibles.'],
 [241,150,'Compatibilité des interfaces','=C207*C203',.125,3,'Contrôles automatisés et analyse par interface/campagne ; hors rejeu en production.'],
 [242,150,'Entretien des tests automatisés','=C204',.25,3,'Mise à jour annuelle des scripts existants pour garder leur exploitabilité ; nouveaux tests compris dans les évolutions.'],
 [243,150,'Préparation et livraison des versions','=C207',2,1,'Coordination des packages D365/K3, contrôle des déploiements et retour arrière ; hors fourniture du standard.'],
 [245,151,'Revue et coordination du service','=C213',2,4,'Qualité de service, problèmes et fournisseurs ; pilotage de chaque évolution financé dans cette évolution.'],
 [246,151,'Priorisation fonctionnelle des problèmes','=C213',2,0,'Analyse transverse de récurrence, arbitrages correctifs ; hors conception de nouvelles fonctions.'],
 [247,151,'Revue d’architecture opérationnelle','=C213',1,1,'Compatibilité, dette et décisions techniques de maintien ; nouvelles architectures dans les évolutions.'],
 [249,155,'Contrôle quotidien technique','=C206',.3,1,'Revue des alertes automatisées, disponibilité et batches. Pas de présence continue ni intervention incluse.'],
 [250,155,'Contrôle quotidien des chaînes métier','=C206',.2,0,'Vérifier l’exécution des chaînes prioritaires ; le rapprochement des données est séparé.'],
 [252,157,'Cohérence commandes / stock / partenaires','=C206',.25,0,'Lire les rapprochements automatisés et qualifier les écarts ; reprises effectives ailleurs.'],
 [254,156,'Rétablissement du service','=C212',2,1,'Connectivité et exécution des batches ; hors diagnostic applicatif, code et rejeu métier.'],
 [256,157,'Accès, paramètres et capacité','=C213',2,1,'Revue technique applicative ; hors administration de l’infrastructure SaaS incluse.'],
 [258,158,'Rejeu technique des interfaces','=C203*C211',.75,1,'Préparer et exécuter le rejeu idempotent d’un épisode ; hors réparation du code.'],
 [259,158,'Contrôle métier après rejeu','=C203*C211',.25,0,'Vérifier l’exhaustivité et les engagements stock/commande après reprise.'],
 [261,159,'Fiabilité préventive des interfaces','=C203*C218',.25,1,'Revue du contrat, alertes et tendances ; travaux de changement financés hors de cette revue.'],
 [263,160,'Procédures opérationnelles métier','=C202*C214',1,0,'Maintenir les modes opératoires de maintien en service existants.'],
 [264,160,'Procédures techniques de reprise','=C202*C214',1,1,'Maintenir les procédures techniques, sans les exécuter une deuxième fois.'],
 [266,161,'Exercices de reprise — technique','=C215',3,1,'Préparation et exécution transverse des exercices ; hors sauvegardes standard SaaS.'],
 [267,161,'Exercices de reprise — métier','=C215',2,0,'Contrôles et preuve de reprise du service métier.'],
 [269,159,'Environnements et données de recette','=C216',2,1,'Préparer les données/environnements existants ; ressources et licences déjà chiffrées séparément.'],
 [271,159,'Préparation des pics — métier','=C217*C202',1,0,'Vérifier les traitements et modes de reprise par domaine avant les pics ; hors évolution de règles.'],
 [272,159,'Préparation des pics — technique','=C217*C202',.5,1,'Vérifier batches, files, seuils et performances existantes ; pas une nouvelle architecture.'],
 // Existing evolution needs, decomposed by skills; their total is not increased.
 [280,172,'Évolution règle — fonctionnel','=C172',1.5,0,'Conception/paramétrage d’une nouvelle règle et documentation ; aucune reprise du pilotage de service.'],
 [281,172,'Évolution règle — développement','=C172',1,2,'Adaptation technique de la règle ; standard/configuration réutilisés.'],
 [282,172,'Évolution règle — tests','=C172',.5,3,'Tests ciblés et mise à jour des scénarios affectés.'],
 [284,173,'Fonction/API — fonctionnel','=C173',3,0,'Conception et documentation de la fonction.'],
 [285,173,'Fonction/API — développement','=C173',10,2,'Réalisation et tests développeur.'],
 [286,173,'Fonction/API — tests','=C173',2,3,'Tests ciblés de la nouvelle fonction.'],
 [287,173,'Fonction/API — pilotage','=C173',1,4,'Pilotage de réalisation propre au changement.'],
 [289,174,'Changement structurant — fonctionnel','=C174',8,0,'Conception métier et documentation.'],
 [290,174,'Changement structurant — architecture','=C174',4,1,'Architecture propre au changement.'],
 [291,174,'Changement structurant — développement','=C174',20,2,'Réalisation et tests développeur.'],
 [292,174,'Changement structurant — tests','=C174',6,3,'Tests ciblés et scénarios nouveaux.'],
 [293,174,'Changement structurant — pilotage','=C174',2,4,'Pilotage de réalisation propre au changement.'],
 ];
 for(const [r,group,label,q,effort,skill,why] of rows){
  set(s,'B'+r,label);
  // Guard every independent driver before a reference can silently treat blank as zero.
  const refs=[...q.matchAll(/C\d+/g)].map(m=>m[0]);
  const valid=refs.map(a=>`ISNUMBER(${a})`).join(',')+(r===233?',ISNUMBER(C208),C209<=C208':'');
  f(s,'C'+r,`=IF(AND(${valid}),${q.slice(1)},NA())`);
  set(s,'D'+r,effort);inp(s,'D'+r,'0.000 "JH/unité"',0,10000);
  f(s,'E'+r,guardedProduct('C'+r,'D'+r));
  f(s,'F'+r,`=B${301+skill}`);
  f(s,'G'+r,`='Prix unitaire Microsoft'!$D$${group>=172?35:31}`);
  f(s,'H'+r,guardedProduct('E'+r,'G'+r));
  set(s,'I'+r,why);
  s.getRange(`B${r}:I${r}`).format.rowHeight=52;
 }
 for(const group of [148,149,150,151,155,156,157,158,159,160,161,172,173,174]){
  const members=rows.filter(r=>r[1]===group);
  if(group<172){
   // These rows are rollups; no fictional single quantity/effort for a mixed activity.
   s.getRange(`C${group}:D${group}`).clear({applyTo:'all'});
   f(s,'E'+group,'=SUM('+members.map(r=>'E'+r[0]).join(',')+')');
  }else{
   f(s,'H'+group,'=SUM('+members.map(r=>'D'+r[0]).join(',')+')');
  }
  f(s,'I'+group,'=SUM('+members.map(r=>'H'+r[0]).join(',')+')');
 }
 set(s,'B150','Versions, régression et tests automatisés');
 set(s,'B157','Cohérence des données, accès et capacité');
 set(s,'B159','Fiabilité, recette et préparation des pics');
 set(s,'C147','Détail →');set(s,'D147','lignes 232+');
 note(s,'B166','Microsoft : les sous-totaux renvoient aux activités et compétences détaillées lignes 232–293. Hypothèses de fréquences, efforts et capacité, sans taux appliqué au Make ni copie d’un forfait SAP.','I',52);
 note(s,'B168','Dossiers, correctifs et reprises sont estimés par domaine ou interface. Le modèle suppose une solution stabilisée et des tests automatisés maintenus. Les forfaits SAP restent inchangés ; leur capacité détaillée demeure inconnue.','I',52);
 note(s,'B64','FLOW conserve son abaque. Microsoft est dimensionné séparément par activités et compétences à partir de la ligne 196. SAP conserve ses forfaits fournisseur. Les niveaux de service ne sont pas démontrés équivalents.','I',52);
 // Earlier detailed narratives describe FLOW only; Microsoft now has its own explicit boundaries.
 for(const r of [99,102,105,108,117,120,123,126,129,132,135,138]){
  const current=s.getRange('B'+r).values[0][0];
  const prefix=current.split(' — ')[0];
  note(s,'B'+r,`${prefix} — détail FLOW : quantités et efforts aux lignes 12 à 25. Microsoft : abaque autonome lignes 232–293 ; aucune quantité FLOW ne détermine ses diagnostics, corrections ou reprises. SAP : forfaits source, capacité non détaillée.`,'I',64);
 }
 title(298,'Capacité par compétence — ventilation des mêmes jours, sans supplément');
 s.getRange('B300:I300').values=[['Compétence','MCO JH','Exploitation JH','Évolutions JH','Total JH','Personnes-an','€/an','Organisation retenue']];
 band(s,'B300:I300',null,true);
 for(const [i,role]of roles.entries()){
  const r=301+i;set(s,'B'+r,role);
  f(s,'C'+r,`=SUMIFS(E232:E247,F232:F247,B${r})`);
  f(s,'D'+r,`=SUMIFS(E249:E272,F249:F272,B${r})`);
  f(s,'E'+r,`=SUMIFS(E280:E293,F280:F293,B${r})`);
  f(s,'F'+r,`=SUM(C${r}:E${r})`);
  f(s,'G'+r,`=IF(AND(ISNUMBER(C220),C220>${zero}),F${r}/$C$220,NA())`);
  f(s,'H'+r,`=SUMIFS(H232:H293,F232:F293,B${r})`);
  set(s,'I'+r,'Capacité fournisseur mutualisée. Activités planifiées et interventions partagent les mêmes spécialistes ; pas de présence dédiée garantie.');
  s.getRange(`B${r}:I${r}`).format.rowHeight=52;
 }
 set(s,'B307','TOTAL CAPACITÉ');
 for(const col of ['C','D','E','F','G','H'])f(s,col+'307',`=SUM(${col}301:${col}305)`);
 total(s,'B307:I307');
 note(s,'B309','La capacité additionne maintenance, exploitation et évolutions. Elle ne s’ajoute à aucun budget. Les jours/jour ouvré ne valent pas garantie de disponibilité : continuité assurée par mutualisation fournisseur, modalités à contractualiser. Aucune réserve de risque ni astreinte ajoutée.','I',60);
 note(s,'B311','Tarif conservé : prix moyen spécialisé France dans Prix unitaire Microsoft, commun aux compétences pour éviter une revalorisation non documentée. Les profils sont visibles en JH ; aucune hypothèse de productivité ne vient d’un prix SAP.','I',54);
 note(s,'B313','Les charges annuelles sont celles d’un régime stabilisé. Le prorata des livraisons est conservé comme convention du modèle, sans promettre la divisibilité d’une équipe réelle. Stabilisation initiale supposée comprise dans le projet ; client interne et L1 exclus.','I',56);
 for(const a of ['E232:E293','C301:F307'])s.getRange(a).setNumberFormat('#,##0.0 "JH"');
 s.getRange('G301:G307').setNumberFormat('0.00 "personnes-an"');
 s.getRange('G232:G293').setNumberFormat(fmtRate);
 s.getRange('H232:H307').setNumberFormat('#,##0 "€/an"');
 s.getRange('C232:C293').setNumberFormat('0 "unités/an"');
 for(const a of ['B231:I293','B300:I307'])borders(s,a);
 // Summary on the Microsoft unit-price sheet: values always link to the owner.
 for(const [r,owner]of [[76,148],[77,149],[78,150],[79,151]]){
  u.getRange(`C${r}:D${r}`).clear({applyTo:'all'});
  set(u,'H'+r,'Hypothèse d’activité — Service annuel, lignes 232–293.');
 }
 set(u,'B78','Versions et entretien des tests');
 set(u,'C75','');set(u,'D75','');
 note(u,'B40','Microsoft : activités par domaine, interface et campagne ; ventilation par compétence dans Service annuel. Fréquences et efforts estimés, service mutualisé en heures ouvrées. Aucun forfait SAP ni pourcentage du Make.','H',60);
 note(u,'B85','Diagnostics : six domaines opérationnels ; quatre dossiers fonctionnels par domaine/mois, dont une analyse technique approfondie. Efforts distincts, sans double réception du même ticket.','H',56);
 note(u,'B86','Correctifs : six par domaine/an, soit un tous les deux mois ; trois JH par correctif répartis entre fonctionnel, développement et tests ciblés. Toutes les adaptations/interfaces, OMS compris.','H',56);
 note(u,'B87','Versions : quatre campagnes, six domaines et 40 interfaces de référence. L’entretien des 120 scénarios automatisés existants est explicite ; les nouveaux tests restent dans les évolutions.','H',56);
 note(u,'B88','Pilotage : coordination de service, priorisation fonctionnelle et revue technique séparées. Le pilotage de réalisation est inclus une fois dans les évolutions.','H',56);
 note(u,'B108','Exploitation : contrôles quotidiens techniques/métier, cohérence des données, reprises par interface, rétablissements, fiabilité, préparation des pics et exercices de reprise. Les ressources cloud et le standard ne sont pas rachetés.','H',60);
 set(u,'H104','Somme des activités détaillées, pas un forfait SAP transposé.');
 s.getRange('E148:E164').setNumberFormat('#,##0.0 "JH"');
 u.getRange('D104').setNumberFormat('#,##0.0 "JH"');
 note(S['Prix Microsoft'],'B34','Services Microsoft : activités et compétences détaillées dans Service annuel. Hypothèses en heures ouvrées, équipe mutualisée ; licences, plateformes et Unified séparés. SAP conserve les forfaits source.','H',56);
 note(S['Comparaison'],'B84','SAP : forfaits fournisseur conservés. Microsoft : activités par domaine/interface et capacité par compétence. Estimations de dépenses ; équivalence des SLA et économies non garanties.','I',42);
 return {activityRows:rows.map(r=>r[0]),drivers:drivers.map(r=>r[0]),skillsRange:'B300:I307'};
}
