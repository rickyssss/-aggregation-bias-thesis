# Extract common variables from SSDSE-B (prefecture) and SSDSE-A (municipality),
# compute all pairwise correlations at both levels, and append to results/summary_table.csv

$ErrorActionPreference = "Stop"
$sjis = [System.Text.Encoding]::GetEncoding(932)
$repo = "C:\Users\saika\-aggregation-bias-thesis"

# --- Labels for the 34 common codes (from SSDSE-B label row, Shift-JIS decoded) ---
$linesB = [System.IO.File]::ReadAllLines("$repo\scratch\SSDSE-B-2026.csv", $sjis)
$codesB = $linesB[0] -split ","
$labelsB = $linesB[1] -split ","
$labelMap = @{}
for ($i = 0; $i -lt $codesB.Count; $i++) { $labelMap[$codesB[$i]] = $labelsB[$i] }

$commonCodes = @("A1101","A110101","A110102","A1102","A110201","A110202","A1301","A130101","A130102",
    "A1302","A130201","A130202","A1303","A130301","A130302","A4101","A4200","A5101","A5102","A9101","A9201",
    "E1101","E1501","E2101","E2401","E2501","E3101","E3401","E3501","E4101","E4501","I510120","I5102","I5103")

# --- Parse SSDSE-B: keep only most recent year (2023) row per prefecture ---
$idxCode = [array]::IndexOf($codesB, "Code")
$idxYear = 0  # first column is year
$colIdx = @{}
foreach ($c in $commonCodes) { $colIdx[$c] = [array]::IndexOf($codesB, $c) }

$coarseRows = @{}
for ($i = 2; $i -lt $linesB.Count; $i++) {
    if ([string]::IsNullOrWhiteSpace($linesB[$i])) { continue }
    $f = $linesB[$i] -split ","
    if ($f[$idxYear] -ne "2023") { continue }
    $code = $f[$idxCode]
    $row = [ordered]@{ area_code = $code }
    foreach ($c in $commonCodes) { $row[$c] = $f[$colIdx[$c]] }
    $coarseRows[$code] = $row
}
"Coarse (prefecture, 2023) rows: $($coarseRows.Count)"

# --- Parse SSDSE-A: one row per municipality ---
$linesA = [System.IO.File]::ReadAllLines("$repo\scratch\SSDSE-A-2026.csv", $sjis)
$codesA = $linesA[0] -split ","
$idxCodeA = [array]::IndexOf($codesA, "Code")
if ($idxCodeA -lt 0) { $idxCodeA = 0 }
$colIdxA = @{}
foreach ($c in $commonCodes) { $colIdxA[$c] = [array]::IndexOf($codesA, $c) }

$fineRows = @()
for ($i = 3; $i -lt $linesA.Count; $i++) {
    if ([string]::IsNullOrWhiteSpace($linesA[$i])) { continue }
    $f = $linesA[$i] -split ","
    $row = [ordered]@{ area_code = $f[0]; area_name = $f[2] }
    foreach ($c in $commonCodes) { $row[$c] = $f[$colIdxA[$c]] }
    $fineRows += [PSCustomObject]$row
}
"Fine (municipality) rows: $($fineRows.Count)"

# --- Save extracted data ---
New-Item -ItemType Directory -Force -Path "$repo\data\日本" | Out-Null
$coarseRows.Values | ForEach-Object { [PSCustomObject]$_ } | Export-Csv "$repo\data\日本\ssdse_coarse.csv" -NoTypeInformation -Encoding UTF8
$fineRows | Export-Csv "$repo\data\日本\ssdse_fine.csv" -NoTypeInformation -Encoding UTF8

# --- Correlation helper ---
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

# --- Build numeric arrays per variable at each level (raw counts) ---
$rawCoarse = @{}
$coarseList = $coarseRows.Values | ForEach-Object { [PSCustomObject]$_ }
foreach ($c in $commonCodes) {
    $rawCoarse[$c] = @()
    foreach ($r in $coarseList) {
        $v = $r.$c
        $num = $null
        if ([double]::TryParse($v, [ref]$num)) { $rawCoarse[$c] += $num } else { $rawCoarse[$c] += [double]::NaN }
    }
}
$rawFine = @{}
foreach ($c in $commonCodes) {
    $rawFine[$c] = @()
    foreach ($r in $fineRows) {
        $v = $r.$c
        $num = $null
        if ([double]::TryParse($v, [ref]$num)) { $rawFine[$c] += $num } else { $rawFine[$c] += [double]::NaN }
    }
}

# --- Convert raw counts into rates (per total population A1101) to avoid trivial
#     "everything correlates with population size" artifacts. Population breakdown
#     codes become ratios (share of total pop); flow counts become per-1000 rates.
$popCoarse = $rawCoarse["A1101"]
$popFine = $rawFine["A1101"]

$rateCodes = @()
$coarseVals = @{}
$fineVals = @{}
foreach ($c in $commonCodes) {
    if ($c -eq "A1101") { continue }  # skip total population itself as a variable (it's the denominator)
    $rateCode = $c + "_rate"
    $rateCodes += $rateCode
    $coarseVals[$rateCode] = for ($i=0; $i -lt $rawCoarse[$c].Count; $i++) {
        if ($popCoarse[$i] -gt 0) { 1000.0 * $rawCoarse[$c][$i] / $popCoarse[$i] } else { [double]::NaN }
    }
    $fineVals[$rateCode] = for ($i=0; $i -lt $rawFine[$c].Count; $i++) {
        if ($popFine[$i] -gt 0) { 1000.0 * $rawFine[$c][$i] / $popFine[$i] } else { [double]::NaN }
    }
    $labelMap[$rateCode] = $labelMap[$c] + " per1000pop"
}
$commonCodes = $rateCodes

# --- All pairwise combinations ---
$results = @()
for ($i = 0; $i -lt $commonCodes.Count; $i++) {
    for ($j = $i + 1; $j -lt $commonCodes.Count; $j++) {
        $c1 = $commonCodes[$i]; $c2 = $commonCodes[$j]

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

        $label1 = $labelMap[$c1]
        $label2 = $labelMap[$c2]
        $varText = $label1 + "(" + $c1 + ") vs " + $label2 + "(" + $c2 + ")"
        $coarseLevelText = "todofuken(n=" + $nCoarse + ")"
        $coarseStatText = "corr=" + [Math]::Round($rCoarse,3)
        $fineLevelText = "shikuchoson(n=" + $nFine + ")"
        $fineStatText = "corr=" + [Math]::Round($rFine,3)
        $notesText = "SSDSE-B(2023)/SSDSE-A extraction, part of exhaustive pairwise scan"
        $sigC = Test-Sig $rCoarse $nCoarse
        $sigF = Test-Sig $rFine $nFine

        $obj = New-Object PSObject
        $obj | Add-Member -MemberType NoteProperty -Name id -Value ""
        $obj | Add-Member -MemberType NoteProperty -Name country -Value "Japan"
        $obj | Add-Member -MemberType NoteProperty -Name variable -Value $varText
        $obj | Add-Member -MemberType NoteProperty -Name coarse_level -Value $coarseLevelText
        $obj | Add-Member -MemberType NoteProperty -Name coarse_stat -Value $coarseStatText
        $obj | Add-Member -MemberType NoteProperty -Name fine_level -Value $fineLevelText
        $obj | Add-Member -MemberType NoteProperty -Name fine_stat -Value $fineStatText
        $obj | Add-Member -MemberType NoteProperty -Name diff_type -Value $diffType
        $obj | Add-Member -MemberType NoteProperty -Name notes -Value $notesText
        $obj | Add-Member -MemberType NoteProperty -Name coarse_significant_p05 -Value $sigC
        $obj | Add-Member -MemberType NoteProperty -Name fine_significant_p05 -Value $sigF
        $results += $obj
    }
}

"Total pairs computed: $($results.Count)"
$reversedSig = ($results | Where-Object { $_.diff_type -eq 'reversed' -and $_.coarse_significant_p05 -eq 'yes' }).Count
"Reversed AND significant: $reversedSig"
$magChangeSig = ($results | Where-Object { $_.diff_type -eq 'magnitude_change' -and $_.coarse_significant_p05 -eq 'yes' }).Count
"Magnitude-change AND significant: $magChangeSig"

$results | Export-Csv "$repo\results\ssdse_japan_full_pairwise.csv" -NoTypeInformation -Encoding UTF8
"Saved to results/ssdse_japan_full_pairwise.csv"
