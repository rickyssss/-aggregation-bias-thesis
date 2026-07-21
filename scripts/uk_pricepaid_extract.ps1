# UK HM Land Registry Price Paid Data 2024: district (fine) vs county (coarse).
# No header row in source file. Fields are quoted; split on the quote+comma+quote pattern.

$ErrorActionPreference = "Stop"
$repo = "C:\Users\saika\-aggregation-bias-thesis"
$srcFile = "$repo\scratch\ukpp\pp2024.csv"

# column indices (0-based) per standard PPD schema:
# 0 id, 1 price, 2 date, 3 postcode, 4 property_type, 5 old_new, 6 duration,
# 7 paon, 8 saon, 9 street, 10 locality, 11 town_city, 12 district, 13 county, 14 ppd_cat, 15 record_status

function ParseLine($line) {
    $trimmed = $line.Substring(1, $line.Length - 2)
    return $trimmed -split '","'
}

$districtData = @{}
$countyData = @{}

function GetBucket($table, $key) {
    if (-not $table.ContainsKey($key)) {
        $table[$key] = @{
            price = New-Object System.Collections.Generic.List[double]
            detached = 0; semi = 0; terraced = 0; flat = 0; other = 0
            newbuild = 0; total = 0
        }
    }
    return $table[$key]
}

$reader = New-Object System.IO.StreamReader($srcFile)
$lineCount = 0
while (-not $reader.EndOfStream) {
    $line = $reader.ReadLine()
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    $f = ParseLine $line
    if ($f.Count -lt 16) { continue }
    $lineCount++

    $price = 0.0
    if (-not [double]::TryParse($f[1], [ref]$price) -or $price -le 0) { continue }

    $propType = $f[4]
    $oldNew = $f[5]
    $district = $f[12]
    $county = $f[13]

    foreach ($bucket in @((GetBucket $districtData $district), (GetBucket $countyData $county))) {
        $bucket.price.Add($price)
        $bucket.total++
        if ($oldNew -eq "Y") { $bucket.newbuild++ }
        switch ($propType) {
            "D" { $bucket.detached++ }
            "S" { $bucket.semi++ }
            "T" { $bucket.terraced++ }
            "F" { $bucket.flat++ }
            default { $bucket.other++ }
        }
    }
}
$reader.Close()
"Lines read: $lineCount, districts: $($districtData.Count), counties: $($countyData.Count)"

function Get-Median($list) {
    if ($list.Count -eq 0) { return [double]::NaN }
    $sorted = $list | Sort-Object
    $n = $sorted.Count
    if ($n % 2 -eq 1) { return $sorted[[int](($n-1)/2)] }
    return ($sorted[$n/2 - 1] + $sorted[$n/2]) / 2.0
}

function BuildTable($table, [int]$minN) {
    $out = New-Object System.Collections.Generic.List[object]
    foreach ($key in $table.Keys) {
        $b = $table[$key]
        if ($b.total -lt $minN) { continue }
        $out.Add([PSCustomObject]@{
            geo = $key
            n_transactions = $b.total
            median_price = Get-Median $b.price
            detached_share_pct = 100.0 * $b.detached / $b.total
            semi_share_pct = 100.0 * $b.semi / $b.total
            terraced_share_pct = 100.0 * $b.terraced / $b.total
            flat_share_pct = 100.0 * $b.flat / $b.total
            newbuild_share_pct = 100.0 * $b.newbuild / $b.total
        })
    }
    return $out
}

$fineTable = BuildTable $districtData 3
$coarseTable = BuildTable $countyData 3
"Fine (district) usable rows: $($fineTable.Count), Coarse (county) usable rows: $($coarseTable.Count)"

New-Item -ItemType Directory -Force -Path "$repo\data\UK" | Out-Null
$fineTable | Export-Csv "$repo\data\UK\pricepaid_fine_district.csv" -NoTypeInformation -Encoding UTF8
$coarseTable | Export-Csv "$repo\data\UK\pricepaid_coarse_county.csv" -NoTypeInformation -Encoding UTF8

$vars = @("median_price","detached_share_pct","semi_share_pct","terraced_share_pct","flat_share_pct","newbuild_share_pct")

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
        $obj | Add-Member -MemberType NoteProperty -Name country -Value "UK"
        $obj | Add-Member -MemberType NoteProperty -Name variable -Value ($c1 + " vs " + $c2)
        $obj | Add-Member -MemberType NoteProperty -Name coarse_level -Value ("county(n=" + $nCoarse + ")")
        $obj | Add-Member -MemberType NoteProperty -Name coarse_stat -Value ("corr=" + [Math]::Round($rCoarse,3))
        $obj | Add-Member -MemberType NoteProperty -Name fine_level -Value ("district(n=" + $nFine + ")")
        $obj | Add-Member -MemberType NoteProperty -Name fine_stat -Value ("corr=" + [Math]::Round($rFine,3))
        $obj | Add-Member -MemberType NoteProperty -Name diff_type -Value $diffType
        $obj | Add-Member -MemberType NoteProperty -Name notes -Value "UK HM Land Registry Price Paid Data 2024(England and Wales). Median price and property-type shares per area(min 3 transactions). No registration required. Direct county-level aggregation of raw transactions."
        $obj | Add-Member -MemberType NoteProperty -Name coarse_significant_p05 -Value (Test-Sig $rCoarse $nCoarse)
        $obj | Add-Member -MemberType NoteProperty -Name fine_significant_p05 -Value (Test-Sig $rFine $nFine)
        $results.Add($obj)
    }
}
"Pairs: $($results.Count)"
$results | Export-Csv "$repo\results\uk_pricepaid_pairwise.csv" -NoTypeInformation -Encoding UTF8
"Saved."
