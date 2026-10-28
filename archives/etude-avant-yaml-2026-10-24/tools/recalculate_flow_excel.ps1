param(
    [string]$Source = 'outputs/01a1530f-f378-7fd1-9654-468c9b2141b6/FLOW_Make_abaques_et_prix_France_v4.xlsx',
    [string]$Destination = 'tmp/FLOW_native_v4_final.xlsx',
    [string]$ChartExport = ''
)

$ErrorActionPreference = 'Stop'
$workspacePath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$sourcePath = if ([IO.Path]::IsPathRooted($Source)) { [IO.Path]::GetFullPath($Source) } else { [IO.Path]::GetFullPath((Join-Path $workspacePath $Source)) }
$destinationPath = if ([IO.Path]::IsPathRooted($Destination)) { [IO.Path]::GetFullPath($Destination) } else { [IO.Path]::GetFullPath((Join-Path $workspacePath $Destination)) }
$workspacePrefix = $workspacePath.TrimEnd('\') + '\'
if (-not $destinationPath.StartsWith($workspacePrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'The disposable destination must stay in the workspace.' }
if ($sourcePath.Equals($destinationPath, [StringComparison]::OrdinalIgnoreCase)) { throw 'The original workbook must never be overwritten.' }
if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) { throw 'Source workbook not found.' }
$sourceSha256 = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash
$destinationParent = Split-Path -Parent $destinationPath
if (-not (Test-Path -LiteralPath $destinationParent -PathType Container)) { $null = New-Item -ItemType Directory -Path $destinationParent }
Copy-Item -LiteralPath $sourcePath -Destination $destinationPath -Force

$excelInstance = $null
$workbooks = $null
$workbook = $null
$worksheets = $null
$started = Get-Date
function Write-TestStage([string]$stage) {
    [Console]::WriteLine(('{0:o} {1}' -f (Get-Date), $stage))
    [Console]::Out.Flush()
}
try {
    # Create a separate hidden process; never attach to an existing Excel instance.
    Write-TestStage 'CREATE_SEPARATE_EXCEL'
    $excelInstance = New-Object -ComObject Excel.Application
    $excelInstance.Visible = $false
    $excelInstance.DisplayAlerts = $false
    $excelInstance.AskToUpdateLinks = $false
    $excelInstance.EnableEvents = $false
    $excelInstance.AutomationSecurity = 3
    $workbooks = $excelInstance.Workbooks
    # UpdateLinks=0; ReadOnly=false applies only to the disposable copy.
    Write-TestStage 'OPEN_DISPOSABLE_COPY'
    $workbook = $workbooks.Open($destinationPath, 0, $false)
    Write-TestStage 'OPEN_COMPLETED'
    # The workspace is under OneDrive. Disable automatic cloud saves for this
    # disposable workbook so an upload cannot hold up the local verification.
    try { $workbook.AutoSaveOn = $false } catch { }
    $workbook.CheckCompatibility = $false
    # The exported model requests a complete calculation on load. On the
    # disposable copy, clear the perpetual force flag before an explicit rebuild.
    $workbook.ForceFullCalculation = $false
    $excelInstance.Calculation = -4105
    Write-TestStage 'CALCULATE_FULL_REBUILD'
    $excelInstance.CalculateFullRebuild()
    Write-TestStage 'REBUILD_RETURNED'
    $deadline = (Get-Date).AddSeconds(45)
    while ($excelInstance.CalculationState -ne 0) {
        if ((Get-Date) -gt $deadline) { throw 'Native Excel calculation exceeded 45 seconds after the rebuild returned.' }
        Start-Sleep -Milliseconds 250
    }
    $nativeSheets = @()
    $headlines = @{}
    $nativeGuardFailures = @()
    $nativeUnitFailures = @()
    $worksheets = $workbook.Worksheets
    for ($sheetIndex = 1; $sheetIndex -le $worksheets.Count; $sheetIndex++) {
        $sheet = $null
        $usedRange = $null
        try {
            $sheet = $worksheets.Item($sheetIndex)
            $usedRange = $sheet.UsedRange
            $values = $usedRange.Value2
            $errorCount = 0
            foreach ($cellValue in $values) {
                if ($cellValue -is [Runtime.InteropServices.ErrorWrapper] -or ($cellValue -is [int] -and $cellValue -ge -2146826288 -and $cellValue -le -2146826240)) { $errorCount++ }
            }
            $nativeSheets += [pscustomobject]@{ name = $sheet.Name; errorCount = $errorCount }
            if ($sheet.Name -eq 'Charges Flow') {
                foreach ($guardRow in 8..21) {
                    $guardRange = $null
                    try {
                        $guardRange = $sheet.Range('I' + $guardRow)
                        if ($guardRange.Value2 -ne 'OK') { $nativeGuardFailures += ('Charges Flow!I' + $guardRow + ': ' + $guardRange.Text) }
                    }
                    finally { if ($null -ne $guardRange) { $null = [Runtime.InteropServices.Marshal]::FinalReleaseComObject($guardRange) } }
                }
            }
            if ($sheet.Name -eq 'Comparaison') {
                foreach ($address in @('D9', 'E9', 'F9', 'G9', 'H9', 'I9', 'D10', 'E10', 'I10', 'D11', 'E11', 'I11', 'D12', 'E12', 'I12')) {
                    $headlineRange = $null
                    try {
                        $headlineRange = $sheet.Range($address)
                        $headlines[$address] = @{ value = $headlineRange.Value2; text = $headlineRange.Text }
                        if ($address -match '^[DEFGHI](9|10|11)$' -and $headlineRange.Value2 -is [double]) {
                            if ($headlineRange.Text -notmatch ('M' + [char]0x20AC)) { $nativeUnitFailures += ('Comparaison!' + $address + ': currency unit absent from ' + $headlineRange.Text) }
                            if ($address.StartsWith('E') -and $headlineRange.Text -notmatch '/an') { $nativeUnitFailures += ('Comparaison!' + $address + ': annual unit absent from ' + $headlineRange.Text) }
                        }
                    }
                    finally { if ($null -ne $headlineRange) { $null = [Runtime.InteropServices.Marshal]::FinalReleaseComObject($headlineRange) } }
                }
            }
        }
        finally {
            if ($null -ne $usedRange) { $null = [Runtime.InteropServices.Marshal]::FinalReleaseComObject($usedRange) }
            if ($null -ne $sheet) { $null = [Runtime.InteropServices.Marshal]::FinalReleaseComObject($sheet) }
        }
    }
    $nativeReport = [pscustomobject]@{ sourceSha256 = $sourceSha256; calculationState = $excelInstance.CalculationState; sheets = $nativeSheets; headlines = $headlines; guardFailures = $nativeGuardFailures; unitFailures = $nativeUnitFailures }
    $nativeReport | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath ($destinationPath + '.native-report.json') -Encoding utf8
    [Console]::WriteLine(($nativeReport | ConvertTo-Json -Depth 6 -Compress))
    [Console]::Out.Flush()
    $errorSheets = @($nativeSheets | Where-Object { $_.errorCount -gt 0 })
    if ($errorSheets.Count -gt 0) { throw ('Native Excel formula errors: ' + (($errorSheets | ForEach-Object { $_.name + '=' + $_.errorCount }) -join ', ')) }
    if ($nativeGuardFailures.Count -gt 0) { throw ('Native Excel allocation guards failed: ' + ($nativeGuardFailures -join ', ')) }
    if ($nativeUnitFailures.Count -gt 0) { throw ('Native Excel displayed units failed: ' + ($nativeUnitFailures -join ', ')) }
    if ($ChartExport) {
        $chartPath = [IO.Path]::GetFullPath((Join-Path $workspacePath $ChartExport))
        if (-not $chartPath.StartsWith($workspacePrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Chart export must stay in workspace.' }
        $chartSheet = $null; $chartObjects = $null; $chartObject = $null; $nativeChart = $null
        try {
            $chartSheet = $worksheets.Item('Comparaison')
            $chartObjects = $chartSheet.ChartObjects()
            $chartObject = $chartObjects.Item(1)
            $nativeChart = $chartObject.Chart
            if (-not $nativeChart.Export($chartPath, 'PNG')) { throw 'Native chart export failed.' }
            Write-TestStage 'NATIVE_CHART_EXPORTED'
        }
        finally {
            foreach ($chartCom in @($nativeChart, $chartObject, $chartObjects, $chartSheet)) {
                if ($null -ne $chartCom) { $null = [Runtime.InteropServices.Marshal]::FinalReleaseComObject($chartCom) }
            }
        }
    }
    Write-TestStage ('CALCULATION_STATE_' + $excelInstance.CalculationState)
    Write-TestStage 'SAVE_DISPOSABLE_COPY'
    $workbook.Save()
    Write-TestStage 'SAVE_COMPLETED'
    [pscustomobject]@{
        status = 'NATIVE_RECALC_SAVED'
        excelVersion = $excelInstance.Version
        source = $sourcePath
        sourceSha256 = $sourceSha256
        disposableCopy = $destinationPath
        elapsedSeconds = [Math]::Round(((Get-Date) - $started).TotalSeconds, 2)
    } | ConvertTo-Json -Compress
}
finally {
    if ($null -ne $workbook) {
        Write-TestStage 'CLOSE_DISPOSABLE_COPY'
        try { $workbook.Close($false) } catch { }
        $null = [Runtime.InteropServices.Marshal]::FinalReleaseComObject($workbook)
    }
    if ($null -ne $workbooks) { $null = [Runtime.InteropServices.Marshal]::FinalReleaseComObject($workbooks) }
    if ($null -ne $worksheets) { $null = [Runtime.InteropServices.Marshal]::FinalReleaseComObject($worksheets) }
    if ($null -ne $excelInstance) {
        Write-TestStage 'QUIT_SEPARATE_EXCEL'
        try { $excelInstance.Quit() } catch { }
        $null = [Runtime.InteropServices.Marshal]::FinalReleaseComObject($excelInstance)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
    Write-TestStage 'CLEANUP_COMPLETED'
}
