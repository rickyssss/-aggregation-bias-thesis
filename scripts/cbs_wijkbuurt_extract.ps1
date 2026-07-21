# Netherlands CBS "Kerncijfers wijken en buurten" 2024 (table 83765NED): gemeente
# (municipality, coarse) vs wijk (district, fine). Raw counts -> per-1000-population
# rates using AantalInwoners_5 as denominator; already-normalized fields kept as-is.

$ErrorActionPreference = "Stop"
$repo = "C:\Users\saika\-aggregation-bias-thesis"

$all = Get-Content "$repo\scratch\cbs\page1.json" -Raw | ConvertFrom-Json
$gemeente = $all | Where-Object { $_.SoortRegio_2.Trim() -eq "Gemeente" }
$wijk = $all | Where-Object { $_.SoortRegio_2.Trim() -eq "Wijk" }
"Gemeente: $($gemeente.Count), Wijk: $($wijk.Count)"

# raw count fields -> convert to per-1000-population rate (denominator: AantalInwoners_5)
$countVars = @(
    "Mannen_6","Vrouwen_7","k_0Tot15Jaar_8","k_15Tot25Jaar_9","k_25Tot45Jaar_10","k_45Tot65Jaar_11","k_65JaarOfOuder_12",
    "Ongehuwd_13","Gehuwd_14","Gescheiden_15","Verweduwd_16","WestersTotaal_17","NietWestersTotaal_18",
    "GeboorteTotaal_24","SterfteTotaal_26","HuishoudensTotaal_28","Eenpersoonshuishoudens_29",
    "HuishoudensZonderKinderen_30","HuishoudensMetKinderen_31","Woningvoorraad_34"
)
# already-normalized fields (percentages, averages, medians) -> keep as-is
$rateVars = @(
    "GeboorteRelatief_25","SterfteRelatief_27","GemiddeldeHuishoudensgrootte_32","Bevolkingsdichtheid_33",
    "GemiddeldeWOZWaardeVanWoningen_35","PercentageEengezinswoning_36","PercentageMeergezinswoning_37",
    "PercentageBewoond_38","PercentageOnbewoond_39","Koopwoningen_40","HuurwoningenTotaal_41",
    "BouwjaarVoor2000_45","BouwjaarVanaf2000_46","GemiddeldElektriciteitsverbruikTotaal_47",
    "GemiddeldAardgasverbruikTotaal_55","AantalInkomensontvangers_64","GemiddeldInkomenPerInkomensontvanger_65",
    "GemiddeldInkomenPerInwoner_66","k_40PersonenMetLaagsteInkomen_67","k_20PersonenMetHoogsteInkomen_68",
    "Actieven1575Jaar_69","HuishoudensMetEenLaagInkomen_72","PersonenautoSPerHuishouden_91",
    "AfstandTotHuisartsenpraktijk_94","AfstandTotGroteSupermarkt_95","AfstandTotSchool_97"
)

function BuildTable($rows) {
    $out = New-Object System.Collections.Generic.List[object]
    foreach ($r in $rows) {
        $pop = 0.0
        if (-not [double]::TryParse("$($r.AantalInwoners_5)", [ref]$pop) -or $pop -le 0) { continue }
        $o = [ordered]@{ geo = $r.Codering_3 }
        foreach ($v in $rateVars) {
            $n = 0.0
            $raw = $r.$v
            $o[$v] = if ($null -ne $raw -and [double]::TryParse("$raw", [ref]$n)) { $n } else { [double]::NaN }
        }
        foreach ($v in $countVars) {
            $n = 0.0
            $raw = $r.$v
            $o[$v] = if ($null -ne $raw -and [double]::TryParse("$raw", [ref]$n)) { 1000.0 * $n / $pop } else { [double]::NaN }
        }
        $out.Add([PSCustomObject]$o)
    }
    return $out
}

$coarseTable = BuildTable $gemeente
$fineTable = BuildTable $wijk
"Coarse (gemeente) usable: $($coarseTable.Count), Fine (wijk) usable: $($fineTable.Count)"

New-Item -ItemType Directory -Force -Path "$repo\data\Netherlands" | Out-Null
$coarseTable | Export-Csv "$repo\data\Netherlands\wijkbuurt_coarse_gemeente.csv" -NoTypeInformation -Encoding UTF8
$fineTable | Export-Csv "$repo\data\Netherlands\wijkbuurt_fine_wijk.csv" -NoTypeInformation -Encoding UTF8

$vars = $rateVars + $countVars

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
        $obj | Add-Member -MemberType NoteProperty -Name country -Value "Netherlands"
        $obj | Add-Member -MemberType NoteProperty -Name variable -Value ($c1 + " vs " + $c2)
        $obj | Add-Member -MemberType NoteProperty -Name coarse_level -Value ("gemeente(n=" + $nCoarse + ")")
        $obj | Add-Member -MemberType NoteProperty -Name coarse_stat -Value ("corr=" + [Math]::Round($rCoarse,3))
        $obj | Add-Member -MemberType NoteProperty -Name fine_level -Value ("wijk(n=" + $nFine + ")")
        $obj | Add-Member -MemberType NoteProperty -Name fine_stat -Value ("corr=" + [Math]::Round($rFine,3))
        $obj | Add-Member -MemberType NoteProperty -Name diff_type -Value $diffType
        $obj | Add-Member -MemberType NoteProperty -Name notes -Value "CBS Kerncijfers wijken en buurten 2024(table 83765NED), OData API, no registration required. gemeente=municipality, wijk=district (finer than gemeente, coarser than buurt/neighbourhood). Counts converted to per-1000-population rate; percentages/medians/averages kept as published."
        $obj | Add-Member -MemberType NoteProperty -Name coarse_significant_p05 -Value (Test-Sig $rCoarse $nCoarse)
        $obj | Add-Member -MemberType NoteProperty -Name fine_significant_p05 -Value (Test-Sig $rFine $nFine)
        $results.Add($obj)
    }
}
"Pairs: $($results.Count)"
$results | Export-Csv "$repo\results\cbs_wijkbuurt_pairwise.csv" -NoTypeInformation -Encoding UTF8
"Saved."
