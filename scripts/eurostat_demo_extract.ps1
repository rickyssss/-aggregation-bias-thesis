# Process the Eurostat demo_r_gind3 SDMX-CSV export into coarse (NUTS2) / fine (NUTS3) tables
# and compute exhaustive pairwise correlations.

$ErrorActionPreference = "Stop"
$repo = "C:\Users\saika\-aggregation-bias-thesis"
$csv = Import-Csv "$repo\scratch\eurostat_demo.csv"

"Total raw rows: $($csv.Count)"

# NUTS2 = 4 chars (e.g. AL01), NUTS3 = 5 chars (e.g. AL011). Country-level (2 char) and NUTS1 (3 char) excluded.
$nuts2Rows = $csv | Where-Object { $_.geo.Length -eq 4 -and $_.OBS_VALUE -ne "" }
$nuts3Rows = $csv | Where-Object { $_.geo.Length -eq 5 -and $_.OBS_VALUE -ne "" }
"NUTS2 rows: $($nuts2Rows.Count), NUTS3 rows: $($nuts3Rows.Count)"

$indicators = $csv.indic_de | Sort-Object -Unique
"Indicators: $($indicators -join ', ')"

function Pivot($rows, $indicators) {
    $byGeo = @{}
    foreach ($r in $rows) {
        if (-not $byGeo.ContainsKey($r.geo)) { $byGeo[$r.geo] = @{} }
        $byGeo[$r.geo][$r.indic_de] = $r.OBS_VALUE
    }
    $result = @()
    foreach ($geo in $byGeo.Keys) {
        $obj = [ordered]@{ geo = $geo }
        foreach ($ind in $indicators) { $obj[$ind] = $byGeo[$geo][$ind] }
        $result += [PSCustomObject]$obj
    }
    return $result
}

$coarseTable = Pivot $nuts2Rows $indicators
$fineTable = Pivot $nuts3Rows $indicators
"Coarse pivoted: $($coarseTable.Count) geos, Fine pivoted: $($fineTable.Count) geos"

New-Item -ItemType Directory -Force -Path "$repo\data\EU" | Out-Null
$coarseTable | Export-Csv "$repo\data\EU\demo_coarse.csv" -NoTypeInformation -Encoding UTF8
$fineTable | Export-Csv "$repo\data\EU\demo_fine.csv" -NoTypeInformation -Encoding UTF8

# --- Correlation + significance (reuse same math as add_significance.ps1) ---
function Get-Correlation($xs, $ys) {
    $n = $xs.Count
    if ($n -lt 4) { return $null }
    $mx = ($xs | Measure-Object -Average).Average
    $my = ($ys | Measure-Object -Average).Average
    $sumXY = 0.0; $sumX2 = 0.0; $sumY2 = 0.0
    for ($i = 0; $i -lt $n; $i++) {
        $dx = $xs[$i] - $mx; $dy = $ys[$i] - $my
        $sumXY += $dx * $dy; $sumX2 += $dx * $dx; $sumY2 += $dy * $dy
    }
    if ($sumX2 -eq 0 -or $sumY2 -eq 0) { return $null }
    return $sumXY / [Math]::Sqrt($sumX2 * $sumY2)
}
$tTable = @{1=12.706;2=4.303;3=3.182;4=2.776;5=2.571;6=2.447;7=2.365;8=2.306;9=2.262;10=2.228;11=2.201;12=2.179;13=2.160;14=2.145;15=2.131;16=2.120;17=2.110;18=2.101;19=2.093;20=2.086;21=2.080;22=2.074;23=2.069;24=2.064;25=2.060;26=2.056;27=2.052;28=2.048;29=2.045;30=2.042}
function Get-CriticalT($df) { if ($df -le 30) { return $tTable[$df] }; return 1.96 + (2.042-1.96)*[Math]::Max(0,(30.0/$df)) }
function Test-Sig($r,$n) { if ($null -eq $r -or $n -lt 4) { return "n/a" }; $df=$n-2; $absR=[Math]::Abs($r); if ($absR -ge 0.999999) {return "yes"}; $t=$absR*[Math]::Sqrt($df/(1-$absR*$absR)); if ($t -ge (Get-CriticalT $df)) {return "yes"} else {return "no"} }

$coarseVals = @{}
foreach ($ind in $indicators) {
    $coarseVals[$ind] = @()
    foreach ($r in $coarseTable) {
        $v = $r.$ind; $num = $null
        if ([double]::TryParse($v, [ref]$num)) { $coarseVals[$ind] += $num } else { $coarseVals[$ind] += [double]::NaN }
    }
}
$fineVals = @{}
foreach ($ind in $indicators) {
    $fineVals[$ind] = @()
    foreach ($r in $fineTable) {
        $v = $r.$ind; $num = $null
        if ([double]::TryParse($v, [ref]$num)) { $fineVals[$ind] += $num } else { $fineVals[$ind] += [double]::NaN }
    }
}

$results = @()
for ($i = 0; $i -lt $indicators.Count; $i++) {
    for ($j = $i + 1; $j -lt $indicators.Count; $j++) {
        $c1 = $indicators[$i]; $c2 = $indicators[$j]
        $cx = $coarseVals[$c1]; $cy = $coarseVals[$c2]
        $validC = 0..($cx.Count-1) | Where-Object { -not [double]::IsNaN($cx[$_]) -and -not [double]::IsNaN($cy[$_]) }
        $cxV = $validC | ForEach-Object { $cx[$_] }; $cyV = $validC | ForEach-Object { $cy[$_] }
        $rCoarse = Get-Correlation $cxV $cyV
        $nCoarse = $validC.Count

        $fx = $fineVals[$c1]; $fy = $fineVals[$c2]
        $validF = 0..($fx.Count-1) | Where-Object { -not [double]::IsNaN($fx[$_]) -and -not [double]::IsNaN($fy[$_]) }
        $fxV = $validF | ForEach-Object { $fx[$_] }; $fyV = $validF | ForEach-Object { $fy[$_] }
        $rFine = Get-Correlation $fxV $fyV
        $nFine = $validF.Count

        if ($null -eq $rCoarse -or $null -eq $rFine) { continue }

        $diffType = "similar"
        if ([Math]::Sign($rCoarse) -ne [Math]::Sign($rFine) -and [Math]::Abs($rCoarse) -gt 0.05 -and [Math]::Abs($rFine) -gt 0.05) {
            $diffType = "reversed"
        } elseif ([Math]::Abs($rCoarse) -gt 0.001) {
            $relChange = [Math]::Abs([Math]::Abs($rCoarse) - [Math]::Abs($rFine)) / [Math]::Abs($rCoarse)
            if ($relChange -gt 0.3) { $diffType = "magnitude_change" }
        }

        $sigC = Test-Sig $rCoarse $nCoarse
        $sigF = Test-Sig $rFine $nFine

        $obj = New-Object PSObject
        $obj | Add-Member -MemberType NoteProperty -Name id -Value ""
        $obj | Add-Member -MemberType NoteProperty -Name country -Value "EU"
        $obj | Add-Member -MemberType NoteProperty -Name variable -Value ($c1 + " vs " + $c2)
        $obj | Add-Member -MemberType NoteProperty -Name coarse_level -Value ("NUTS2(n=" + $nCoarse + ")")
        $obj | Add-Member -MemberType NoteProperty -Name coarse_stat -Value ("corr=" + [Math]::Round($rCoarse,3))
        $obj | Add-Member -MemberType NoteProperty -Name fine_level -Value ("NUTS3(n=" + $nFine + ")")
        $obj | Add-Member -MemberType NoteProperty -Name fine_stat -Value ("corr=" + [Math]::Round($rFine,3))
        $obj | Add-Member -MemberType NoteProperty -Name diff_type -Value $diffType
        $obj | Add-Member -MemberType NoteProperty -Name notes -Value "Eurostat demo_r_gind3 (population change, births, deaths, migration rates), 2022, NUTS2 vs NUTS3"
        $obj | Add-Member -MemberType NoteProperty -Name coarse_significant_p05 -Value $sigC
        $obj | Add-Member -MemberType NoteProperty -Name fine_significant_p05 -Value $sigF
        $results += $obj
    }
}
"Total pairs: $($results.Count)"
$results | Export-Csv "$repo\results\eurostat_demo_pairwise.csv" -NoTypeInformation -Encoding UTF8
"Saved."
