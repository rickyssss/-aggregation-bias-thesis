# Parse Census ACS 5-year (2022) state vs county JSON, convert counts to per-1000-population
# rates (medians/per-capita figures kept as-is), compute exhaustive pairwise correlations.

$ErrorActionPreference = "Stop"
$repo = "C:\Users\saika\-aggregation-bias-thesis"

function LoadAcs($path) {
    $raw = Get-Content $path -Raw | ConvertFrom-Json
    $header = $raw[0]
    $rows = @()
    for ($i = 1; $i -lt $raw.Count; $i++) {
        $obj = [ordered]@{}
        for ($j = 0; $j -lt $header.Count; $j++) { $obj[$header[$j]] = $raw[$i][$j] }
        $rows += [PSCustomObject]$obj
    }
    return $rows
}

$stateRows = LoadAcs "$repo\scratch\acs_state.json"
$countyRows = LoadAcs "$repo\scratch\acs_county.json"
"State rows: $($stateRows.Count), County rows: $($countyRows.Count)"

# variables kept as raw medians/per-capita (no rate conversion)
$rawVars = @("B01002_001E","B19013_001E","B19301_001E","B25064_001E","B25077_001E")
# variables converted to per-1000-population rate using B01003_001E as denominator
$countVars = @(
    "B01001_002E","B01001_026E","B17001_002E","B15003_017E","B15003_022E","B15003_002E",
    "B23025_002E","B23025_005E","B23025_004E","B25002_002E","B25002_003E","B25003_002E","B25003_003E",
    "B08301_010E","B08301_021E","B11003_010E","B18101_004E","B27010_017E","B16001_002E",
    "B02001_002E","B02001_003E","B02001_005E","B25024_002E","B25024_010E"
)

function BuildRateTable($rows) {
    $out = New-Object System.Collections.Generic.List[object]
    foreach ($r in $rows) {
        $pop = 0.0
        if (-not [double]::TryParse($r.B01003_001E, [ref]$pop) -or $pop -le 0) { continue }
        $o = [ordered]@{ name = $r.NAME }
        foreach ($v in $rawVars) {
            $n = 0.0
            $o[$v] = if ([double]::TryParse($r.$v, [ref]$n)) { $n } else { [double]::NaN }
        }
        foreach ($v in $countVars) {
            $n = 0.0
            $o[$v] = if ([double]::TryParse($r.$v, [ref]$n)) { 1000.0 * $n / $pop } else { [double]::NaN }
        }
        $out.Add([PSCustomObject]$o)
    }
    return $out
}

$coarseTable = BuildRateTable $stateRows
$fineTable = BuildRateTable $countyRows
"Coarse (state) usable rows: $($coarseTable.Count)"
"Fine (county) usable rows: $($fineTable.Count)"

New-Item -ItemType Directory -Force -Path "$repo\data\US" | Out-Null
$coarseTable | Export-Csv "$repo\data\US\acs_coarse_state.csv" -NoTypeInformation -Encoding UTF8
$fineTable | Export-Csv "$repo\data\US\acs_fine_county.csv" -NoTypeInformation -Encoding UTF8

$vars = $rawVars + $countVars

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
foreach ($v in $vars) { $coarseVals[$v] = $coarseTable | ForEach-Object { $_.$v } }
$fineVals = @{}
foreach ($v in $vars) { $fineVals[$v] = $fineTable | ForEach-Object { $_.$v } }

$results = New-Object System.Collections.Generic.List[object]
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
        $obj | Add-Member -MemberType NoteProperty -Name country -Value "US"
        $obj | Add-Member -MemberType NoteProperty -Name variable -Value ($c1 + " vs " + $c2)
        $obj | Add-Member -MemberType NoteProperty -Name coarse_level -Value ("state(n=" + $nCoarse + ")")
        $obj | Add-Member -MemberType NoteProperty -Name coarse_stat -Value ("corr=" + [Math]::Round($rCoarse,3))
        $obj | Add-Member -MemberType NoteProperty -Name fine_level -Value ("county(n=" + $nFine + ")")
        $obj | Add-Member -MemberType NoteProperty -Name fine_stat -Value ("corr=" + [Math]::Round($rFine,3))
        $obj | Add-Member -MemberType NoteProperty -Name diff_type -Value $diffType
        $obj | Add-Member -MemberType NoteProperty -Name notes -Value "US Census ACS 5-year 2022 (B-series). Most variables converted to per-1000-population rate using B01003_001E as denominator (approximate universe, not narrow subgroup universe); median/per-capita variables (B01002/B19013/B19301/B25064/B25077) kept as published. Exhaustive pairwise scan across 36 variables -- multiple-testing caution applies, same as SSDSE full scan."
        $obj | Add-Member -MemberType NoteProperty -Name coarse_significant_p05 -Value (Test-Sig $rCoarse $nCoarse)
        $obj | Add-Member -MemberType NoteProperty -Name fine_significant_p05 -Value (Test-Sig $rFine $nFine)
        $results.Add($obj)
    }
}
"Pairs: $($results.Count)"
$results | Export-Csv "$repo\results\acs_pairwise.csv" -NoTypeInformation -Encoding UTF8
"Saved."
