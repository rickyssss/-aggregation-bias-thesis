# Benjamini-Hochberg correction for all correlation tests in results/summary_table.csv.
# Reconstructs two-tailed p-values from corr=... and n=... fields.

$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
$summaryPath = Join-Path $repo "results\summary_table.csv"
$detailPath = Join-Path $repo "results\multiple_testing_correction.csv"
$reportPath = Join-Path $repo "results\multiple_testing_correction.md"

function Get-LogGamma([double]$z) {
    $coef = @(
        0.99999999999980993,
        676.5203681218851,
        -1259.1392167224028,
        771.32342877765313,
        -176.61502916214059,
        12.507343278686905,
        -0.13857109526572012,
        9.9843695780195716e-6,
        1.5056327351493116e-7
    )
    if ($z -lt 0.5) {
        return [Math]::Log([Math]::PI) - [Math]::Log([Math]::Sin([Math]::PI * $z)) - (Get-LogGamma (1.0 - $z))
    }

    $z -= 1.0
    $x = $coef[0]
    for ($i = 1; $i -lt $coef.Count; $i++) {
        $x += $coef[$i] / ($z + $i)
    }
    $t = $z + 7.5
    return 0.9189385332046727 + ($z + 0.5) * [Math]::Log($t) - $t + [Math]::Log($x)
}

function Get-BetaContinuedFraction([double]$a, [double]$b, [double]$x) {
    $maxIterations = 200
    $eps = 3.0e-14
    $fpmin = 1.0e-300

    $qab = $a + $b
    $qap = $a + 1.0
    $qam = $a - 1.0
    $c = 1.0
    $d = 1.0 - $qab * $x / $qap
    if ([Math]::Abs($d) -lt $fpmin) { $d = $fpmin }
    $d = 1.0 / $d
    $h = $d

    for ($m = 1; $m -le $maxIterations; $m++) {
        $m2 = 2 * $m
        $aa = $m * ($b - $m) * $x / (($qam + $m2) * ($a + $m2))
        $d = 1.0 + $aa * $d
        if ([Math]::Abs($d) -lt $fpmin) { $d = $fpmin }
        $c = 1.0 + $aa / $c
        if ([Math]::Abs($c) -lt $fpmin) { $c = $fpmin }
        $d = 1.0 / $d
        $h *= $d * $c

        $aa = -($a + $m) * ($qab + $m) * $x / (($a + $m2) * ($qap + $m2))
        $d = 1.0 + $aa * $d
        if ([Math]::Abs($d) -lt $fpmin) { $d = $fpmin }
        $c = 1.0 + $aa / $c
        if ([Math]::Abs($c) -lt $fpmin) { $c = $fpmin }
        $d = 1.0 / $d
        $del = $d * $c
        $h *= $del
        if ([Math]::Abs($del - 1.0) -le $eps) { break }
    }
    return $h
}

function Get-RegularizedBeta([double]$x, [double]$a, [double]$b) {
    if ($x -le 0.0) { return 0.0 }
    if ($x -ge 1.0) { return 1.0 }

    $logBt = (Get-LogGamma ($a + $b)) - (Get-LogGamma $a) - (Get-LogGamma $b) +
        $a * [Math]::Log($x) + $b * [Math]::Log(1.0 - $x)
    $bt = [Math]::Exp($logBt)

    if ($x -lt (($a + 1.0) / ($a + $b + 2.0))) {
        return $bt * (Get-BetaContinuedFraction $a $b $x) / $a
    }
    return 1.0 - ($bt * (Get-BetaContinuedFraction $b $a (1.0 - $x)) / $b)
}

function Get-TwoTailedP([double]$r, [int]$n) {
    if ($n -lt 4) { return $null }
    $absR = [Math]::Abs($r)
    if ($absR -ge 0.999999999999) { return 0.0 }
    $df = $n - 2
    $t = $absR * [Math]::Sqrt($df / (1.0 - $absR * $absR))
    $x = $df / ($df + $t * $t)
    return Get-RegularizedBeta $x ($df / 2.0) 0.5
}

function Get-CorrTest($row, [int]$rowNumber, [string]$levelName) {
    $levelField = if ($levelName -eq "coarse") { $row.coarse_level } else { $row.fine_level }
    $statField = if ($levelName -eq "coarse") { $row.coarse_stat } else { $row.fine_stat }
    $flagField = if ($levelName -eq "coarse") { $row.coarse_significant_p05 } else { $row.fine_significant_p05 }

    if ($statField -notmatch 'corr=(-?[\d.]+)') { return $null }
    $r = [double]$Matches[1]
    if ($levelField -notmatch 'n=(\d+)') { return $null }
    $n = [int]$Matches[1]
    $p = Get-TwoTailedP $r $n
    if ($null -eq $p) { return $null }

    return [PSCustomObject]@{
        row_number = $rowNumber
        id = $row.id
        country = $row.country
        variable = $row.variable
        diff_type = $row.diff_type
        level = $levelName
        level_label = $levelField
        stat = $statField
        r = $r
        n = $n
        p_value = $p
        p05_flag = $flagField
        bh_q_value = $null
        bh_significant_p05 = $null
    }
}

$rows = Import-Csv -Path $summaryPath
$tests = New-Object System.Collections.Generic.List[object]

for ($i = 0; $i -lt $rows.Count; $i++) {
    $rowNumber = $i + 1
    $coarseTest = Get-CorrTest $rows[$i] $rowNumber "coarse"
    $fineTest = Get-CorrTest $rows[$i] $rowNumber "fine"
    if ($null -ne $coarseTest) { $tests.Add($coarseTest) }
    if ($null -ne $fineTest) { $tests.Add($fineTest) }
}

$m = $tests.Count
$sorted = @($tests | Sort-Object p_value)
$prevQ = 1.0
for ($i = $m - 1; $i -ge 0; $i--) {
    $rank = $i + 1
    $q = [Math]::Min($prevQ, $sorted[$i].p_value * $m / $rank)
    if ($q -gt 1.0) { $q = 1.0 }
    $sorted[$i].bh_q_value = $q
    $sorted[$i].bh_significant_p05 = if ($q -le 0.05) { "yes" } else { "no" }
    $prevQ = $q
}

$tests |
    Sort-Object row_number, level |
    Select-Object row_number,id,country,variable,diff_type,level,level_label,stat,r,n,p_value,bh_q_value,p05_flag,bh_significant_p05 |
    Export-Csv -Path $detailPath -NoTypeInformation -Encoding UTF8

$uncorrectedSig = @($tests | Where-Object { $_.p_value -le 0.05 }).Count
$bhSig = @($tests | Where-Object { $_.bh_q_value -le 0.05 }).Count
$coarseTotal = @($tests | Where-Object { $_.level -eq "coarse" }).Count
$fineTotal = @($tests | Where-Object { $_.level -eq "fine" }).Count
$coarseBhSig = @($tests | Where-Object { $_.level -eq "coarse" -and $_.bh_q_value -le 0.05 }).Count
$fineBhSig = @($tests | Where-Object { $_.level -eq "fine" -and $_.bh_q_value -le 0.05 }).Count

$rowGroups = $tests | Group-Object row_number
$rowsAnyBh = @($rowGroups | Where-Object { @($_.Group | Where-Object { $_.bh_q_value -le 0.05 }).Count -gt 0 }).Count
$rowsBothBh = @($rowGroups | Where-Object {
    @($_.Group | Where-Object { $_.level -eq "coarse" -and $_.bh_q_value -le 0.05 }).Count -gt 0 -and
    @($_.Group | Where-Object { $_.level -eq "fine" -and $_.bh_q_value -le 0.05 }).Count -gt 0
}).Count
$reversedTestsBh = @($tests | Where-Object { $_.diff_type -eq "reversed" -and $_.bh_q_value -le 0.05 }).Count
$reversedRowsBothBh = @($rowGroups | Where-Object {
    $_.Group[0].diff_type -eq "reversed" -and
    @($_.Group | Where-Object { $_.level -eq "coarse" -and $_.bh_q_value -le 0.05 }).Count -gt 0 -and
    @($_.Group | Where-Object { $_.level -eq "fine" -and $_.bh_q_value -le 0.05 }).Count -gt 0
}).Count

$byDiff = $tests |
    Group-Object diff_type |
    Sort-Object Name |
    ForEach-Object {
        $sig = @($_.Group | Where-Object { $_.bh_q_value -le 0.05 }).Count
        "| $($_.Name) | $($_.Count) | $sig |"
    }

$top = $tests |
    Sort-Object bh_q_value |
    Select-Object -First 10 |
    ForEach-Object {
        $pText = "{0:E3}" -f $_.p_value
        $qText = "{0:E3}" -f $_.bh_q_value
        "| $($_.id) | $($_.country) | $($_.level) | $($_.variable) | $($_.stat) | $pText | $qText |"
    }

$report = @"
# 多重検定補正

`results/summary_table.csv` から抽出できる全ての相関検定に対して、Benjamini-Hochberg 法で false discovery rate を補正した。各行は最大2件の検定、すなわち粗い集計単位の相関と細かい集計単位の相関を持つ。CV比較など、`corr=` ではない行は除外した。

- 入力行数: $($rows.Count)
- 補正対象の相関検定数: $m
- 補正前 p <= 0.05: $uncorrectedSig
- BH補正後 q <= 0.05: $bhSig
- 粗い単位でBH補正後も有意: $coarseBhSig / $coarseTotal
- 細かい単位でBH補正後も有意: $fineBhSig / $fineTotal
- 少なくとも片側の相関がBH補正後も有意な行: $rowsAnyBh
- 粗い単位・細かい単位の両方がBH補正後も有意な行: $rowsBothBh
- 符号反転(reversed)の検定のうちBH補正後も有意: $reversedTestsBh
- 符号反転(reversed)行のうち粗細両方がBH補正後も有意: $reversedRowsBothBh

## diff_type別

| diff_type | 検定数 | BH q <= 0.05 |
|---|---:|---:|
$($byDiff -join "`n")

## q値が最小の例

| id | country | level | variable | stat | p | BH q |
|---|---|---|---|---:|---:|---:|
$($top -join "`n")

詳細は `results/multiple_testing_correction.csv` に保存した。
"@

Set-Content -Path $reportPath -Value $report -Encoding UTF8

Write-Output "Input rows: $($rows.Count)"
Write-Output "Correlation tests: $m"
Write-Output "Uncorrected p<=0.05: $uncorrectedSig"
Write-Output "BH q<=0.05: $bhSig"
Write-Output "Report: $reportPath"
