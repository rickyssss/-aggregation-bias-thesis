# BLS QCEW 2024 annual, industry_code=10 (total all industries), own_code=0 (all ownerships).
# State (coarse) vs county (fine), same variable set at each level.

$ErrorActionPreference = "Stop"
$repo = "C:\Users\saika\-aggregation-bias-thesis"

$raw = Import-Csv "$repo\scratch\bls\qcew_2024_industry10.csv"
$stateRaw = $raw | Where-Object { $_.agglvl_code -eq "50" -and $_.own_code -eq "0" }
$countyRaw = $raw | Where-Object { $_.agglvl_code -eq "70" -and $_.own_code -eq "0" }
"Coarse (state) rows: $($stateRaw.Count), Fine (county) rows: $($countyRaw.Count)"

function BuildTable($rows) {
    $out = New-Object System.Collections.Generic.List[object]
    foreach ($r in $rows) {
        $estabs = 0.0; $emplvl = 0.0
        [double]::TryParse($r.annual_avg_estabs, [ref]$estabs) | Out-Null
        [double]::TryParse($r.annual_avg_emplvl, [ref]$emplvl) | Out-Null
        $o = [ordered]@{
            area = $r.area_fips
            annual_avg_wkly_wage = $r.annual_avg_wkly_wage
            avg_annual_pay = $r.avg_annual_pay
            oty_annual_avg_estabs_pct_chg = $r.oty_annual_avg_estabs_pct_chg
            oty_annual_avg_emplvl_pct_chg = $r.oty_annual_avg_emplvl_pct_chg
            oty_total_annual_wages_pct_chg = $r.oty_total_annual_wages_pct_chg
            oty_taxable_annual_wages_pct_chg = $r.oty_taxable_annual_wages_pct_chg
            oty_annual_contributions_pct_chg = $r.oty_annual_contributions_pct_chg
            oty_annual_avg_wkly_wage_pct_chg = $r.oty_annual_avg_wkly_wage_pct_chg
            oty_avg_annual_pay_pct_chg = $r.oty_avg_annual_pay_pct_chg
            estabs_per_1000_emp = if ($emplvl -gt 0) { 1000.0 * $estabs / $emplvl } else { $null }
        }
        $out.Add([PSCustomObject]$o)
    }
    return $out
}

$coarseTable = BuildTable $stateRaw
$fineTable = BuildTable $countyRaw
New-Item -ItemType Directory -Force -Path "$repo\data\US" | Out-Null
$coarseTable | Export-Csv "$repo\data\US\qcew_coarse_state.csv" -NoTypeInformation -Encoding UTF8
$fineTable | Export-Csv "$repo\data\US\qcew_fine_county.csv" -NoTypeInformation -Encoding UTF8

$vars = @("annual_avg_wkly_wage","avg_annual_pay","oty_annual_avg_estabs_pct_chg","oty_annual_avg_emplvl_pct_chg","oty_total_annual_wages_pct_chg","oty_taxable_annual_wages_pct_chg","oty_annual_contributions_pct_chg","oty_annual_avg_wkly_wage_pct_chg","oty_avg_annual_pay_pct_chg","estabs_per_1000_emp")

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
foreach ($v in $vars) { $coarseVals[$v] = $coarseTable | ForEach-Object { $n=0.0; if($null -ne $_.$v -and [double]::TryParse($_.$v,[ref]$n)){$n}else{[double]::NaN} } }
$fineVals = @{}
foreach ($v in $vars) { $fineVals[$v] = $fineTable | ForEach-Object { $n=0.0; if($null -ne $_.$v -and [double]::TryParse($_.$v,[ref]$n)){$n}else{[double]::NaN} } }

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
        $obj | Add-Member -MemberType NoteProperty -Name notes -Value "BLS QCEW 2024 annual, industry_code=10(total all industries), own_code=0(all ownerships). Wage/pay levels and year-over-year pct-change fields used as-is(already rates); estabs_per_1000_emp is a derived ratio. No registration required."
        $obj | Add-Member -MemberType NoteProperty -Name coarse_significant_p05 -Value (Test-Sig $rCoarse $nCoarse)
        $obj | Add-Member -MemberType NoteProperty -Name fine_significant_p05 -Value (Test-Sig $rFine $nFine)
        $results.Add($obj)
    }
}
"Pairs: $($results.Count)"
$results | Export-Csv "$repo\results\bls_qcew_pairwise.csv" -NoTypeInformation -Encoding UTF8
"Saved."
