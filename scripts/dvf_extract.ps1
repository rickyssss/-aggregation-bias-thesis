# France DVF (Demandes de valeurs foncieres) 2024: commune (fine) vs departement (coarse).
# Streams the 607MB national file, dedupes multi-lot sales by id_mutation, keeps
# Vente transactions of type Maison/Appartement with valid price+surface, derives
# per-area median price/sqm, median price, median surface, median rooms, apartment share.

$ErrorActionPreference = "Stop"
$repo = "C:\Users\saika\-aggregation-bias-thesis"
$srcFile = "$repo\scratch\dvf\full2024.csv"

$reader = New-Object System.IO.StreamReader($srcFile)
$header = $reader.ReadLine() -split ","
$idx = @{}
for ($i = 0; $i -lt $header.Count; $i++) { $idx[$header[$i]] = $i }

function ParseNum($s) {
    if ([string]::IsNullOrWhiteSpace($s)) { return [double]::NaN }
    $n = 0.0
    if ([double]::TryParse($s, [System.Globalization.NumberStyles]::Any, [System.Globalization.CultureInfo]::InvariantCulture, [ref]$n)) { return $n }
    return [double]::NaN
}

$seenMutations = New-Object System.Collections.Generic.HashSet[string]

$communeData = @{}   # commune code -> hashtable of lists
$deptData = @{}       # dept code -> hashtable of lists

function GetBucket($table, $key) {
    if (-not $table.ContainsKey($key)) {
        $table[$key] = @{
            price_per_sqm = New-Object System.Collections.Generic.List[double]
            valeur = New-Object System.Collections.Generic.List[double]
            surface = New-Object System.Collections.Generic.List[double]
            pieces = New-Object System.Collections.Generic.List[double]
            appt = 0
            maison = 0
        }
    }
    return $table[$key]
}

$lineCount = 0
$keptCount = 0
while (-not $reader.EndOfStream) {
    $line = $reader.ReadLine()
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    $f = $line -split ","
    $lineCount++

    $idMut = $f[$idx["id_mutation"]]
    if ($seenMutations.Contains($idMut)) { continue }
    $seenMutations.Add($idMut) | Out-Null

    if ($f[$idx["nature_mutation"]] -ne "Vente") { continue }
    $typeLocal = $f[$idx["type_local"]]
    if ($typeLocal -ne "Maison" -and $typeLocal -ne "Appartement") { continue }

    $valeur = ParseNum $f[$idx["valeur_fonciere"]]
    $surface = ParseNum $f[$idx["surface_reelle_bati"]]
    if ([double]::IsNaN($valeur) -or $valeur -le 0 -or [double]::IsNaN($surface) -or $surface -le 0) { continue }

    $pieces = ParseNum $f[$idx["nombre_pieces_principales"]]
    $commune = $f[$idx["code_commune"]]
    $dept = $f[$idx["code_departement"]]
    $pricePerSqm = $valeur / $surface

    foreach ($bucket in @((GetBucket $communeData $commune), (GetBucket $deptData $dept))) {
        $bucket.price_per_sqm.Add($pricePerSqm)
        $bucket.valeur.Add($valeur)
        $bucket.surface.Add($surface)
        if (-not [double]::IsNaN($pieces) -and $pieces -gt 0) { $bucket.pieces.Add($pieces) }
        if ($typeLocal -eq "Appartement") { $bucket.appt++ } else { $bucket.maison++ }
    }
    $keptCount++
}
$reader.Close()
"Lines read: $lineCount, kept sales: $keptCount, communes: $($communeData.Count), departements: $($deptData.Count)"

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
        $n = $b.valeur.Count
        if ($n -lt $minN) { continue }
        $totalType = $b.appt + $b.maison
        $out.Add([PSCustomObject]@{
            geo = $key
            n_transactions = $n
            median_price_per_sqm = Get-Median $b.price_per_sqm
            median_valeur_fonciere = Get-Median $b.valeur
            median_surface_bati = Get-Median $b.surface
            median_pieces = Get-Median $b.pieces
            appartement_share_pct = if ($totalType -gt 0) { 100.0 * $b.appt / $totalType } else { [double]::NaN }
        })
    }
    return $out
}

$fineTable = BuildTable $communeData 3
$coarseTable = BuildTable $deptData 3
"Fine (commune) usable rows: $($fineTable.Count), Coarse (departement) usable rows: $($coarseTable.Count)"

New-Item -ItemType Directory -Force -Path "$repo\data\France" | Out-Null
$fineTable | Export-Csv "$repo\data\France\dvf_fine_commune.csv" -NoTypeInformation -Encoding UTF8
$coarseTable | Export-Csv "$repo\data\France\dvf_coarse_departement.csv" -NoTypeInformation -Encoding UTF8

$vars = @("median_price_per_sqm","median_valeur_fonciere","median_surface_bati","median_pieces","appartement_share_pct")

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
        $obj | Add-Member -MemberType NoteProperty -Name country -Value "France"
        $obj | Add-Member -MemberType NoteProperty -Name variable -Value ($c1 + " vs " + $c2)
        $obj | Add-Member -MemberType NoteProperty -Name coarse_level -Value ("departement(n=" + $nCoarse + ")")
        $obj | Add-Member -MemberType NoteProperty -Name coarse_stat -Value ("corr=" + [Math]::Round($rCoarse,3))
        $obj | Add-Member -MemberType NoteProperty -Name fine_level -Value ("commune(n=" + $nFine + ")")
        $obj | Add-Member -MemberType NoteProperty -Name fine_stat -Value ("corr=" + [Math]::Round($rFine,3))
        $obj | Add-Member -MemberType NoteProperty -Name diff_type -Value $diffType
        $obj | Add-Member -MemberType NoteProperty -Name notes -Value "France DVF(demandes de valeurs foncieres) 2024, Vente only, Maison/Appartement only, deduped by id_mutation. Median per area(min 3 transactions). No registration required. Direct department-level aggregation of raw transactions(not population-weighted)."
        $obj | Add-Member -MemberType NoteProperty -Name coarse_significant_p05 -Value (Test-Sig $rCoarse $nCoarse)
        $obj | Add-Member -MemberType NoteProperty -Name fine_significant_p05 -Value (Test-Sig $rFine $nFine)
        $results.Add($obj)
    }
}
"Pairs: $($results.Count)"
$results | Export-Csv "$repo\results\dvf_pairwise.csv" -NoTypeInformation -Encoding UTF8
"Saved."
