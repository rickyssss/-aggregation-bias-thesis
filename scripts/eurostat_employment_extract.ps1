# Add employment rate (per 1000 population) to the EU dataset, correlate against
# the existing GDP/population/demographic-rate variables.

$ErrorActionPreference = "Stop"
$repo = "C:\Users\saika\-aggregation-bias-thesis"

function LoadMap($path, $keyCol) {
    $rows = Import-Csv $path
    $map = @{}
    foreach ($r in $rows) { $map[$r.$keyCol] = $r }
    return $map
}

$gdpCoarse = LoadMap "$repo\data\EU\gdp_coarse.csv" "nuts2_code"
$gdpFine = LoadMap "$repo\data\EU\gdp_fine.csv" "nuts3_code"
$demoCoarse = LoadMap "$repo\data\EU\demo_coarse.csv" "geo"
$demoFine = LoadMap "$repo\data\EU\demo_fine.csv" "geo"

$empRaw = Import-Csv "$repo\scratch\eurostat_employ.csv" | Where-Object { $_.nace_r2 -eq 'TOTAL' -and $_.OBS_VALUE -ne '' }
$empCoarse = @{}; $empFine = @{}
foreach ($r in $empRaw) {
    if ($r.geo.Length -eq 4) { $empCoarse[$r.geo] = $r.OBS_VALUE }
    elseif ($r.geo.Length -eq 5) { $empFine[$r.geo] = $r.OBS_VALUE }
}

function BuildTable($gdpMap, $demoMap, $empMap) {
    $out = @()
    foreach ($geo in $gdpMap.Keys) {
        if (-not $demoMap.ContainsKey($geo)) { continue }
        if (-not $empMap.ContainsKey($geo)) { continue }
        $pop = 0.0; $gdp = 0.0; $emp = 0.0
        [double]::TryParse($gdpMap[$geo].population_2022, [ref]$pop) | Out-Null
        [double]::TryParse($gdpMap[$geo].gdp_mio_eur_2022, [ref]$gdp) | Out-Null
        [double]::TryParse($empMap[$geo], [ref]$emp) | Out-Null
        if ($pop -le 0) { continue }
        $row = [ordered]@{
            geo = $geo
            gdp_per_capita_eur = ($gdp * 1000000.0) / $pop
            employment_rate_per1000 = ($emp * 1000.0 * 1000.0) / $pop
            CNMIGRATRT = $demoMap[$geo].CNMIGRATRT
            GBIRTHRT = $demoMap[$geo].GBIRTHRT
            GDEATHRT = $demoMap[$geo].GDEATHRT
            GROWRT = $demoMap[$geo].GROWRT
            NATGROWRT = $demoMap[$geo].NATGROWRT
        }
        $out += [PSCustomObject]$row
    }
    return $out
}

$coarseTable = BuildTable $gdpCoarse $demoCoarse $empCoarse
$fineTable = BuildTable $gdpFine $demoFine $empFine
"Coarse merged rows: $($coarseTable.Count)"
"Fine merged rows: $($fineTable.Count)"

$vars = @("gdp_per_capita_eur","employment_rate_per1000","CNMIGRATRT","GBIRTHRT","GDEATHRT","GROWRT","NATGROWRT")

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
foreach ($v in $vars) { $coarseVals[$v] = $coarseTable | ForEach-Object { $n=0.0; if([double]::TryParse($_.$v,[ref]$n)){$n}else{[double]::NaN} } }
$fineVals = @{}
foreach ($v in $vars) { $fineVals[$v] = $fineTable | ForEach-Object { $n=0.0; if([double]::TryParse($_.$v,[ref]$n)){$n}else{[double]::NaN} } }

$results = @()
for ($i = 0; $i -lt $vars.Count; $i++) {
    for ($j = $i + 1; $j -lt $vars.Count; $j++) {
        $c1 = $vars[$i]; $c2 = $vars[$j]
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

        $obj = New-Object PSObject
        $obj | Add-Member -MemberType NoteProperty -Name id -Value ""
        $obj | Add-Member -MemberType NoteProperty -Name country -Value "EU"
        $obj | Add-Member -MemberType NoteProperty -Name variable -Value ($c1 + " vs " + $c2)
        $obj | Add-Member -MemberType NoteProperty -Name coarse_level -Value ("NUTS2(n=" + $nCoarse + ")")
        $obj | Add-Member -MemberType NoteProperty -Name coarse_stat -Value ("corr=" + [Math]::Round($rCoarse,3))
        $obj | Add-Member -MemberType NoteProperty -Name fine_level -Value ("NUTS3(n=" + $nFine + ")")
        $obj | Add-Member -MemberType NoteProperty -Name fine_stat -Value ("corr=" + [Math]::Round($rFine,3))
        $obj | Add-Member -MemberType NoteProperty -Name diff_type -Value $diffType
        $obj | Add-Member -MemberType NoteProperty -Name notes -Value "Eurostat: employment(nama_10r_3empers)/GDP/population(nama_10r_3gdp)/demo(demo_r_gind3) merged, 2022, NUTS2 vs NUTS3"
        $obj | Add-Member -MemberType NoteProperty -Name coarse_significant_p05 -Value (Test-Sig $rCoarse $nCoarse)
        $obj | Add-Member -MemberType NoteProperty -Name fine_significant_p05 -Value (Test-Sig $rFine $nFine)
        $results += $obj
    }
}
"New pairs: $($results.Count)"
$results | Export-Csv "$repo\results\eurostat_employment_pairwise.csv" -NoTypeInformation -Encoding UTF8
$coarseTable | Export-Csv "$repo\data\EU\merged_coarse.csv" -NoTypeInformation -Encoding UTF8
$fineTable | Export-Csv "$repo\data\EU\merged_fine.csv" -NoTypeInformation -Encoding UTF8
"Done."
