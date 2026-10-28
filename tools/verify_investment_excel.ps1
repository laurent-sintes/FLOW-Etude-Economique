param([string]$Destination='outputs/01a15da9-73b2-7760-8111-3c718f6245f3/FLOW_Investissements_10_ans_Integration_Migration.xlsx')
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$copy=Join-Path $root "tmp/investissement-10-ans/native-check-$PID.xlsx"
$dest=[IO.Path]::GetFullPath((Join-Path $root $Destination))
if (-not $dest.StartsWith($root.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Destination hors workspace' }
function AssertDestinationAvailable {
 if(Test-Path -LiteralPath $dest){
  try {$probe=[IO.File]::Open($dest,[IO.FileMode]::Open,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None);$probe.Dispose()}
  catch [IO.IOException] {throw "Classeur de destination ouvert ou verrouillé : $dest. Enregistrer et fermer sa session Excel avant la régénération."}
 }
}
AssertDestinationAvailable
Copy-Item -LiteralPath (Join-Path $root 'tmp/investissement-10-ans/authored.xlsx') -Destination $copy -Force
$expected=Get-Content -LiteralPath (Join-Path $root 'tmp/investissement-10-ans/expected.json') -Raw | ConvertFrom-Json
$inputs=Get-Content -LiteralPath (Join-Path $root 'tmp/investissement-10-ans/inputs.json') -Raw | ConvertFrom-Json
$sheetNames=[pscustomobject]@{synthese=$inputs.glossaire.vues.synthese.libelle;hypotheses=$inputs.glossaire.vues.hypotheses.libelle;investissements=$inputs.glossaire.vues.investissements.libelle;perimetre=$inputs.glossaire.vues.perimetre.libelle;calculs=$inputs.glossaire.vues.calculs.libelle;sources=$inputs.glossaire.vues.sources.libelle}
$layout=Get-Content -LiteralPath (Join-Path $root 'tmp/investissement-10-ans/layout.json') -Raw | ConvertFrom-Json
if($layout.version -ne 1 -or $layout.sheets.Count -ne 6){throw 'Contrat visuel du générateur absent ou incompatible'}
function OleColor([string]$hex){$v=$hex.TrimStart('#');[Convert]::ToInt32($v.Substring(0,2),16)+256*[Convert]::ToInt32($v.Substring(2,2),16)+65536*[Convert]::ToInt32($v.Substring(4,2),16)}
$app=$null;$book=$null;$sheets=$null;$syn=$null;$hyp=$null;$plan=$null;$scope=$null;$calc=$null;$src=$null
function Near($a,$b,[string]$label,[double]$tolerance=0.000001){ if ([Math]::Abs([double]$a-[double]$b) -gt $tolerance) { throw "$label : $a != $b" } }
# Reference budgets are rounded to cents in EUR: 0.00001 kEUR = one cent.
function NearK($a,$b,[string]$label){Near $a $b $label 0.00001}
function CompactRow($sheet,[int]$row,[double]$maximum){
 $actual=[double]$sheet.Range("A$row").EntireRow.RowHeight
 if($actual -gt $maximum+0.1){throw "Densité insuffisante : $($sheet.Name) ligne $row = $actual pt (maximum $maximum pt)"}
}
function Recalc { $app.CalculateFullRebuild(); if ($app.CalculationState -ne 0) { throw 'Recalcul non terminé' } }
try {
 $app=New-Object -ComObject Excel.Application
 $app.Visible=$false;$app.DisplayAlerts=$false;$app.EnableEvents=$false;$app.AskToUpdateLinks=$false;$app.AutomationSecurity=3
 $book=$app.Workbooks.Open($copy,0,$false)
 try {$book.AutoSaveOn=$false} catch {}
 $book.ForceFullCalculation=$false;$app.Calculation=-4105
 $sheets=$book.Worksheets;$syn=$sheets.Item(($sheetNames.synthese));$hyp=$sheets.Item(($sheetNames.hypotheses));$plan=$sheets.Item(($sheetNames.investissements));$scope=$sheets.Item(($sheetNames.perimetre));$calc=$sheets.Item(($sheetNames.calculs));$src=$sheets.Item(($sheetNames.sources))
 Recalc
 foreach($address in @('B8','B14','B18','B19','B20','B21','B22','B23','B24','C8','C9','C15','C18','F8','G8','F9','G9','F15','G15','C23','D23','E23','F14','G14','F18','G18','F23','G23','C28','C29','C30')){
  $note=$hyp.Range($address).Comment
  if(-not $note -or [string]::IsNullOrWhiteSpace($note.Text())){throw "Infobulle Hypothèses absente ou vide : $address"}
 }
 foreach($sheet in $sheets){
  $expectedNotes=@($layout.notes | Where-Object sheet -eq $sheet.Name).Count
  if($expectedNotes -eq 0 -or $sheet.Comments.Count -ne $expectedNotes){throw "Couverture des infobulles incorrecte : $($sheet.Name)"}
 }
 foreach($r in @(18,20,21,22,24)){CompactRow $hyp $r 24}
 foreach($r in @(19,23)){CompactRow $hyp $r 38}
 foreach($r in @(8,9)){CompactRow $src $r 38}
 CompactRow $plan 24 26;CompactRow $plan 25 38
 CompactRow $syn 4 46;CompactRow $hyp 4 38;CompactRow $src 4 38
 foreach($sheet in @($syn,$hyp,$plan,$scope,$calc,$src)){
  if([double]$sheet.Range('B2').Font.Size -ne $layout.ui.sheetTitle){throw "Titre de feuille hors charte : $($sheet.Name)"}
 }
 if($expected.statut_integration_make -ne 'simulation_ancree_sap_non_calibree' -or $syn.Range('B4').Value2 -notmatch 'sans calibration' -or $hyp.Range('B4').Value2 -notmatch 'non calibrée'){throw 'Avertissement de calibration Make absent'}
 if($hyp.Range('B25').Text -ne '' -or $hyp.Range('C25').Text -ne ''){throw 'Contrôle technique visible sans erreur de saisie'}
 if($hyp.Range('B6').Value2 -notmatch ([Regex]::Escape($inputs.glossaire.notions.build_core_system.libelle)) -or $hyp.Range('B11').Value2 -notmatch ([Regex]::Escape($inputs.glossaire.notions.integration_migration.libelle)) -or $hyp.Range('B16').Value2 -notmatch ([Regex]::Escape($inputs.glossaire.notions.mco_run.libelle))){throw 'Trois tableaux de dépenses absents'}
 if($syn.Range('D6').Value2 -notmatch 'Build' -or $syn.Range('E6').Value2 -notmatch 'Intégration' -or $syn.Range('F6').Value2 -notmatch 'MCO annuel' -or $plan.Range('B26').Value2 -notmatch 'MCO annuel' -or $src.Range('B9').Value2 -notmatch 'MCO annuel'){throw 'Lecture à trois postes incohérente entre onglets'}
 for($i=0;$i -lt 5;$i++){
  $r=7+$i;$e=$expected.options[$i];$cc=[string][char](67+$i)
  Near $syn.Range("D$r").Value2 ($e.totaux_eur_ht.build/1e6) 'Build'
  Near $syn.Range("E$r").Value2 ($e.totaux_eur_ht.integration/1e6) 'Intégration'
  Near $syn.Range("F$r").Value2 ($e.totaux_eur_ht.mco_run/1e6) 'MCO'
  Near $syn.Range("G$r").Value2 ($e.totaux_eur_ht.total/1e6) 'Total'
  Near $syn.Range("H$r").Value2 $e.annees_service_complet 'Années de service'
  for($y=0;$y -lt 10;$y++){Near $plan.Range($cc+($y+7)).Value2 ($e.annees[$y].total/1e6) 'Dépense annuelle'}
 }
 Write-Output 'Référence : 5 options et 50 dépenses annuelles conformes au calcul Python.'
 for($i=0;$i -lt 3;$i++){
  $cc=[string][char](67+$i);$e=$expected.options[$i].services_annuels_reference_eur_ht
  NearK $hyp.Range($cc+'18').Value2 ($e.core/1e3) 'Entretien Core Make en k€'
  NearK $hyp.Range($cc+'19').Value2 ($e.integration/1e3) 'Entretien intégration Make en k€'
  Near $src.Range($cc+'8').Value2 ($inputs.options[$i].integration_source/1e6) 'Chiffrage par activités Make'
  NearK $hyp.Range($cc+'39').Value2 $hyp.Range($cc+'14').Value2 'Budget Make retenu dans le contrôle'
  NearK $hyp.Range($cc+'40').Value2 ($src.Range($cc+'8').Value2*1000) 'Contrepoint Make dans le contrôle'
  NearK $hyp.Range($cc+'41').Value2 ($hyp.Range($cc+'14').Value2-$src.Range($cc+'8').Value2*1000) 'Écart Make à expliquer'
 }
 foreach($cc in @('F','G')){NearK $hyp.Range($cc+'39').Value2 $hyp.Range($cc+'14').Value2 'Budget Buy dans le contrôle'}
 if(-not $hyp.Range('F18:F19').MergeCells -or -not $hyp.Range('G18:G19').MergeCells){throw 'Prestations Buy non regroupées'}
 NearK $hyp.Range('C20').Value2 72 'Hébergement Make séparé'
 NearK $hyp.Range('C21').Value2 36 'iPaaS Make séparé'
 NearK $hyp.Range('F20').Value2 30 'Compléments hébergement Microsoft'
 NearK $hyp.Range('G20').Value2 30 'Compléments hébergement SAP'
 NearK $hyp.Range('G21').Value2 100 'iPaaS SAP séparé'
 NearK $hyp.Range('G22').Value2 0 'Aucun double compte iPaaS SAP en licences'
 NearK $hyp.Range('G18').Value2 1334.24953 'Services SAP regroupés par nature'
 NearK $hyp.Range('C24').Value2 976.48192 'Total annuel Make à pleine capacité'
 NearK $hyp.Range('F24').Value2 2071.64976 'Total annuel Microsoft à pleine capacité'
 NearK $hyp.Range('G24').Value2 2735.12853 'Total annuel SAP à pleine capacité'
 NearK $hyp.Range('F23').Value2 979.00151 'Abonnement Microsoft visible'
 NearK $hyp.Range('G23').Value2 1270.879 'Abonnement SAP visible'
 if($hyp.Range('B17').Text -notmatch 'k€' -or $hyp.Range('C21').Text -notmatch '^36[,.]0$'){throw 'Unité ou précision du MCO incohérente'}
 $sf=$expected.sensibilite_finance_sap
 NearK $hyp.Range('D57').Value2 $sf.jh_finance_fpa 'JH Finance du proxy SAP'
 NearK $hyp.Range('G57').Value2 ($sf.retrait_indicatif_eur_ht/1e3) 'Retrait indicatif SAP'
 NearK $hyp.Range('G58').Value2 ($sf.integration_sap_apres_retrait_eur_ht/1e3) 'SAP indicatif après retrait'
 NearK $hyp.Range('C15').Value2 ($expected.bonus_continuite_make.taux_pct/100) 'Gain de continuité Make'
 NearK $hyp.Range('G62').Value2 ($expected.bonus_continuite_make.reduction_eur_ht/1e3) 'Gain de continuité en euros'
 NearK $hyp.Range('G63').Value2 ($expected.bonus_continuite_make.budget_apres_bonus_eur_ht/1e3) 'Pont Make après bonus'
 NearK $hyp.Range('C14').Value2 ($expected.bonus_continuite_make.budget_apres_bonus_eur_ht/1e3) 'Budget Make après bonus'
 NearK $hyp.Range('G59').Value2 ($sf.complements_sap_pilotage_preparation_retenus_dans_ancre_make_eur_ht/1e3) 'Compléments retenus dans ancre Make'
 NearK $hyp.Range('G60').Value2 ($sf.base_delaware_apres_retrait_eur_ht/1e3) 'Base Delaware après retrait'
 $pc=$expected.comparaison_prix_integration
 NearK $hyp.Range('C71').Value2 1 'Mix des profils ESN'
 if($hyp.Range('G71').Text -ne ''){throw 'Mix ESN invalide en référence'}
 NearK $hyp.Range('E65').Value2 ($sf.base_delaware_apres_retrait_eur_ht/$pc.jh_base_sap_proxy) 'Prix moyen SAP hors Finance'
 NearK $hyp.Range('F81').Value2 ($pc.cout_esn_par_profils_indicatif_eur_ht/1e3) 'Contrepoint ESN par profils'
 NearK $hyp.Range('F83').Value2 ($pc.sap_buy_avec_complements_esn_indicatif_eur_ht/1e3) 'SAP Buy aux mêmes prix ESN'
 NearK $hyp.Range('F84').Value2 ($pc.contrepoint_integrateur_avec_pilotage_eur_ht.bas/1e3) 'Stress ESN bas'
 NearK $hyp.Range('F85').Value2 ($pc.contrepoint_integrateur_avec_pilotage_eur_ht.haut/1e3) 'Stress ESN haut'
 $oldProfileRate=$hyp.Range('E67').Value2;$oldEsn=$hyp.Range('F81').Value2;$oldActive=$hyp.Range('C14').Value2
 $hyp.Range('E67').Value2=$oldProfileRate+10;Recalc
 if($hyp.Range('F81').Value2 -le $oldEsn){throw 'TJM fonctionnel ESN sans effet'}
 NearK $hyp.Range('C14').Value2 $oldActive 'Contrepoint ESN indépendant du budget actif'
 $hyp.Range('E67').Value2=$oldProfileRate;Recalc
 foreach($cc in @('C','D','E')){NearK $hyp.Range($cc+'14').Value2 ($hyp.Range('G58').Value2*(1-$hyp.Range('C15').Value2)) 'Ancre Make après bonus'}
 $oldBonus=$hyp.Range('C15').Value2;$baseMake=$syn.Range('E7').Value2;$baseBuy=$syn.Range('E10').Value2
 $hyp.Range('C15').Value2=0;Recalc
 foreach($cc in @('C','D','E')){NearK $hyp.Range($cc+'14').Value2 $hyp.Range('G58').Value2 'Bonus nul : budget Make avant gain'}
 NearK $hyp.Range('G62').Value2 0 'Bonus nul : gain en euros'
 NearK $hyp.Range('G63').Value2 $hyp.Range('G58').Value2 'Bonus nul : budget après gain'
 Near $syn.Range('E7').Value2 ($hyp.Range('G58').Value2/1000) 'Bonus nul propagé à la synthèse'
 Near $syn.Range('E10').Value2 $baseBuy 'Budget Buy indépendant du bonus Make'
 $hyp.Range('C15').Value2=0.2;Recalc
 NearK $hyp.Range('C14').Value2 (0.8*$hyp.Range('G58').Value2) 'Bonus Make modifiable'
 NearK $hyp.Range('G62').Value2 (0.2*$hyp.Range('G58').Value2) 'Gain en euros modifiable'
 NearK $hyp.Range('G63').Value2 $hyp.Range('C14').Value2 'Budget du pont modifiable'
 $hyp.Range('C15').ClearContents();Recalc
 if($hyp.Range('C25').Value2 -ne 'À corriger' -or $hyp.Range('F25').Value2 -ne ''){throw 'Bonus Make manquant non détecté ou Buy affecté'}
 $hyp.Range('C15').Value2=$oldBonus;Recalc
 Near $syn.Range('E7').Value2 $baseMake 'Bonus de référence restauré'
 $oldSap=$hyp.Range('G14').Value2;$hyp.Range('G14').Value2=$oldSap+1;Recalc
 NearK $hyp.Range('G58').Value2 ($sf.integration_sap_apres_retrait_eur_ht/1e3+1) 'Sensibilité SAP liée au budget modifiable'
 NearK $hyp.Range('G60').Value2 ($sf.base_delaware_apres_retrait_eur_ht/1e3+1) 'Sensibilité Delaware liée au budget SAP'
 foreach($cc in @('C','D','E')){NearK $hyp.Range($cc+'14').Value2 ($hyp.Range('G58').Value2*(1-$oldBonus)) 'Ancre SAP après bonus propagée à Make'}
 $hyp.Range('G14').Value2=$oldSap;Recalc
 $oldIpaas=$hyp.Range('G21').Value2;$beforeCloud=$calc.Range('F77').Value2
 $hyp.Range('G21').Value2=$oldIpaas+10;Recalc
 Near $calc.Range('F77').Value2 ($beforeCloud+0.01*[Math]::Pow(1+$hyp.Range('C29').Value2,3)) 'Simulation iPaaS SAP et indexation logiciel'
 Near $calc.Range('F79').Value2 0 'iPaaS non dupliqué en licences complémentaires'
 $hyp.Range('G21').Value2=$oldIpaas;Recalc
 $oldLicense=$hyp.Range('F22').Value2;$hyp.Range('F22').ClearContents();Recalc
 if($hyp.Range('F25').Value2 -ne 'À corriger'){throw 'Licence complémentaire manquante masquée'}
 if($hyp.Range('B25').Value2 -ne 'Saisie à corriger'){throw 'Alerte de saisie absente'}
 $hyp.Range('F22').Value2=$oldLicense;Recalc
 $baseline=$syn.Range('G7').Value2
 $hyp.Range('C8').Value2=36; Recalc
 Near $plan.Range('C7').Value2 ($hyp.Range('C9').Value2/3/1000) 'Build sur trois ans, conversion k€ vers M€'
 if ($syn.Range('G7').Value2 -le $baseline) { throw 'Durée de build non propagée au MCO' }
 $series=$plan.ChartObjects(1).Chart.SeriesCollection(1).Values
 Near $series.GetValue($series.GetLowerBound(0)) $plan.Range('C7').Value2 'Graphique lié au scénario'
 $hyp.Range('C8').Value2=48
 $hyp.Range('F13').Value2=50; Recalc
 foreach($c in @('C','D','E')){NearK $hyp.Range($c+'13').Value2 40 'Moyenne durée Make'}
 $hyp.Range('F13').Value2=38
 $oldCost=$hyp.Range('F14').Value2;$oldMake=$hyp.Range('C14').Value2;$oldGap=$hyp.Range('C41').Value2;$hyp.Range('F14').Value2=$oldCost+2;Recalc
 foreach($c in @('C','D','E')){NearK $hyp.Range($c+'14').Value2 $oldMake 'Microsoft sans poids dans le coût Make'}
 NearK $hyp.Range('C41').Value2 $oldGap 'Contrôle Make indépendant de Microsoft'
 $hyp.Range('F14').Value2=$oldCost
 $oldRate=$hyp.Range('C29').Value2;$hyp.Range('C29').Value2=0;Recalc
 Near $calc.Range('G62').Value2 0.97900151 'Microsoft prix RFI an 5'
 Near $calc.Range('H62').Value2 0.97900151 'Microsoft inflation an 6'
 Near $calc.Range('E78').Value2 1.270879 'SAP inflation après séquence documentée'
 $hyp.Range('C29').Value2=$oldRate
 $oldRate=$hyp.Range('C28').Value2;$hyp.Range('C28').Value2=0;Recalc
 if ($syn.Range('G7').Value2 -ge $baseline) { throw 'Inflation services non propagée' }
 $hyp.Range('C28').Value2=$oldRate
 $hyp.Range('C8').ClearContents();Recalc
 if ($hyp.Range('C25').Value2 -ne 'À corriger') { throw 'Entrée manquante masquée' }
 $hyp.Range('C8').Value2=48
 $oldService=$hyp.Range('C18').Value2;$hyp.Range('C18').Value2=0;Recalc
 if ($hyp.Range('C25').Text -ne '') { throw 'Zéro explicite refusé' }
 if ($syn.Range('G7').Value2 -ge $baseline) { throw 'Zéro explicite non propagé' }
 $hyp.Range('C18').Value2=$oldService
 $hyp.Range('C8').Value2=60;$hyp.Range('F13').Value2=60;$hyp.Range('G13').Value2=60;Recalc
 Near $syn.Range('H7').Value2 0 'Fin intégration à dix ans'
 Near $syn.Range('F7').Value2 0 'Absence de MCO fictif après la fenêtre'
 $hyp.Range('C8').Value2=48;$hyp.Range('F13').Value2=38;$hyp.Range('G13').Value2=30
 $plan.Range('C21').Value2=$inputs.glossaire.options.rust.libelle;Recalc
 Near $plan.Range('C24').Value2 ($hyp.Range('E9').Value2/4/1000) 'Sélecteur détail Rust'
 $plan.Range('C21').Value2=$inputs.glossaire.options.'java-spring'.libelle;Recalc
 Near $syn.Range('G7').Value2 $baseline 'Restauration scénario de référence'
 # Excel AutoFit ignores merged prose. Measure the same text/font in one ordinary
 # scratch cell with the exact target width, then remove the scratch sheet.
 $measureSheet=$sheets.Add();$measureSheet.Name='_LayoutMeasure'
 try {
  $measureCell=$measureSheet.Range('A1');$measureCell.WrapText=$true
  $measureColumn=$measureSheet.Columns.Item(1)
  foreach($entry in $layout.fit){
   $sheet=$sheets.Item($entry.sheet);$needed=[double]$entry.minHeight;$row=$null
   foreach($address in $entry.addresses){
    $target=$sheet.Range($address);$cell=$target.Cells.Item(1,1);$row=$cell.Row
    $text=[string]$cell.Text
    if([string]::IsNullOrWhiteSpace($text)){continue}
    $targetWidth=[Math]::Max(10,[double]$target.Width-1)
    $measureColumn.ColumnWidth=40
    for($pass=0;$pass -lt 2;$pass++){$measureColumn.ColumnWidth=[Math]::Min(255,[double]$measureColumn.ColumnWidth*$targetWidth/[double]$measureColumn.Width)}
    $measureCell.Formula="'"+$text
    $measureCell.Font.Name=[string]$cell.Font.Name
    $measureCell.Font.Size=[double]$cell.Font.Size
    $measureCell.Font.Bold=[bool]$cell.Font.Bold
    $null=$measureCell.EntireRow.AutoFit()
    $needed=[Math]::Max($needed,[double]$measureCell.RowHeight+2)
   }
   if($needed -gt 409){throw "Texte trop long pour une ligne Excel : $($entry.sheet) / $row"}
   if($row){$sheet.Rows.Item($row).RowHeight=[Math]::Ceiling($needed)}
  }
 } finally {$null=$measureSheet.Delete();$measureSheet=$null}
 if($sheets.Count -ne 6){throw 'Feuille temporaire de mesure conservée'}
 # Verify the visual roles across all six sheets, not only the first sponsor view.
 foreach($meta in $layout.sheets){
  $s=$sheets.Item($meta.name)
  if($s.Range('B2').Font.Name -ne $layout.ui.font -or $s.Range('B2').Font.Size -ne $layout.ui.sheetTitle){throw "Titre hors charte : $($meta.name)"}
  if($s.Range('B4').Interior.Color -ne (OleColor $layout.ui.introFill)){throw "Encart introductif hors charte : $($meta.name)"}
 }
 foreach($meta in $layout.headers){
  $cell=$sheets.Item($meta.sheet).Range($meta.address).Cells.Item(1,1)
  if($cell.Font.Name -ne $layout.ui.font -or $cell.Font.Size -ne $layout.ui.headerFont -or $cell.Interior.Color -ne (OleColor $layout.ui.ink) -or $cell.Font.Color -ne 16777215){throw "En-tête hors charte : $($meta.sheet) / $($meta.address)"}
 }
 foreach($meta in $layout.sections){
  $cell=$sheets.Item($meta.sheet).Range($meta.address).Cells.Item(1,1)
  if($cell.Interior.Color -ne 16777215 -or -not $cell.Font.Bold){throw "Titre de section hors charte : $($meta.sheet) / $($meta.address)"}
 }
 foreach($pair in @(@($hyp,'C8'),@($hyp,'C15'),@($plan,'C21'))){if($pair[0].Range($pair[1]).Interior.Color -ne (OleColor $layout.ui.input)){throw 'Entrée modifiable sans repère jaune'}}
 foreach($pair in @(@($hyp,'C13'),@($src,'C7'))){if($pair[0].Range($pair[1]).Interior.Color -eq (OleColor $layout.ui.input)){throw 'Cellule en lecture seule présentée comme une entrée'}}
 Write-Output 'Finition : six onglets, titres, en-têtes, sections et textes longs contrôlés dans Excel.'
 # Imported VML note shapes can make Range.CopyPicture fail. Their source bodies
 # are in the generated manifest; export the views cleanly, then add native ScreenTips.
 $nativeNotes=@($layout.notes)
 foreach($sheet in $sheets){$null=$sheet.Cells.ClearComments()}
 $areas=@{($sheetNames.synthese)='B2:H36';($sheetNames.hypotheses)='B2:G87';($sheetNames.investissements)='B2:L46';($sheetNames.perimetre)='B2:E23';($sheetNames.calculs)='B2:L82';($sheetNames.sources)='B2:G86'}
 foreach($s in $sheets){
  foreach($v in $s.UsedRange.Value2){
   if($s.Name -ne ($sheetNames.sources) -and $v -is [string] -and $v -match '\bRFI\b'){throw "RFI présenté hors provenance dans $($s.Name)"}
   if($s.Name -eq ($sheetNames.hypotheses) -and $v -is [string] -and $v -match 'M€'){throw 'Plusieurs échelles monétaires dans Hypothèses'}
   if ($v -is [Runtime.InteropServices.ErrorWrapper] -or ($v -is [int] -and $v -ge -2146826288 -and $v -le -2146826240)){throw "Erreur Excel dans $($s.Name)"}
  }
  # Aucune dépendance à un pilote d'impression pour vérifier le classeur interactif.
  $s.Activate();$app.ActiveWindow.DisplayGridlines=$false;$app.ActiveWindow.FreezePanes=$false;$app.ActiveWindow.Zoom=100;$s.Range('B2').Select()
 }
 if($plan.ChartObjects().Count -ne 1 -or $plan.ChartObjects(1).Chart.SeriesCollection().Count -ne 5){throw 'Graphique annuel incomplet'}
 if($syn.ChartObjects().Count -ne 1){throw 'Graphique synthèse absent'}
 foreach($chart in @($syn.ChartObjects(1).Chart,$plan.ChartObjects(1).Chart)){
  $chart.ChartArea.Format.Line.Visible=0;$chart.PlotArea.Format.Line.Visible=0
  $chart.ChartTitle.Font.Name=$layout.ui.font;$chart.ChartTitle.Font.Size=[double]$layout.ui.chartTitle
  $chart.ChartTitle.Font.Color=(OleColor $layout.ui.ink)
  foreach($axisType in @(1,2)){
   $axis=$chart.Axes($axisType)
   $axis.Format.Line.Visible=0
   $axis.TickLabels.Font.Name=$layout.ui.font;$axis.TickLabels.Font.Size=[double]$layout.ui.note
   $axis.TickLabels.Font.Color=(OleColor $layout.ui.muted)
   $axis.HasMajorGridlines=($axisType -eq 2)
   if($axisType -eq 2){$axis.MajorGridlines.Format.Line.ForeColor.RGB=(OleColor $layout.ui.border);$axis.MajorGridlines.Format.Line.DashStyle=1;$axis.MajorGridlines.Format.Line.Weight=0.5}
  }
  if($chart.HasLegend){$chart.Legend.Font.Name=$layout.ui.font;$chart.Legend.Font.Size=[double]$layout.ui.note}
 }
 $summarySeries=$syn.ChartObjects(1).Chart.SeriesCollection(1)
 $null=$summarySeries.ApplyDataLabels(2)
 $summarySeries.DataLabels().NumberFormat='0.0';$summarySeries.DataLabels().Position=2
 $summarySeries.DataLabels().Font.Name=$layout.ui.font;$summarySeries.DataLabels().Font.Size=[double]$layout.ui.body
 $summarySeries.DataLabels().Font.Color=(OleColor $layout.ui.ink)
 for($i=1;$i -le 5;$i++){
  $summarySeries.Points($i).Format.Fill.ForeColor.RGB=(OleColor $layout.ui.optionColors[$i-1])
  $summarySeries.Points($i).Format.Line.Visible=0
 }
 $plan.Activate();$null=$plan.ChartObjects(1).Activate();$null=$plan.ChartObjects(1).Chart.Refresh()
 if(-not $plan.ChartObjects(1).Chart.Export((Join-Path $root 'tmp/investissement-10-ans/chart-native.png'),'PNG')){throw 'Export graphique annuel impossible'}
 $syn.Activate();$null=$syn.ChartObjects(1).Activate();$null=$syn.ChartObjects(1).Chart.Refresh()
 if(-not $syn.ChartObjects(1).Chart.Export((Join-Path $root 'tmp/investissement-10-ans/summary-chart-native.png'),'PNG')){throw 'Export graphique synthèse impossible'}
 # Export actual Excel-rendered ranges at 100% for the compact-layout review.
 if($env:FLOW_NATIVE_PREVIEW -eq '1'){
  $views=@(
   @(($sheetNames.synthese),'B2:H19','synthese'),@(($sheetNames.hypotheses),'B2:G9','hypotheses-build'),@(($sheetNames.hypotheses),'B11:G15','hypotheses-integration'),@(($sheetNames.hypotheses),'B16:G24','hypotheses-mco'),
  @(($sheetNames.hypotheses),'B27:G35','hypotheses-notes'),@(($sheetNames.hypotheses),'B37:G51','hypotheses-controle'),@(($sheetNames.hypotheses),'B53:G63','hypotheses-finance-sap'),@(($sheetNames.hypotheses),'B64:G87','hypotheses-prix-esn'),@(($sheetNames.investissements),'B2:L27','investissements'),
   @(($sheetNames.perimetre),'B2:E23','perimetre'),@(($sheetNames.calculs),'B2:L18','calculs-entree'),@(($sheetNames.calculs),'B70:L82','calculs'),
   @(($sheetNames.sources),'B2:G25','sources'),@(($sheetNames.sources),'B27:G50','sources-notes-1'),@(($sheetNames.sources),'B52:G76','sources-notes-2'),@(($sheetNames.sources),'B78:G84','sources-prix-esn'),@(($sheetNames.sources),'B86:G86','sources-eweb')
  )
  foreach($v in $views){
   $sheet=$sheets.Item($v[0]);$sheet.Activate();$app.ActiveWindow.Zoom=100
   $range=$sheet.Range($v[1]);$range.Select()
   $pictureCopied=$false
   for($attempt=1;$attempt -le 3;$attempt++){
    try {$copyFormat=if($attempt -eq 1){2}else{-4147};$null=$range.CopyPicture(1,$copyFormat);$pictureCopied=$true;break}
    catch {if($attempt -eq 3){throw "Aperçu $($v[0]) $($v[1]) impossible : $($_.Exception.Message)"};$app.CutCopyMode=0;Start-Sleep -Milliseconds 250;$sheet.Activate();$range.Select()}
   }
   if(-not $pictureCopied){throw "Aperçu non copié : $($v[0])"}
   $preview=$sheet.ChartObjects().Add(0,0,$range.Width,$range.Height)
   $null=$preview.Activate();$null=$preview.Chart.Paste()
   $previewPath=Join-Path $root ('tmp/investissement-10-ans/excel-'+$v[2]+'.png')
   if(-not $preview.Chart.Export($previewPath,'PNG')){throw "Rendu Excel impossible : $($v[0])"}
   $null=$preview.Delete();$app.CutCopyMode=0
  }
 }
 if($env:FLOW_NATIVE_PREVIEW -eq 'screen'){Write-Output 'Contrôle visuel à terminer dans les six onglets Excel natifs à 100 %.'}
 # Classic notes can overflow, and modern comments show a collapsed preview on hover.
 # An inactive hyperlink has a complete native ScreenTip without navigation or macros.
 if($layout.ui.tooltip.kind -ne 'screenTip'){throw "Type d’infobulle non pris en charge"}
 foreach($entry in $nativeNotes){
  if(([string]$entry.body).Length -gt $layout.ui.tooltip.maxCharacters){throw "Infobulle trop longue : $($entry.sheet) / $($entry.address)"}
  $cell=$sheets.Item($entry.sheet).Range($entry.address)
  if($cell.Hyperlinks.Count -ne 0){throw "Lien existant à préserver : $($entry.sheet) / $($entry.address)"}
  $originalFormula=$cell.Formula;$originalFormat=$cell.NumberFormat
  $font=$cell.Font
  $style=@{Name=$font.Name;Size=$font.Size;Bold=$font.Bold;Italic=$font.Italic;Underline=$font.Underline;Color=$font.Color}
  # No Address, SubAddress or TextToDisplay: blank cells stay blank and clicking
  # does not navigate. Restore typed values/formulas and the original cell font.
  $tip=$sheets.Item($entry.sheet).Hyperlinks.Add($cell,'','',[string]$entry.body)
  if([string]$originalFormula -ne ''){$cell.Formula=$originalFormula}
  $cell.NumberFormat=$originalFormat
  $font=$cell.Font
  $font.Name=[string]$style.Name;$font.Size=[double]$style.Size
  $font.Bold=[bool]$style.Bold;$font.Italic=[bool]$style.Italic
  $font.Underline=[int]$style.Underline;$font.Color=[int]$style.Color
  if($cell.Hyperlinks.Count -ne 1 -or $tip.ScreenTip -cne [string]$entry.body -or $tip.Address -or $tip.SubAddress){throw "Infobulle inactive altérée : $($entry.sheet) / $($entry.address)"}
  if($cell.Font.Color -ne $style.Color -or $cell.Font.Underline -ne $style.Underline -or $cell.Font.Size -ne $style.Size -or $cell.Formula -cne $originalFormula){throw "Cellule modifiée par son infobulle : $($entry.sheet) / $($entry.address)"}
 }
 foreach($sheet in $sheets){
  if($sheet.Comments.Count -ne 0 -or $sheet.CommentsThreaded.Count -ne 0 -or $sheet.Hyperlinks.Count -ne @($layout.notes | Where-Object sheet -eq $sheet.Name).Count){throw "Infobulles perdues à la conversion : $($sheet.Name)"}
 }
 # Editing an input must retain both its numeric type and its explanatory tip.
 $originalInput=$hyp.Range('C21').Value2
 $inputTip=$hyp.Range('C21').Hyperlinks.Item(1).ScreenTip
 $hyp.Range('C21').Value2=72.0;Recalc
 NearK $hyp.Range('C21').Value2 72 'Saisie conservée avec infobulle'
 if($hyp.Range('C21').Hyperlinks.Item(1).ScreenTip -cne $inputTip){throw "Infobulle perdue après modification d’une entrée"}
 $hyp.Range('C21').Value2=$originalInput;Recalc
 Write-Output ("Infobulles : "+$nativeNotes.Count+' ScreenTips inactifs, textes et cellules contrôlés sur six onglets.')
 # Range previews leave large selected areas. Restore a neutral opening view everywhere.
 foreach($s in $sheets){$s.Activate();$s.Range('B2').Select();$app.ActiveWindow.Zoom=100;$app.ActiveWindow.ScrollRow=1;$app.ActiveWindow.ScrollColumn=1}
 $syn.Activate();$syn.Range('B2').Select();$book.Save()
 # Verify persistence in the saved XLSX, rather than only the in-memory COM objects.
 $book.Close($false);$book=$app.Workbooks.Open($copy,0,$false);$sheets=$book.Worksheets
 foreach($sheet in $sheets){
  if($sheet.Comments.Count -ne 0 -or $sheet.CommentsThreaded.Count -ne 0 -or $sheet.Hyperlinks.Count -ne @($layout.notes | Where-Object sheet -eq $sheet.Name).Count){throw "Infobulles perdues après réouverture : $($sheet.Name)"}
 }
 foreach($entry in $nativeNotes){
  $tip=$sheets.Item($entry.sheet).Range($entry.address).Hyperlinks.Item(1)
  if($tip.ScreenTip -cne [string]$entry.body -or $tip.Address -or $tip.SubAddress){throw "Infobulle altérée après sauvegarde : $($entry.sheet) / $($entry.address)"}
 }
 $null=New-Item -ItemType Directory -Path (Split-Path $dest) -Force
 $book.Close($false);$book=$null
 AssertDestinationAvailable
 Copy-Item -LiteralPath $copy -Destination $dest -Force
 Write-Output 'OK : ouverture normale, recalcul, tests de propagation, sources RFI préservées, aucun défaut de formule.'
 Write-Output $dest
} finally {
 if($book){try {$book.Close($false)} catch {}}
 foreach($x in @($src,$calc,$scope,$plan,$hyp,$syn,$sheets)){if($x){try {$null=[Runtime.InteropServices.Marshal]::FinalReleaseComObject($x)} catch {}}}
 if($app){try {$app.Quit()} catch {};try {$null=[Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)} catch {}}
 [GC]::Collect();[GC]::WaitForPendingFinalizers()
 if(Test-Path -LiteralPath $copy){try {Remove-Item -LiteralPath $copy -Force} catch {}}
}
$activeDestination=Join-Path $root 'outputs/01a15da9-73b2-7760-8111-3c718f6245f3/FLOW_Investissements_10_ans_Integration_Migration.xlsx'
if([string]::Equals($dest,$activeDestination,[StringComparison]::OrdinalIgnoreCase)){
 $excelPath=Get-ItemPropertyValue -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\excel.exe' -Name '(default)' -ErrorAction SilentlyContinue
 if(-not $excelPath -or -not (Test-Path -LiteralPath $excelPath)){throw 'Livrable vérifié, mais Microsoft Excel est introuvable pour son ouverture visible'}
 # Windows PowerShell exposes Marshal.GetActiveObject; reuse the running Excel window,
 # including an empty one, instead of launching an additional blank instance.
 $env:FLOW_WORKBOOK_TO_OPEN=$dest
 $reuseScript='$ErrorActionPreference="Stop";try{$x=[Runtime.InteropServices.Marshal]::GetActiveObject("Excel.Application");$x.Visible=$true;$null=$x.Workbooks.Open($env:FLOW_WORKBOOK_TO_OPEN,0,$false);$x.ActiveWindow.Activate();exit 0}catch{exit 2}'
 $encoded=[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($reuseScript))
 & powershell.exe -NoProfile -EncodedCommand $encoded
 $reused=($LASTEXITCODE -eq 0)
 Remove-Item Env:FLOW_WORKBOOK_TO_OPEN
 if(-not $reused){
  Start-Process -FilePath $excelPath -ArgumentList ('"'+$dest+'"')
 }
 Write-Output "Ouvert dans Microsoft Excel : $dest"
}
