# Italy IstatData resident population by age: regione (coarse) vs comune (fine).
# Raw exact-age counts are converted to per-1000-population rates.

$ErrorActionPreference = "Stop"
$repo = "C:\Users\saika\-aggregation-bias-thesis"
$baseUrl = "https://esploradati.istat.it/SDMXWS/rest/data"
$year = "2025"
$coarseFlow = "22_289_DF_DCIS_POPRES1_2"
$fineFlow = "22_289_DF_DCIS_POPRES1_24"
$ageCodes = @("TOTAL","Y0","Y14","Y30","Y50","Y65","Y85","Y_GE100")
$coarseRegionCodes = @(
    "ITC1","ITC2","ITC3","ITC4","ITD1","ITD2","ITD3","ITD4","ITD5",
    "ITE1","ITE2","ITE3","ITE4","ITF1","ITF2","ITF3","ITF4","ITF5","ITF6","ITG1","ITG2"
)
$lastRequestAt = $null

function Invoke-IstatCsv($flow, $age, $refAreas) {
    if ($null -ne $script:lastRequestAt) {
        $elapsed = (Get-Date) - $script:lastRequestAt
        if ($elapsed.TotalSeconds -lt 15) {
            Start-Sleep -Seconds ([Math]::Ceiling(15 - $elapsed.TotalSeconds))
        }
    }
    $refKey = if ($null -eq $refAreas -or $refAreas.Count -eq 0) { "" } else { $refAreas -join "+" }
    $url = "$baseUrl/$flow/A.$refKey.JAN.9.$age.99?startPeriod=$year&endPeriod=$year"
    "GET $flow age=$age"
    $script:lastRequestAt = Get-Date
    try {
        $resp = Invoke-WebRequest -Uri $url -Headers @{ Accept = "text/csv" } -UseBasicParsing -TimeoutSec 180
        return @($resp.Content | ConvertFrom-Csv)
    } catch {
        Start-Sleep -Seconds 45
        $script:lastRequestAt = Get-Date
        $resp = Invoke-WebRequest -Uri $url -Headers @{ Accept = "text/csv" } -UseBasicParsing -TimeoutSec 180
        return @($resp.Content | ConvertFrom-Csv)
    }
}

function Load-AgeTable($flow, $level, $refAreas) {
    $areas = @{}
    foreach ($age in $ageCodes) {
        $rows = Invoke-IstatCsv $flow $age $refAreas
        $rows = @($rows | Where-Object { $_.TIME_PERIOD -eq $year })
        if ($rows.Count -eq 0) { throw "No $year rows returned for $flow age=$age" }
        foreach ($r in $rows) {
            $code = "$($r.REF_AREA)"
            if ($level -eq "region") {
                if ($code -notmatch '^IT[A-Z0-9]{2}$') { continue }
            } else {
                if ($code -notmatch '^[0-9]{6}$') { continue }
            }
            $value = 0.0
            if (-not [double]::TryParse("$($r.OBS_VALUE)", [ref]$value)) { continue }
            if (-not $areas.ContainsKey($code)) {
                $areas[$code] = [ordered]@{
                    geo = $code
                    population = [double]::NaN
                    age0 = [double]::NaN
                    age14 = [double]::NaN
                    age30 = [double]::NaN
                    age50 = [double]::NaN
                    age65 = [double]::NaN
                    age85 = [double]::NaN
                    age100_plus = [double]::NaN
                }
            }
            switch ($age) {
                "TOTAL" { $areas[$code].population = $value }
                "Y0" { $areas[$code].age0 = $value }
                "Y14" { $areas[$code].age14 = $value }
                "Y30" { $areas[$code].age30 = $value }
                "Y50" { $areas[$code].age50 = $value }
                "Y65" { $areas[$code].age65 = $value }
                "Y85" { $areas[$code].age85 = $value }
                "Y_GE100" { $areas[$code].age100_plus = $value }
            }
        }
    }
    return @($areas.Values | ForEach-Object { [PSCustomObject]$_ })
}

function SafeRatio($num, $den) {
    if ([double]::IsNaN($num) -or [double]::IsNaN($den) -or $den -le 0) { return [double]::NaN }
    return 1000.0 * $num / $den
}

function BuildRateTable($rows) {
    $out = New-Object System.Collections.Generic.List[object]
    foreach ($r in $rows) {
        $pop = [double]$r.population
        if ([double]::IsNaN($pop) -or $pop -le 0) { continue }
        $o = [ordered]@{
            geo = $r.geo
            population = [int][Math]::Round($pop,0)
            age0_rate = SafeRatio ([double]$r.age0) $pop
            age14_rate = SafeRatio ([double]$r.age14) $pop
            age30_rate = SafeRatio ([double]$r.age30) $pop
            age50_rate = SafeRatio ([double]$r.age50) $pop
            age65_rate = SafeRatio ([double]$r.age65) $pop
            age85_rate = SafeRatio ([double]$r.age85) $pop
            age100_plus_rate = SafeRatio ([double]$r.age100_plus) $pop
        }
        $out.Add([PSCustomObject]$o)
    }
    return $out
}

"Downloading Italy region age table..."
$coarseRaw = Load-AgeTable $coarseFlow "region" $coarseRegionCodes
"Downloading Italy municipality age table..."
$fineRaw = Load-AgeTable $fineFlow "municipality" @()

$coarseTable = BuildRateTable $coarseRaw
$fineTable = BuildRateTable $fineRaw
"Coarse (region) usable: $($coarseTable.Count), Fine (comune) usable: $($fineTable.Count)"

New-Item -ItemType Directory -Force -Path "$repo\data\Italy" | Out-Null
$coarseTable | Sort-Object geo | Export-Csv "$repo\data\Italy\istat_population_age_coarse_region.csv" -NoTypeInformation -Encoding UTF8
$fineTable | Sort-Object geo | Export-Csv "$repo\data\Italy\istat_population_age_fine_comune.csv" -NoTypeInformation -Encoding UTF8

$vars = @(
    "age0_rate","age14_rate","age30_rate","age50_rate","age65_rate","age85_rate","age100_plus_rate"
)

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
foreach ($v in $vars) { $coarseVals[$v] = $coarseTable | ForEach-Object { $n=0.0; if([double]::TryParse("$($_.$v)",[ref]$n)){$n}else{[double]::NaN} } }
$fineVals = @{}
foreach ($v in $vars) { $fineVals[$v] = $fineTable | ForEach-Object { $n=0.0; if([double]::TryParse("$($_.$v)",[ref]$n)){$n}else{[double]::NaN} } }

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
        $obj | Add-Member -MemberType NoteProperty -Name country -Value "Italy"
        $obj | Add-Member -MemberType NoteProperty -Name variable -Value ($c1 + " vs " + $c2)
        $obj | Add-Member -MemberType NoteProperty -Name coarse_level -Value ("regione(n=" + $nCoarse + ")")
        $obj | Add-Member -MemberType NoteProperty -Name coarse_stat -Value ("corr=" + [Math]::Round($rCoarse,3))
        $obj | Add-Member -MemberType NoteProperty -Name fine_level -Value ("comune(n=" + $nFine + ")")
        $obj | Add-Member -MemberType NoteProperty -Name fine_stat -Value ("corr=" + [Math]::Round($rFine,3))
        $obj | Add-Member -MemberType NoteProperty -Name diff_type -Value $diffType
        $obj | Add-Member -MemberType NoteProperty -Name notes -Value "IstatData SDMX API resident population on 1 January, 2025. Coarse flow 22_289_DF_DCIS_POPRES1_2 = 21 NUTS2 region-level units (Bolzano/Trento as autonomous province region-level units; duplicate ITDA and ITZZ excluded). Fine flow 22_289_DF_DCIS_POPRES1_24 = all municipality(comune) rows. Raw exact-age counts converted to per-1000-population rates; 2026 estimated rows returned by API are ignored."
        $obj | Add-Member -MemberType NoteProperty -Name coarse_significant_p05 -Value (Test-Sig $rCoarse $nCoarse)
        $obj | Add-Member -MemberType NoteProperty -Name fine_significant_p05 -Value (Test-Sig $rFine $nFine)
        $results.Add($obj)
    }
}
"Pairs: $($results.Count)"
$results | Export-Csv "$repo\results\istat_italy_population_age_pairwise.csv" -NoTypeInformation -Encoding UTF8
"Saved."
