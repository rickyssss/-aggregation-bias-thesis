# Adds statistical-significance flags (alpha=0.05, two-tailed) to results/summary_table.csv
# based on sample size (n) embedded in coarse_level/fine_level text and r embedded in coarse_stat/fine_stat.

$ErrorActionPreference = "Stop"

# Critical t-values for df = 1..30 at alpha=0.05 two-tailed (standard t-table)
$tTable = @{
    1=12.706; 2=4.303; 3=3.182; 4=2.776; 5=2.571; 6=2.447; 7=2.365; 8=2.306; 9=2.262; 10=2.228;
    11=2.201; 12=2.179; 13=2.160; 14=2.145; 15=2.131; 16=2.120; 17=2.110; 18=2.101; 19=2.093; 20=2.086;
    21=2.080; 22=2.074; 23=2.069; 24=2.064; 25=2.060; 26=2.056; 27=2.052; 28=2.048; 29=2.045; 30=2.042
}

function Get-CriticalT($df) {
    if ($df -le 0) { return $null }
    if ($df -le 30) { return $tTable[$df] }
    return 1.96 + (2.042 - 1.96) * [Math]::Max(0, (30.0 / $df))
}

function Test-Significant($r, $n) {
    if ($null -eq $r -or $null -eq $n -or $n -lt 4) { return "n/a" }
    $df = $n - 2
    if ($df -le 0) { return "n/a" }
    $absR = [Math]::Abs($r)
    if ($absR -ge 0.999999) { return "yes" }
    $t = $absR * [Math]::Sqrt($df / (1 - $absR * $absR))
    $tCrit = Get-CriticalT $df
    if ($t -ge $tCrit) { return "yes" } else { return "no" }
}

$inPath = "C:\Users\saika\-aggregation-bias-thesis\results\summary_table.csv"
$rows = Import-Csv -Path $inPath

$output = foreach ($row in $rows) {
    $coarseLevel = $row.coarse_level
    $fineLevel = $row.fine_level
    $coarseStat = $row.coarse_stat
    $fineStat = $row.fine_stat

    $nCoarse = $null; $nFine = $null; $rCoarse = $null; $rFine = $null

    if ($coarseLevel -match 'n=(\d+)') { $nCoarse = [int]$Matches[1] }
    if ($fineLevel -match 'n=(\d+)') { $nFine = [int]$Matches[1] }
    if ($coarseStat -match 'corr=(-?[\d.]+)') { $rCoarse = [double]$Matches[1] }
    if ($fineStat -match 'corr=(-?[\d.]+)') { $rFine = [double]$Matches[1] }

    $coarseSig = if ($coarseStat -match 'corr=') { Test-Significant $rCoarse $nCoarse } else { "n/a(not_corr)" }
    $fineSig = if ($fineStat -match 'corr=') { Test-Significant $rFine $nFine } else { "n/a(not_corr)" }

    [PSCustomObject]@{
        id = $row.id
        country = $row.country
        variable = $row.variable
        coarse_level = $coarseLevel
        coarse_stat = $coarseStat
        fine_level = $fineLevel
        fine_stat = $fineStat
        diff_type = $row.diff_type
        notes = $row.notes
        coarse_significant_p05 = $coarseSig
        fine_significant_p05 = $fineSig
    }
}

$outPath = "C:\Users\saika\-aggregation-bias-thesis\results\summary_table.csv"
$output | Export-Csv -Path $outPath -NoTypeInformation -Encoding UTF8

Write-Output "Done. Rows processed: $($output.Count)"
$sigReversed = $output | Where-Object { $_.diff_type -eq 'reversed' -and $_.coarse_significant_p05 -eq 'yes' }
Write-Output "Reversed AND coarse-significant (real reversals): $($sigReversed.Count)"
$notSigReversed = $output | Where-Object { $_.diff_type -eq 'reversed' -and $_.coarse_significant_p05 -eq 'no' }
Write-Output "Reversed but coarse NOT significant (likely noise): $($notSigReversed.Count)"
