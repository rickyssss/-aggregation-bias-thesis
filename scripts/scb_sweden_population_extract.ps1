# Sweden SCB Statistikdatabasen population demographics: county (lan) vs
# municipality (kommun). Raw counts are converted to per-1000-population rates.

$ErrorActionPreference = "Stop"
$repo = "C:\Users\saika\-aggregation-bias-thesis"
$url = "https://api.scb.se/OV0104/v1/doris/en/ssd/START/BE/BE0101/BE0101A/BefolkningNy"

function Invoke-ScbCsv($query) {
    $body = @{
        query = $query
        response = @{ format = "CSV" }
    } | ConvertTo-Json -Depth 12
    $raw = Invoke-RestMethod -Uri $url -Method Post -ContentType "application/json; charset=utf-8" -Body $body
    return $raw | ConvertFrom-Csv
}

function Get-Measure($row) {
    $prop = $row.PSObject.Properties | Where-Object { $_.Name -match "2024$" } | Select-Object -First 1
    if ($null -eq $prop) { return [double]::NaN }
    $n = 0.0
    if ([double]::TryParse("$($prop.Value)", [ref]$n)) { return $n }
    return [double]::NaN
}

function Get-RegionParts($region) {
    if ("$region" -match "^([0-9]{2,4})\s+(.+)$") {
        return @{ code = $Matches[1]; name = $Matches[2] }
    }
    return $null
}

$regionAll = @{ code = "Region"; selection = @{ filter = "all"; values = @("*") } }
$year2024 = @{ code = "Tid"; selection = @{ filter = "item"; values = @("2024") } }
$popObs = @{ code = "ContentsCode"; selection = @{ filter = "item"; values = @("BE0101N1") } }
$growthObs = @{ code = "ContentsCode"; selection = @{ filter = "item"; values = @("BE0101N2") } }
$ageTotal = @{ code = "Alder"; selection = @{ filter = "item"; values = @("tot") } }
$widowedCode = ([char]0x00C4) + "NKL"

$ageValues = @()
for ($i = 0; $i -le 99; $i++) { $ageValues += "$i" }
$ageValues += "100+"

"Downloading SCB totals..."
$totalRows = Invoke-ScbCsv @($regionAll, $ageTotal, $popObs, $year2024)
"Downloading SCB age rows..."
$ageRows = Invoke-ScbCsv @(
    $regionAll,
    @{ code = "Alder"; selection = @{ filter = "item"; values = $ageValues } },
    $popObs,
    $year2024
)
"Downloading SCB sex rows..."
$sexRows = Invoke-ScbCsv @(
    $regionAll,
    $ageTotal,
    @{ code = "Kon"; selection = @{ filter = "item"; values = @("1","2") } },
    $popObs,
    $year2024
)
"Downloading SCB marital-status rows..."
$maritalRows = Invoke-ScbCsv @(
    $regionAll,
    @{ code = "Civilstand"; selection = @{ filter = "item"; values = @("OG","G",$widowedCode,"SK") } },
    $ageTotal,
    $popObs,
    $year2024
)
"Downloading SCB population-growth rows..."
$growthRows = Invoke-ScbCsv @($regionAll, $ageTotal, $growthObs, $year2024)

$regions = @{}
foreach ($r in $totalRows) {
    $parts = Get-RegionParts $r.region
    if ($null -eq $parts) { continue }
    $pop = Get-Measure $r
    if ([double]::IsNaN($pop) -or $pop -le 0) { continue }
    $regions[$parts.code] = [ordered]@{
        region_code = $parts.code
        region_name = $parts.name
        population = $pop
        age_0_17 = 0.0
        age_18_64 = 0.0
        age_65_plus = 0.0
        men = [double]::NaN
        women = [double]::NaN
        single = [double]::NaN
        married = [double]::NaN
        widowed = [double]::NaN
        divorced = [double]::NaN
        population_growth = [double]::NaN
    }
}

foreach ($r in $ageRows) {
    $parts = Get-RegionParts $r.region
    if ($null -eq $parts -or -not $regions.ContainsKey($parts.code)) { continue }
    if ("$($r.age)" -notmatch "^([0-9]+)") { continue }
    $age = [int]$Matches[1]
    $value = Get-Measure $r
    if ([double]::IsNaN($value)) { continue }
    if ($age -le 17) {
        $regions[$parts.code].age_0_17 += $value
    } elseif ($age -le 64) {
        $regions[$parts.code].age_18_64 += $value
    } else {
        $regions[$parts.code].age_65_plus += $value
    }
}

foreach ($r in $sexRows) {
    $parts = Get-RegionParts $r.region
    if ($null -eq $parts -or -not $regions.ContainsKey($parts.code)) { continue }
    $value = Get-Measure $r
    if ([double]::IsNaN($value)) { continue }
    switch ("$($r.sex)") {
        "men" { $regions[$parts.code].men = $value }
        "women" { $regions[$parts.code].women = $value }
    }
}

foreach ($r in $maritalRows) {
    $parts = Get-RegionParts $r.region
    if ($null -eq $parts -or -not $regions.ContainsKey($parts.code)) { continue }
    $value = Get-Measure $r
    if ([double]::IsNaN($value)) { continue }
    switch ("$($r.'marital status')") {
        "single" { $regions[$parts.code].single = $value }
        "married" { $regions[$parts.code].married = $value }
        "widowers/widows" { $regions[$parts.code].widowed = $value }
        "divorced" { $regions[$parts.code].divorced = $value }
    }
}

foreach ($r in $growthRows) {
    $parts = Get-RegionParts $r.region
    if ($null -eq $parts -or -not $regions.ContainsKey($parts.code)) { continue }
    $regions[$parts.code].population_growth = Get-Measure $r
}

function BuildRateTable($rows) {
    $out = New-Object System.Collections.Generic.List[object]
    foreach ($r in $rows) {
        $pop = [double]$r.population
        if ($pop -le 0) { continue }
        $o = [ordered]@{
            region_code = $r.region_code
            region_name = $r.region_name
            population = [int][Math]::Round($pop,0)
            young_0_17_rate = 1000.0 * [double]$r.age_0_17 / $pop
            working_18_64_rate = 1000.0 * [double]$r.age_18_64 / $pop
            elderly_65_plus_rate = 1000.0 * [double]$r.age_65_plus / $pop
            male_rate = 1000.0 * [double]$r.men / $pop
            female_rate = 1000.0 * [double]$r.women / $pop
            single_rate = 1000.0 * [double]$r.single / $pop
            married_rate = 1000.0 * [double]$r.married / $pop
            widowed_rate = 1000.0 * [double]$r.widowed / $pop
            divorced_rate = 1000.0 * [double]$r.divorced / $pop
            growth_per1000 = 1000.0 * [double]$r.population_growth / $pop
        }
        $out.Add([PSCustomObject]$o)
    }
    return $out
}

$allRegions = $regions.Values | ForEach-Object { [PSCustomObject]$_ }
$lan = $allRegions | Where-Object { $_.region_code.Length -eq 2 -and $_.region_code -ne "00" } | Sort-Object region_code
$kommun = $allRegions | Where-Object { $_.region_code.Length -eq 4 } | Sort-Object region_code

$coarseTable = BuildRateTable $lan
$fineTable = BuildRateTable $kommun
"Coarse (lan county) usable: $($coarseTable.Count), Fine (kommun municipality) usable: $($fineTable.Count)"

New-Item -ItemType Directory -Force -Path "$repo\data\Sweden" | Out-Null
$coarseTable | Export-Csv "$repo\data\Sweden\scb_population_demographics_coarse_lan.csv" -NoTypeInformation -Encoding UTF8
$fineTable | Export-Csv "$repo\data\Sweden\scb_population_demographics_fine_kommun.csv" -NoTypeInformation -Encoding UTF8

$vars = @(
    "young_0_17_rate","working_18_64_rate","elderly_65_plus_rate","male_rate","female_rate",
    "single_rate","married_rate","widowed_rate","divorced_rate","growth_per1000"
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
        $obj | Add-Member -MemberType NoteProperty -Name country -Value "Sweden"
        $obj | Add-Member -MemberType NoteProperty -Name variable -Value ($c1 + " vs " + $c2)
        $obj | Add-Member -MemberType NoteProperty -Name coarse_level -Value ("lan_county(n=" + $nCoarse + ")")
        $obj | Add-Member -MemberType NoteProperty -Name coarse_stat -Value ("corr=" + [Math]::Round($rCoarse,3))
        $obj | Add-Member -MemberType NoteProperty -Name fine_level -Value ("kommun_municipality(n=" + $nFine + ")")
        $obj | Add-Member -MemberType NoteProperty -Name fine_stat -Value ("corr=" + [Math]::Round($rFine,3))
        $obj | Add-Member -MemberType NoteProperty -Name diff_type -Value $diffType
        $obj | Add-Member -MemberType NoteProperty -Name notes -Value "Statistics Sweden SCB Statistikdatabasen PxWeb table BefolkningNy (Population by region, marital status, age and sex), 2024, no registration required. County(lan) and municipality(kommun) rows come from the same Region dimension. Raw demographic counts and population growth converted to per-1000-population rates."
        $obj | Add-Member -MemberType NoteProperty -Name coarse_significant_p05 -Value (Test-Sig $rCoarse $nCoarse)
        $obj | Add-Member -MemberType NoteProperty -Name fine_significant_p05 -Value (Test-Sig $rFine $nFine)
        $results.Add($obj)
    }
}
"Pairs: $($results.Count)"
$results | Export-Csv "$repo\results\scb_sweden_population_pairwise.csv" -NoTypeInformation -Encoding UTF8
"Saved."
