> **Historique — retiré de la base active le 24 octobre 2026.** Les hypothèses et résultats de cette note sont remplacés par le [modèle YAML actuel](../../source/README.md).

> **Historique conservé.** Les montants, abaques de service et noms d’onglets ci-dessous décrivent les versions antérieures. Depuis le 21 octobre 2026, la [méthode](<02-methode-estimation.md>), la [note de décision](<04-resultats-etude.md>) et le [guide des trois onglets](<13-audit-classeur-excel.md>) portent le calcul courant.



![Logo eXalt](<../../assets/exalt-logo.png>)



**Laurent Sintès** · 20 octobre 2026



---



# Audit de la version v4 — lecture décideur, hypothèses et coûts récurrents



> **Statut au 20 octobre 2026 : audit de la version précédente, conservé pour traçabilité.** Les corrections demandées sont décrites dans le [suivi des corrections](<18-corrections-services-et-tracabilite.md>). Les montants, cellules et empreinte ci-dessous concernent le fichier audité avant ces modifications ; consulter la [note de décision](<04-resultats-etude.md>) et le [journal de validation](<14-audit-inflation-run-et-comparaison.md>) pour la version courante.



## Avis



**Le classeur est utilisable pour discuter des budgets sous hypothèses. Il ne suffit pas encore à conclure que FLOW est économiquement préférable à Microsoft sur quinze ans.** La première page est lisible et les additions FLOW sont réconciliées. Les réserves principales portent sur la comparabilité des services, un recouvrement possible du MCO Microsoft et plusieurs calculs qui restent décrits en texte.



Cet audit porte sur le [classeur livré](<../../outputs/01a1530f-f378-7fd1-9654-468c9b2141b6/FLOW_Make_abaques_et_prix_France_v4.xlsx>), sans le modifier. Empreinte SHA-256 : `C3A7DB3E674E5B6B21BE61F706330C2560E5B4F5EB435A5146AD76E323D9B65F`.



| Axe | Conclusion |

| --- | --- |

| Lecture rapide par un décideur | Les chiffres, horizons et jalons se lisent bien. Les conditions qui expliquent le classement doivent être rapprochées des résultats. |

| Traçabilité des hypothèses | Les principales sources et hypothèses sont identifiées. Des sous-totaux saisis et des données source dupliquées limitent encore la possibilité de modifier le modèle en confiance. |

| Double compte des coûts récurrents | Aucun double compte arithmétique confirmé dans FLOW. Un recouvrement de périmètre reste plausible dans le MCO Microsoft. L'équivalence des services entre options n'est pas établie. |



## 1. Le faible écart FLOW/Microsoft doit être présenté avec ses conditions



`Comparaison!I9:I11` présente **35,781 M€ FLOW**, **50,119886 M€ SAP** et **36,564052 M€ Microsoft**. L'avantage nominal FLOW/Microsoft est de **783 052 €**, soit **2,1 % du cumul Microsoft**.



Le prix de supervision Microsoft est une hypothèse de **450 000 €/an**, reprise du prix SAP avec un coefficient de 1 (`Prix unitaire Microsoft!D104:D106`). Cette ligne pèse **5,655 M€** sur quinze ans (`Comparaison!I76`). La source SAP porte sur des horaires étendus ; FLOW est chiffré en heures ouvrées, avec son astreinte désactivée.



La durée de fonctionnement pondérée Microsoft vaut **12,5667 années** (`Comparaison!F37`). Une diminution du proxy de supervision de seulement **62 312 €/an**, soit **13,85 %**, effacerait l'écart de 783 052 €. Calcul : écart à quinze ans ÷ années de fonctionnement pondérées. Il s'agit d'un seuil de sensibilité, pas d'un nouveau prix estimé.



**Action recommandée :** placer sous le premier tableau une ligne courte indiquant les hypothèses actives — services en France à prix constants, licences/CPI à 4 % selon les gels, options inactives, appui interne exclu — et préciser que FLOW et Microsoft sont proches à quinze ans. Signaler le proxy Microsoft de supervision à cet endroit. Retenir une même hypothèse de service, ou afficher explicitement la différence de couverture horaire. Cela demande un choix d'hypothèse, pas un cadrage détaillé.



Les premières mises en service restent M60 pour FLOW et M18 pour les solutions Buy. Les bénéfices des années de service supplémentaires ne sont pas valorisés. Le croisement à M174 est un croisement de dépenses conditionnel, pas un retour sur investissement.



## 2. Un recouvrement de périmètre subsiste dans le MCO Microsoft



| Poste Microsoft | Cellules | Budget annuel |

| --- | --- | ---: |

| Corrections des extensions et interfaces : 90 JH | `Prix unitaire Microsoft!B77:G77` | 76 500 € |

| MCO supplémentaire des nouvelles extensions : 19,17 JH | `Prix unitaire Microsoft!D134:D136` | 16 294,50 € |



Les deux charges sont additionnées dans `D30`, puis valorisées dans `D26`. Le supplément correspond à **3 % des 639 JH de complément** de `Passage Buy France!G72`. La note `B138` le rattache aux extensions nouvelles. Cependant, le panier des 90 JH ne dit pas qu'il exclut ces extensions.



**Le recouvrement est plausible, mais il n'est pas démontré que les 19,17 JH sont intégralement indus.** L'enjeu du supplément concerné est de **204 767,55 € sur quinze ans**.



**Action recommandée :** utiliser un panier annuel unique de corrections couvrant toutes les extensions, ou distinguer explicitement le patrimoine du RFI et les compléments, avec des volumes d'activité propres à chacun. La simple présence de deux formules différentes ne démontre pas deux services différents.



SAP comporte également **16,44 JH supplémentaires** ajoutés au forfait MCO de 250 k€, soit **13 974 €/an**. Une couverture limitée au patrimoine du RFI est plausible, mais cette frontière reste une hypothèse à expliciter. Aucun doublon SAP n'est établi par les pièces examinées.



## 3. La réconciliation FLOW change aussi une hypothèse de capacité



L'ancienne enveloppe de support finançait **240 diagnostics × 0,5 JH = 120 JH/an**. Le panier courant finance :



| Activité | Calcul | Charge annuelle |

| --- | --- | ---: |

| Contrôles préventifs | 250 × 0,2 JH | 50 JH |

| Diagnostics applicatifs | 100 × 0,5 JH | 50 JH |

| Rétablissements techniques | 10 × 2 JH | 20 JH |

| Total | | **120 JH** |



Les facteurs sont dans `Run Flow!C12:D14` ; l'explication historique est en `B102`. Microsoft conserve **240 diagnostics/an** dans `Prix unitaire Microsoft!C76:E76`.



La prévention peut réduire la demande réactive, mais ce gain n'est pas mesuré. Le maintien de l'enveloppe de 120 JH ne démontre donc pas une capacité identique. **La baisse du budget FLOW ne doit pas être présentée comme la seule suppression de doubles comptes.**



À titre de sensibilité, conserver 240 diagnostics FLOW tout en gardant les autres activités ajouterait **70 JH × 750 € = 52 500 €/an**, soit **525 000 € sur les dix années de fonctionnement**. Ce n'est pas une correction imposée du nominal.



**Action recommandée :** annoncer explicitement cette hypothèse de prévention et de capacité. Pour comparer les prix à besoin équivalent, définir un panier de demandes commun, ou rendre le gain de prévention supposé visible dans les chiffres.



## 4. Le détail de certains calculs est visible, mais n'est pas recalculable



Le contrôle « aucune constante numérique dans les formules » est exact. **Il ne repère pas les résultats précalculés qui ont été saisis comme des valeurs.** Le contrôle précédent était insuffisant pour conclure que tous les abaques étaient entièrement affinables.



Huit sous-totaux de charge de `Passage Buy France` sont concernés :



| Cellule | Total saisi | Calcul seulement décrit dans une note |

| --- | ---: | --- |

| E126 | 55 JH | 1 × 25 + 3 × 10 — B142 |

| E128 | 107 JH | 4 × 18 + 35 — B144 |

| E129 | 99 JH | 4 × 16 + 35 — B145 |

| E130 | 90 JH | 2 × 35 + 20 — B146 |

| E167 | 42 JH | 18 + 3 × 8 — B182 |

| E169 | 100 JH | 4 × 18 + 28 — B184 |

| E170 | 100 JH | 4 × 18 + 28 — B185 |

| E171 | 54 JH | 2 × 18 + 18 — B186 |



La justification existe bien **dans Excel**. En revanche, modifier le nombre de familles ou l'effort d'une sous-activité dans le texte ne change pas le coût.



**Action recommandée :** mettre ces quantités et charges unitaires dans des sous-lignes de cellules et faire calculer leurs totaux. Conserver comme entrées les efforts réellement estimés ; calculer les sommes et produits qui en découlent.



Deux autres défauts de traçabilité méritent correction :



- **Sources dupliquées sans liaison.** Par exemple `Paramètres!D25` et `Références!C30` portent séparément 2 810 JH ; `D37` et `C29` portent 1 319 JH ; `D38` et `C27` portent 1 467 JH ; `D39` et `C28` portent 204 JH. Une source doit avoir une cellule propriétaire, avec des renvois pour les autres usages.

- **Attribution incorrecte.** `Paramètres!C11` qualifie les 200 JH par personne et par an d'« Hypothèse COPIL ». Le COPIL fournit les effectifs et durées ; les 200 JH sont une convention de l'étude. La nature doit être corrigée.



## 5. La présentation est améliorée, mais quelques libellés entretiennent la confusion



| Localisation | Problème | Correction recommandée |

| --- | --- | --- |

| `Prix unitaire Flow!B30:D32` | « MCO : volume calculé » désigne les **656 JH de maintenance et exploitation**, alors que la ligne maintenance/pilotage de la comparaison n'en représente que 266. | Nommer explicitement « Maintenance et exploitation : charge annuelle » et harmoniser les lignes de tarif/forfait. |

| `Comparaison!B44:E64` | FLOW présente 90 k€ d'évolutions fonctionnelles dans le Core et seulement 150 k€ dans « Évolutions continues hors Core ». Les paniers Buy sont affichés en totalité dans cette dernière famille. | Afficher un total comparable des évolutions : **240 k€ FLOW, 357 k€ SAP, 374 k€ Microsoft**. Le détail Core doit rester un « dont » identifiable, sans supplément. |

| `Prix Flow`, `Prix SAP`, `Prix Microsoft`, `F6:H13` | Les cumuls 5/10/15 ans et deux notions annuelles répètent encore la comparaison. | Garder les fiches Prix pour le budget, les livraisons et les options ; limiter les repères répétés à ceux utiles à leur lecture. |

| `Structure coûts!C34:C46` | Des charges en JH sont affichées comme des nombres génériques, dans une colonne qui contient aussi des coefficients. | Afficher les unités JH et distinguer les coefficients. |

| Navigation entre les 19 onglets | Aucun lien interne ne permet de passer directement d'une famille de coût à son abaque. `Comparaison!B86` ne cite pas Run Flow. | Ajouter quelques liens depuis les résultats vers les cellules propriétaires, sans nouvel onglet de synthèse. |

| Nom de l'onglet `Plateforme et exploitation` | Il contient désormais les ressources techniques et l'option de sortie ; les prestations humaines sont ailleurs. | Employer « Plateformes et sortie ». |

| `Run Flow!I12:I23`, `Paramètres!B17/F17/B31/F31` | « Panier historique » peut être lu comme une mesure Beaumanoir ; certains commentaires décrivent encore des usages de paramètres désormais séparés. | Écrire « Hypothèse antérieure de l'étude » et retirer les explications périmées. |



La coexistence des classements « Core », « maintenance » et « évolutions » mérite une attention particulière : les lignes ne portent pas toujours sur les mêmes services entre Make et Buy. Les mises à jour du produit standard Buy sont financées par la souscription, tandis que les versions FLOW sont financées par ses équipes. Les totaux se réconcilient ; les intitulés doivent expliquer cette différence.



## 6. Ce qui est vérifié et peut être conservé



Le modèle FLOW comporte une seule addition des activités :



| Coût FLOW, année pleine | Charge | Montant |

| --- | ---: | ---: |

| Versions techniques courantes du Core | 96 JH | 72 000 € |

| Maintenance applicative et pilotage | 266 JH | 199 500 € |

| Exploitation | 294 JH | 220 500 € |

| Sous-total maintenance et exploitation | **656 JH** | **492 000 €** |

| Versions fonctionnelles du Core | 120 JH | 90 000 € |

| Autres évolutions | 200 JH | 150 000 € |

| Sous-total évolutions | **320 JH** | **240 000 €** |

| Ressources techniques | | 400 000 € |

| **Total nominal** | **976 JH** | **1 132 000 €** |



`Run Flow!E42:G49` porte cette ventilation. Dans `Calculs 15 ans`, les colonnes de Core et d'exploitation sont des sous-ensembles ; elles ne sont pas ajoutées une seconde fois au total.



Les frontières entre tests ciblés et régression transverse, entre pilotage du service et pilotage des évolutions, ainsi qu'entre factures cloud et interventions humaines sont décrites. Aucun doublon confirmé n'a été trouvé dans ces postes.



Les options d'astreinte et de migrations FLOW/SAP sont effectivement désactivées (`Run Flow!H68:H70`). Les provisions de migration ne sont pas également facturées comme des campagnes ponctuelles. Le nominal respecte ce choix ; il ne constitue pas un budget de renouvellement complet garanti sur quinze ans.



Les pièces Synvance distinguent effectivement les forfaits SAP de **250 k€ de MCO**, **450 k€ de monitoring** et **350 k€ de TMA évolutive**. La formule SAP retient le maximum entre le forfait d'évolutions et le panier estimé ; elle n'additionne pas 350 k€ et 357 k€. La couverture fonctionnelle du forfait demeure toutefois inconnue.



Les charges du pilote Microsoft de 630/460/230/380/600 JH sont bien issues des valeurs hautes de l'offre Avanade page 39. Elles ne sont pas une ventilation inventée. L'application d'un tarif France commun reste une hypothèse distincte.



L'onglet Comparaison présente correctement les horizons initial/annuel/3/5/10/15 ans, les unités, les jalons et les années pondérées de Run. Le graphique commun fonctionne et les anciennes notes coupées de Prix Flow sont réparées.



## 7. Portée de la vérification



L'empreinte du fichier est identique à celle des preuves existantes : [235 contrôles financiers](<../../tmp/audit_flow_v4_delivered.log>), [contrôle de transparence](<../../tmp/FLOW_v4_transparency_final.json>) et [recalcul Excel natif](<../../tmp/FLOW_native_v4_final.xlsx.native-report.json>). Ces contrôles ne sont pas relancés sans changement du fichier.



La présente relecture a inspecté les valeurs et formules du classeur, remonté les sources locales Synvance concernées, vérifié les frontières d'activités et examiné les vues rendues du fichier final. Les sensibilités ci-dessus sont calculées à partir de ses valeurs et proratas ; elles ne changent aucune hypothèse du livrable.



**Ordre de correction proposé :** rendre les conditions du classement visibles, définir la frontière du supplément MCO Microsoft, expliciter la capacité FLOW, convertir les huit sous-totaux en calculs Excel, puis terminer l'harmonisation des libellés, unités et renvois. Les montants actuels restent des budgets conditionnels en attendant ces corrections.

